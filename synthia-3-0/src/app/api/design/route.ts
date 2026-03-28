/**
 * SYNTHIA 3.0 — AI Design API route
 * POST /api/design
 * Body: { prompt: string, projectName: string }
 * Returns: { spec: DesignSpec, html: string }
 */

import { NextRequest, NextResponse } from 'next/server'
import { renderDesignToHTML, defaultDesignSpec, type DesignSpec } from '@/lib/design-engine'

// Build a structured DesignSpec from the AI response text.
function parseAIDesignResponse(raw: string, projectName: string): DesignSpec {
  try {
    // Attempt to extract JSON block from AI markdown response
    const jsonMatch = raw.match(/```(?:json)?\s*([\s\S]*?)```/)
    const jsonStr = jsonMatch ? jsonMatch[1].trim() : raw.trim()
    const parsed = JSON.parse(jsonStr)
    return { ...defaultDesignSpec(projectName), ...parsed, projectName }
  } catch {
    // Fallback: return default spec with project name populated
    return defaultDesignSpec(projectName)
  }
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  const body = await req.json().catch(() => null)
  if (!body || typeof body.prompt !== 'string') {
    return NextResponse.json({ error: 'prompt requerido' }, { status: 400 })
  }

  const { prompt, projectName = 'Mi Proyecto' } = body as {
    prompt: string
    projectName?: string
  }

  const apiKey = process.env.ANTHROPIC_API_KEY
  if (!apiKey) {
    return NextResponse.json({ error: 'ANTHROPIC_API_KEY no configurada' }, { status: 500 })
  }

  const systemPrompt = `Eres SYNTHIA™, una IA de diseño especializada en emprendedoras latinoamericanas.
Tu tarea: convertir la descripción de un proyecto en una especificación de diseño completa en JSON.

REGLAS:
- Responde SOLO con JSON válido dentro de \`\`\`json ... \`\`\`
- Usa español para textos de contenido
- Paleta: profesional, femenina pero no rosa-por-defecto; prioriza paletas ricas (violeta, índigo, verde oscuro, terracota)
- Tipografía: Plus Jakarta Sans siempre
- UDEC mínimo: 8.5/10
- Sin gradientes, sin glassmorphism, sin radio > 12px en tarjetas

ESQUEMA JSON:
{
  "projectName": "string",
  "description": "string (español, 1-2 oraciones)",
  "industry": "string",
  "audience": "string",
  "colors": { "primary":"#hex","secondary":"#hex","background":"#hex","surface":"#hex","text":"#hex","textSecondary":"#hex","border":"#hex" },
  "typography": { "fontFamily":"string", "heading":{"size":"px","weight":"string","lineHeight":"string"}, "body":{"size":"px","weight":"string","lineHeight":"string"}, "small":{"size":"px","weight":"string","lineHeight":"string"} },
  "components": [{ "type":"card|button|badge|hero|nav|footer", "label":"string", "content":"string" }],
  "layout": "landing|dashboard|portfolio|ecommerce",
  "udecScore": 8.5,
  "reasoning": "string (explica decisiones de diseño en español)"
}`

  try {
    const aiRes = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 2048,
        system: systemPrompt,
        messages: [{ role: 'user', content: `Proyecto: "${projectName}"\nDescripción: ${prompt}` }],
      }),
    })

    if (!aiRes.ok) {
      const errText = await aiRes.text()
      console.error('[SYNTHIA API] Anthropic error:', errText)
      const fallback = defaultDesignSpec(projectName)
      return NextResponse.json({ spec: fallback, html: renderDesignToHTML(fallback) })
    }

    const aiData = await aiRes.json()
    const rawText: string = aiData.content?.[0]?.text ?? ''
    const spec = parseAIDesignResponse(rawText, projectName)
    const html = renderDesignToHTML(spec)

    return NextResponse.json({ spec, html })
  } catch (err) {
    console.error('[SYNTHIA API] Unexpected error:', err)
    const fallback = defaultDesignSpec(projectName)
    return NextResponse.json({ spec: fallback, html: renderDesignToHTML(fallback) })
  }
}
