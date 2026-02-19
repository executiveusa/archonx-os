
import { GoogleGenAI, Type, Modality } from "@google/genai";

export class GeminiService {
  private ai: GoogleGenAI;

  constructor() {
    this.ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
  }

  // Refresh instance to ensure we use the latest injected API key from window.aistudio
  private refreshAI() {
    this.ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });
  }

  async generateScript(prompt: string) {
    this.refreshAI();
    const response = await this.ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: prompt,
      config: {
        thinkingConfig: { thinkingBudget: 32768 },
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            title: { type: Type.STRING },
            duration_seconds: { type: Type.INTEGER },
            hook: { type: Type.STRING },
            scenes: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  scene_id: { type: Type.INTEGER },
                  visual_description: { type: Type.STRING },
                  pauli_dialogue: { type: Type.STRING },
                  on_screen_text: { type: Type.STRING },
                  sound_fx: { type: Type.STRING },
                  b_roll_or_overlay: { type: Type.STRING },
                  cta_step: { type: Type.STRING },
                },
                required: ["scene_id", "visual_description", "pauli_dialogue"]
              }
            },
            cta: {
              type: Type.OBJECT,
              properties: {
                offer: { type: Type.STRING },
                next_step: { type: Type.STRING },
                link_text: { type: Type.STRING },
              }
            },
            keywords: { type: Type.ARRAY, items: { type: Type.STRING } },
            thumbnail_text: { type: Type.STRING },
          },
          required: ["title", "scenes", "cta"]
        }
      }
    });
    return JSON.parse(response.text || '{}');
  }

  async generateImage(prompt: string, aspectRatio: string = "16:9") {
    this.refreshAI();
    const response = await this.ai.models.generateContent({
      model: 'gemini-3-pro-image-preview',
      contents: { parts: [{ text: prompt }] },
      config: {
        imageConfig: {
          aspectRatio: aspectRatio as any,
          imageSize: "1K"
        }
      }
    });
    
    for (const part of response.candidates?.[0]?.content?.parts || []) {
      if (part.inlineData) {
        return `data:image/png;base64,${part.inlineData.data}`;
      }
    }
    return null;
  }

  async generateVideo(prompt: string, onProgress?: (msg: string) => void) {
    this.refreshAI();
    try {
      onProgress?.("Initiating Veo engine...");
      let operation = await this.ai.models.generateVideos({
        model: 'veo-3.1-fast-generate-preview',
        prompt,
        config: {
          numberOfVideos: 1,
          resolution: '1080p',
          aspectRatio: '16:9'
        }
      });

      onProgress?.("Rendering cinematic frames...");
      while (!operation.done) {
        await new Promise(resolve => setTimeout(resolve, 5000));
        operation = await this.ai.operations.getVideosOperation({ operation: operation });
        onProgress?.("Pauli is reviewing the cut...");
      }

      const downloadLink = operation.response?.generatedVideos?.[0]?.video?.uri;
      if (!downloadLink) throw new Error("Video generation failed");

      const response = await fetch(`${downloadLink}&key=${process.env.API_KEY}`);
      const blob = await response.blob();
      return URL.createObjectURL(blob);
    } catch (error: any) {
      if (error.message?.includes("Requested entity was not found")) {
        // This signifies the API key might be invalid or project missing
        throw new Error("API_KEY_ERROR");
      }
      throw error;
    }
  }

  async analyzeMedia(mediaData: string, mimeType: string, prompt: string) {
    this.refreshAI();
    const response = await this.ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: {
        parts: [
          { inlineData: { data: mediaData.split(',')[1], mimeType } },
          { text: prompt }
        ]
      }
    });
    return response.text;
  }

  async searchGrounding(query: string) {
    this.refreshAI();
    const response = await this.ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: query,
      config: {
        tools: [{ googleSearch: {} }]
      }
    });
    return {
      text: response.text,
      chunks: response.candidates?.[0]?.groundingMetadata?.groundingChunks || []
    };
  }

  async generateSpeech(text: string) {
    this.refreshAI();
    const response = await this.ai.models.generateContent({
      model: "gemini-2.5-flash-preview-tts",
      contents: [{ parts: [{ text: `Pauli: ${text}` }] }],
      config: {
        responseModalities: [Modality.AUDIO],
        speechConfig: {
          voiceConfig: {
            prebuiltVoiceConfig: { voiceName: 'Kore' }
          }
        }
      }
    });
    return response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
  }
}
