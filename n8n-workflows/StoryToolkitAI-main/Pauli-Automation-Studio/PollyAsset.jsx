/**
 * PollyAsset Component
 * Dynamic Polly character rendering with caching and error handling
 * Path: components/PollyAsset.jsx
 */

import React, { useState, useEffect } from 'react';
import Image from 'next/image';

// Scene pack data (can be imported from JSON file)
const SCENE_PACKS = {
  delivery: {
    dispatch: {
      scene: "Polly standing at a neon-lit food delivery dispatch desk with glowing order tickets surrounding him",
      position: "centered in the frame",
      mood: "looking confident and sly"
    },
    receipt: {
      scene: "Polly holding a glowing pizza box with a mysterious delivery slip",
      position: "in the foreground on the left",
      mood: "examining the order with expertise"
    },
    night_run: {
      scene: "Polly delivering food through a rainy night city street",
      position: "dominating the entire scene",
      mood: "focused and determined"
    },
    customer_meeting: {
      scene: "Polly at a customer's door presenting a delivery with a sly grin",
      position: "centered in the frame",
      mood: "confident and sly"
    },
    success: {
      scene: "Polly celebrating a completed delivery route with arms raised triumphantly",
      position: "dominating the entire scene",
      mood: "triumphant, raising his arms"
    }
  },
  pauli_effect: {
    presentation: {
      scene: "Polly presenting the Pauli Effect delivery system to an audience",
      position: "centered in the frame",
      mood: "confident and sly"
    },
    referral: {
      scene: "Polly holding a golden coin (Pauli coin) with dollar signs floating around him",
      position: "in the foreground on the left",
      mood: "scheming, with a knowing smirk"
    },
    wally_vs: {
      scene: "Polly standing victoriously over a pile of bloated WordPress plugin boxes",
      position: "dominating the entire scene",
      mood: "triumphant, raising his arms"
    }
  },
  lifestyle: {
    alley: {
      scene: "Polly scheming in a shadowy urban alley with neon signs reflecting off wet pavement",
      position: "centered in the frame",
      mood: "scheming, with a knowing smirk"
    },
    cool: {
      scene: "Polly leaning casually against a brick wall in a dimly lit street corner",
      position: "in the foreground on the left",
      mood: "casual and cool, leaning against a wall"
    },
    shocked: {
      scene: "Polly looking shocked and taken aback by an unexpected turn of events",
      position: "centered in the frame",
      mood: "appearing surprised but collecting himself"
    },
    thinking: {
      scene: "Polly sitting on a curb, stroking his beard thoughtfully, contemplating his next move",
      position: "in the foreground on the left",
      mood: "contemplative, stroking his beard"
    },
    playful: {
      scene: "Polly in a playful tussle or playful moment with another character or object",
      position: "centered in the frame",
      mood: "playful and mischievous"
    }
  },
  promotional: {
    hero: {
      scene: "Polly as a heroic figure standing on a rooftop overlooking a city skyline",
      position: "dominating the entire scene",
      mood: "confident and sly"
    },
    banner: {
      scene: "Polly peeking from behind a large promotional banner for a special offer",
      position: "peeking from behind an object",
      mood: "playful and mischievous"
    },
    action: {
      scene: "Polly in a dynamic action pose, leaping or gesturing energetically",
      position: "in dynamic action pose",
      mood: "intense and focused"
    },
    mystery: {
      scene: "Polly in shadows, partially obscured, with only his sunglasses glowing",
      position: "small but detailed in lower right corner",
      mood: "mysterious and intriguing"
    }
  }
};

// Master character lock template
const CHARACTER_LOCK = "Polly must match the reference character exactly in face, body, clothing, and attitude. Always: sheep species, fluffy wool, scruffy beard, round dark sunglasses, oversized bare hooves, long worn coat, confident posture. Never: change species, add shoes, remove sunglasses, soften character.";

const STYLE_LOCK = "Black-and-white gritty ink illustration, heavy linework, stippling, underground comic style, vintage graphic novel, high contrast, no color, no shading gradients, no realism, no 3D.";

// Helper function to create cache key
const getCacheKey = (sceneId, customizations = {}) => {
  const baseKey = sceneId;
  const customString = JSON.stringify(customizations);
  const hash = Math.abs(customString.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)).toString(16);
  return `polly_${baseKey}_${hash}`;
};

// Helper function to build full prompt
const buildPollyPrompt = (sceneData, customScene, customPosition, customMood) => {
  const scene = customScene || sceneData.scene;
  const position = customPosition || sceneData.position;
  const mood = customMood || sceneData.mood;

  return `${scene}, featuring Polly — a mischievous anthropomorphic sheep with fluffy wool, scruffy beard, messy woolly hair, oversized bare hooves, and round dark sunglasses, wearing a long slightly worn coat.

Character Lock: ${CHARACTER_LOCK}

Style: ${STYLE_LOCK}

Composition: Polly should be the main focus, clearly visible, ${position}, with confident mischievous body language.

Mood: ${mood}`;
};

