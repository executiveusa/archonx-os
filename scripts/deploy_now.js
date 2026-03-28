// Phase 3B: Vercel deploy runner
// node scripts/deploy_now.js
// Reads master.env, deploys chess-theater + synthia-3-0 to Vercel

const { execSync, spawnSync } = require('child_process')
const fs = require('fs')
const path = require('path')

const ROOT = path.join(__dirname, '..')
const ENV_FILE = path.join(ROOT, 'master.env')

// ── Load env vars ──────────────────────────────────────────────────────────
const lines = fs.readFileSync(ENV_FILE, 'utf8').replace(/\r/g, '').split('\n')
const env = {}
for (const line of lines) {
  const m = line.match(/^([A-Z_][A-Z0-9_]*)=(.*)$/)
  if (m) env[m[1]] = m[2].trim().replace(/^["']|["']$/g, '')
}

const TOKEN = env['VERCEL_TOKEN']
if (!TOKEN) { console.error('VERCEL_TOKEN not found'); process.exit(1) }
console.log(`[deploy] token loaded (${TOKEN.length} chars)`)

// ── Deploy helper ──────────────────────────────────────────────────────────
function deploy(name, dir) {
  console.log(`\n[deploy] ${name} → ${dir}`)
  const result = spawnSync(
    'vercel',
    ['deploy', '--prod', '--yes', '--no-clipboard', '--token', TOKEN],
    { cwd: dir, encoding: 'utf8', timeout: 180_000, shell: true, env: { ...process.env, VERCEL_TOKEN: TOKEN } }
  )
  if (result.status !== 0) {
    console.error(`[deploy] ${name} FAILED (exit ${result.status}):\n${result.stderr || result.stdout}`)
    return null
  }
  const url = (result.stdout || '').split('\n').filter(l => l.includes('https://')).pop()?.trim()
  console.log(`[deploy] ${name}: ${url || '(no URL in output)'}`)
  return url
}

const chessUrl  = deploy('chess-theater', path.join(ROOT, 'chess-theater'))
const synthiaUrl = deploy('synthia-3-0',   path.join(ROOT, 'synthia-3-0'))

console.log('\n╔═══════════════════════════════════════════════════╗')
console.log('║  PHASE 3B DEPLOYMENT REPORT                      ║')
console.log('╠═══════════════════════════════════════════════════╣')
console.log(`║  Chess Theater : ${(chessUrl || 'FAILED').padEnd(34)}║`)
console.log(`║  Synthia 3.0   : ${(synthiaUrl || 'FAILED').padEnd(34)}║`)
console.log('╚═══════════════════════════════════════════════════╝')