/**
 * PollyAsset Component
 * 
 * Props:
 * - sceneId: string (e.g., "delivery_dispatch", "lifestyle_cool")
 * - pack: string (default: "delivery") - which pack to use
 * - customScene: string - override scene description
 * - customMood: string - override mood
 * - customPosition: string - override position
 * - width: number (default: 512)
 * - height: number (default: 512)
 * - cacheKey: string - manual cache key override
 * - onLoad: function - callback when image loads
 * - altText: string - alt text for image
 * - showPrompt: boolean - show the prompt in console/debug
 */
export default function PollyAsset({
  sceneId,
  pack = 'delivery',
  customScene,
  customMood,
  customPosition,
  width = 512,
  height = 512,
  cacheKey: customCacheKey,
  onLoad,
  altText = 'Polly the mischievous sheep',
  showPrompt = false,
  className = ''
}) {
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [prompt, setPrompt] = useState(null);

  useEffect(() => {
    const generatePolly = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get scene data from pack
        const packData = SCENE_PACKS[pack];
        if (!packData || !packData[sceneId]) {
          throw new Error(`Scene not found: ${pack}.${sceneId}`);
        }
        const sceneData = packData[sceneId];

        // Build full prompt
        const fullPrompt = buildPollyPrompt(sceneData, customScene, customPosition, customMood);
        setPrompt(fullPrompt);

        if (showPrompt) {
          console.log('🎨 Polly Generation Prompt:', fullPrompt);
        }

        // Generate cache key
        const cacheKey = customCacheKey || getCacheKey(`${pack}_${sceneId}`, {
          customScene,
          customMood,
          customPosition,
          width,
          height
        });

        // Call API to generate or retrieve Polly
        const response = await fetch('/api/polly/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: fullPrompt,
            width,
            height,
            cacheKey,
            steps: 30
          })
        });

        if (!response.ok) {
          throw new Error(`Generation failed: ${response.statusText}`);
        }

        const data = await response.json();
        setImageUrl(data.imageUrl);

        if (showPrompt) {
          console.log('🖼️ Polly Generated:', {
            url: data.imageUrl,
            cached: data.cached,
            generationTime: data.generationTime
          });
        }

        if (onLoad) {
          onLoad({ imageUrl: data.imageUrl, cached: data.cached });
        }
      } catch (err) {
        console.error('❌ Polly Generation Error:', err);
        setError(err.message);
        // Fallback to placeholder
        setImageUrl('/images/polly-placeholder.png');
      } finally {
        setLoading(false);
      }
    };

    generatePolly();
  }, [sceneId, pack, customScene, customMood, customPosition, width, height, customCacheKey, onLoad, showPrompt]);

  // Render loading state
  if (loading && !imageUrl) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ width, height }}>
        <div className="text-center">
          <div className="animate-spin text-3xl mb-2">🐾</div>
          <p className="text-sm text-gray-500">Polly is scheming...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (error && !imageUrl) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 border border-red-300 rounded ${className}`} style={{ width, height }}>
        <div className="text-center">
          <p className="text-red-600 text-sm font-semibold">⚠️ Generation Error</p>
          <p className="text-gray-600 text-xs mt-1">{error}</p>
        </div>
      </div>
    );
  }

  // Render image
  return (
    <div className={className}>
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={altText}
          width={width}
          height={height}
          className="w-full h-auto rounded"
          style={{ maxWidth: '100%', height: 'auto' }}
        />
      ) : (
        <div
          className="bg-gray-200 rounded flex items-center justify-center"
          style={{ width, height }}
        >
          <p className="text-gray-500">Image failed to load</p>
        </div>
      )}
      {showPrompt && prompt && (
        <details className="mt-4 text-xs bg-gray-100 p-2 rounded border border-gray-300">
          <summary className="cursor-pointer font-semibold text-gray-700">View Prompt</summary>
          <pre className="mt-2 text-gray-600 overflow-auto whitespace-pre-wrap">{prompt}</pre>
        </details>
      )}
    </div>
  );
}

/**
 * Export scene pack for reference
 */
export { SCENE_PACKS };

/**
 * Export prompt builder for advanced usage
 */
export { buildPollyPrompt };

/**
 * Quick preset components (optional convenience exports)
 */

export function PollyDeliveryDispatch(props) {
  return <PollyAsset pack="delivery" sceneId="dispatch" {...props} />;
}

export function PollyDeliverySuccess(props) {
  return <PollyAsset pack="delivery" sceneId="success" {...props} />;
}

export function PollyLifestyleCool(props) {
  return <PollyAsset pack="lifestyle" sceneId="cool" {...props} />;
}

export function PollyPromoHero(props) {
  return <PollyAsset pack="promotional" sceneId="hero" {...props} />;
}

export function PollyReferral(props) {
  return <PollyAsset pack="pauli_effect" sceneId="referral" {...props} />;
}
