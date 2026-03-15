"""
Story Toolkit Skill
===================
Generate consistent character assets and story-driven content.
Integrates the Polly Character System and StoryToolkitAI from n8n-workflows.

This skill provides:
- Polly character generation with scene packs
- Story-driven content creation
- Brand-consistent asset generation
- Delivery funnel visual assets
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.story_toolkit")


class ScenePack(str, Enum):
    """Available scene packs for character generation."""
    DELIVERY = "delivery"
    PAULI_EFFECT = "pauli_effect"
    LIFESTYLE = "lifestyle"
    PROMOTIONAL = "promotional"
    CUSTOM = "custom"


class CharacterType(str, Enum):
    """Available character types."""
    POLLY = "polly"
    PAULI = "pauli"
    WALLY = "wally"


@dataclass
class SceneDefinition:
    """Definition of a character scene."""
    scene_id: str
    pack: ScenePack
    description: str
    position: str
    mood: str
    default_width: int = 512
    default_height: int = 512


# Pre-defined scenes from StoryToolkitAI
SCENE_LIBRARY: dict[str, SceneDefinition] = {
    # Delivery Pack
    "delivery_dispatch": SceneDefinition(
        scene_id="delivery_dispatch",
        pack=ScenePack.DELIVERY,
        description="Polly standing at a food delivery dispatch desk",
        position="centered in the frame",
        mood="looking confident and ready for action",
    ),
    "delivery_receipt": SceneDefinition(
        scene_id="delivery_receipt",
        pack=ScenePack.DELIVERY,
        description="Polly holding a pizza box with pride",
        position="centered, showing the box prominently",
        mood="satisfied and professional",
    ),
    "delivery_night_run": SceneDefinition(
        scene_id="delivery_night_run",
        pack=ScenePack.DELIVERY,
        description="Polly delivering at night through city streets",
        position="dynamic action pose",
        mood="focused and determined",
    ),
    "delivery_customer_meeting": SceneDefinition(
        scene_id="delivery_customer_meeting",
        pack=ScenePack.DELIVERY,
        description="Polly at a customer's door",
        position="friendly stance at doorway",
        mood="welcoming and professional",
    ),
    "delivery_success": SceneDefinition(
        scene_id="delivery_success",
        pack=ScenePack.DELIVERY,
        description="Polly celebrating a successful delivery",
        position="triumphant pose",
        mood="joyful and accomplished",
    ),
    # Pauli Effect Pack
    "pauli_effect_presentation": SceneDefinition(
        scene_id="pauli_effect_presentation",
        pack=ScenePack.PAULI_EFFECT,
        description="Polly presenting the Pauli Effect funnel",
        position="gesturing toward presentation",
        mood="confident and persuasive",
    ),
    "pauli_effect_referral": SceneDefinition(
        scene_id="pauli_effect_referral",
        pack=ScenePack.PAULI_EFFECT,
        description="Polly holding a golden referral coin",
        position="showing coin prominently",
        mood="celebrating earnings",
    ),
    "pauli_effect_wally_vs": SceneDefinition(
        scene_id="pauli_effect_wally_vs",
        pack=ScenePack.PAULI_EFFECT,
        description="Polly defeating WordPress bloat monster",
        position="victorious stance",
        mood="triumphant and powerful",
    ),
    # Lifestyle Pack
    "lifestyle_alley": SceneDefinition(
        scene_id="lifestyle_alley",
        pack=ScenePack.LIFESTYLE,
        description="Polly scheming in a dark alley",
        position="leaning against brick wall",
        mood="mischievous and calculating",
    ),
    "lifestyle_cool": SceneDefinition(
        scene_id="lifestyle_cool",
        pack=ScenePack.LIFESTYLE,
        description="Polly leaning cool against a wall",
        position="relaxed confident pose",
        mood="cool and collected",
    ),
    "lifestyle_shocked": SceneDefinition(
        scene_id="lifestyle_shocked",
        pack=ScenePack.LIFESTYLE,
        description="Polly with a surprised expression",
        position="centered, expressive",
        mood="shocked and surprised",
    ),
    "lifestyle_thinking": SceneDefinition(
        scene_id="lifestyle_thinking",
        pack=ScenePack.LIFESTYLE,
        description="Polly contemplating deeply",
        position="thoughtful pose",
        mood="contemplative and wise",
    ),
    "lifestyle_playful": SceneDefinition(
        scene_id="lifestyle_playful",
        pack=ScenePack.LIFESTYLE,
        description="Polly being playful and fun",
        position="dynamic playful pose",
        mood="playful and energetic",
    ),
    # Promotional Pack
    "promo_hero": SceneDefinition(
        scene_id="promo_hero",
        pack=ScenePack.PROMOTIONAL,
        description="Polly heroic on a rooftop at sunset",
        position="heroic silhouette",
        mood="heroic and inspiring",
    ),
    "promo_banner": SceneDefinition(
        scene_id="promo_banner",
        pack=ScenePack.PROMOTIONAL,
        description="Polly peeking from behind a banner",
        position="peeking from side",
        mood="inviting and curious",
    ),
    "promo_action": SceneDefinition(
        scene_id="promo_action",
        pack=ScenePack.PROMOTIONAL,
        description="Polly in dynamic action scene",
        position="mid-action pose",
        mood="dynamic and exciting",
    ),
    "promo_mystery": SceneDefinition(
        scene_id="promo_mystery",
        pack=ScenePack.PROMOTIONAL,
        description="Polly mysterious in shadows",
        position="emerging from shadows",
        mood="mysterious and intriguing",
    ),
}

# Master prompt template for Polly character
POLLY_MASTER_PROMPT = """
# POLLY CHARACTER SYSTEM — MASTER PROMPT
A mischievous anthropomorphic sheep named Polly, drawn in a gritty black-and-white, hand-inked, stippled illustration style.

### Physical Characteristics
- Species: Anthropomorphic sheep
- Head: Round sheep face with fluffy wool, scruffy beard, messy woolly hair
- Eyes: Round dark sunglasses (always present)
- Feet: Oversized bare hooves (no shoes)
- Posture: Slightly hunched, confident, mischievous attitude
- Clothing: Long buttoned coat or jacket, slightly worn and oversized
- Expression: Confident, sly, slightly smug, streetwise

### Rendering Style Lock
- Black and white only
- Heavy ink lines, stippling texture, gritty halftone patterns
- High-contrast, hand-drawn appearance

### Template
[SCENE DESCRIPTION], featuring Polly — a mischievous anthropomorphic sheep with fluffy wool, scruffy beard, messy woolly hair, oversized bare hooves, and round dark sunglasses, wearing a long slightly worn coat.

Character Lock: Polly must match the reference character exactly in face, body, clothing, and attitude.
Style: Black-and-white gritty ink illustration, heavy linework, stippling, underground comic style, vintage graphic novel, high contrast, no color.
Composition: Polly should be the main focus, clearly visible, [POSITION INSTRUCTION].
Mood: [MOOD INSTRUCTION]
"""


class StoryToolkitSkill(BaseSkill):
    """Generate consistent character assets and story-driven content."""

    name = "story_toolkit"
    description = "Generate consistent character assets and story-driven content using StoryToolkitAI"
    category = SkillCategory.CREATIVE

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Generate character assets and story content.

        Params:
            action: 'generate_scene' | 'list_scenes' | 'generate_custom' | 'generate_story'
            scene_id: Pre-defined scene ID (e.g., 'delivery_dispatch')
            pack: Scene pack name ('delivery', 'pauli_effect', 'lifestyle', 'promotional')
            character: Character type ('polly', 'pauli', 'wally')
            custom_scene: Custom scene description (for generate_custom)
            custom_position: Custom position instruction
            custom_mood: Custom mood instruction
            width: Image width (default: 512)
            height: Image height (default: 512)
            use_cache: Whether to use cached results (default: True)
            cache_key: Custom cache key (optional)
            generate_prompt_only: Return prompt without generating (default: False)
        """
        action = context.params.get("action", "generate_scene")
        scene_id = context.params.get("scene_id", "")
        pack = context.params.get("pack", "")
        character = context.params.get("character", "polly")
        custom_scene = context.params.get("custom_scene", "")
        custom_position = context.params.get("custom_position", "centered in the frame")
        custom_mood = context.params.get("custom_mood", "looking confident and sly")
        width = context.params.get("width", 512)
        height = context.params.get("height", 512)
        use_cache = context.params.get("use_cache", True)
        cache_key = context.params.get("cache_key")
        generate_prompt_only = context.params.get("generate_prompt_only", False)

        try:
            if action == "generate_scene":
                result = await self._generate_scene(
                    scene_id, width, height, use_cache, cache_key, generate_prompt_only, context
                )
            elif action == "list_scenes":
                result = await self._list_scenes(pack)
            elif action == "generate_custom":
                result = await self._generate_custom(
                    custom_scene, custom_position, custom_mood,
                    width, height, character, generate_prompt_only, context
                )
            elif action == "generate_story":
                result = await self._generate_story(context)
            else:
                return SkillResult(
                    skill=self.name,
                    status="error",
                    error=f"Unknown action: {action}",
                    data={"action": action}
                )

            return SkillResult(
                skill=self.name,
                status="success",
                data=result,
                metadata={
                    "action": action,
                    "character": character,
                }
            )

        except Exception as e:
            logger.error("Story toolkit failed: %s", str(e))
            return SkillResult(
                skill=self.name,
                status="error",
                error=str(e),
                data={"action": action}
            )

    async def _generate_scene(
        self,
        scene_id: str,
        width: int,
        height: int,
        use_cache: bool,
        cache_key: str | None,
        generate_prompt_only: bool,
        context: SkillContext
    ) -> dict[str, Any]:
        """Generate a pre-defined scene."""
        if not scene_id:
            return {"error": "scene_id is required", "available_scenes": list(SCENE_LIBRARY.keys())}

        scene = SCENE_LIBRARY.get(scene_id)
        if not scene:
            return {
                "error": f"Scene '{scene_id}' not found",
                "available_scenes": list(SCENE_LIBRARY.keys())
            }

        # Build the prompt
        prompt = self._build_prompt(
            scene.description, scene.position, scene.mood
        )

        if generate_prompt_only:
            return {
                "scene_id": scene_id,
                "prompt": prompt,
                "pack": scene.pack.value,
            }

        # Generate or retrieve from cache
        cache_key = cache_key or self._generate_cache_key(scene_id, width, height)

        if use_cache:
            cached = await self._check_cache(cache_key, context)
            if cached:
                return {
                    "scene_id": scene_id,
                    "image_url": cached["url"],
                    "prompt": prompt,
                    "pack": scene.pack.value,
                    "cached": True,
                }

        # Generate new image
        image_result = await self._generate_image(prompt, width, height, context)

        return {
            "scene_id": scene_id,
            "image_url": image_result.get("url"),
            "prompt": prompt,
            "pack": scene.pack.value,
            "cached": False,
            "cache_key": cache_key,
        }

    async def _list_scenes(self, pack: str | None) -> dict[str, Any]:
        """List available scenes, optionally filtered by pack."""
        scenes = []

        for scene_id, scene in SCENE_LIBRARY.items():
            if pack and scene.pack.value != pack:
                continue

            scenes.append({
                "scene_id": scene_id,
                "pack": scene.pack.value,
                "description": scene.description,
                "default_size": f"{scene.default_width}x{scene.default_height}",
            })

        packs = {}
        for scene in scenes:
            pack_name = scene["pack"]
            if pack_name not in packs:
                packs[pack_name] = []
            packs[pack_name].append(scene["scene_id"])

        return {
            "total_scenes": len(scenes),
            "packs": packs,
            "scenes": scenes,
        }

    async def _generate_custom(
        self,
        custom_scene: str,
        custom_position: str,
        custom_mood: str,
        width: int,
        height: int,
        character: str,
        generate_prompt_only: bool,
        context: SkillContext
    ) -> dict[str, Any]:
        """Generate a custom scene."""
        if not custom_scene:
            return {"error": "custom_scene is required for custom generation"}

        # Build the prompt
        prompt = self._build_prompt(custom_scene, custom_position, custom_mood)

        if generate_prompt_only:
            return {
                "prompt": prompt,
                "character": character,
            }

        # Generate image
        image_result = await self._generate_image(prompt, width, height, context)

        return {
            "image_url": image_result.get("url"),
            "prompt": prompt,
            "character": character,
            "cached": False,
        }

    async def _generate_story(self, context: SkillContext) -> dict[str, Any]:
        """Generate a story-driven sequence of scenes."""
        story_type = context.params.get("story_type", "delivery_funnel")
        num_scenes = context.params.get("num_scenes", 5)
        width = context.params.get("width", 512)
        height = context.params.get("height", 512)

        # Pre-defined story sequences
        story_sequences = {
            "delivery_funnel": [
                "delivery_dispatch",
                "pauli_effect_presentation",
                "pauli_effect_wally_vs",
                "pauli_effect_referral",
                "delivery_success",
            ],
            "customer_journey": [
                "lifestyle_alley",
                "delivery_customer_meeting",
                "lifestyle_thinking",
                "delivery_success",
                "promo_hero",
            ],
            "brand_story": [
                "promo_mystery",
                "lifestyle_cool",
                "pauli_effect_presentation",
                "promo_action",
                "promo_hero",
            ],
        }

        scene_ids = story_sequences.get(story_type, list(SCENE_LIBRARY.keys())[:num_scenes])

        scenes = []
        for scene_id in scene_ids[:num_scenes]:
            scene_result = await self._generate_scene(
                scene_id, width, height, True, None, False, context
            )
            scenes.append(scene_result)

        return {
            "story_type": story_type,
            "total_scenes": len(scenes),
            "scenes": scenes,
        }

    def _build_prompt(
        self,
        scene: str,
        position: str,
        mood: str
    ) -> str:
        """Build the generation prompt from the master template."""
        prompt = POLLY_MASTER_PROMPT
        prompt = prompt.replace("[SCENE DESCRIPTION]", scene)
        prompt = prompt.replace("[POSITION INSTRUCTION]", position)
        prompt = prompt.replace("[MOOD INSTRUCTION]", mood)
        return prompt.strip()

    def _generate_cache_key(
        self,
        scene_id: str,
        width: int,
        height: int
    ) -> str:
        """Generate a cache key for the scene."""
        key_string = f"{scene_id}_{width}_{height}"
        return f"polly_{hashlib.md5(key_string.encode()).hexdigest()[:12]}"

    async def _check_cache(
        self,
        cache_key: str,
        context: SkillContext
    ) -> dict[str, Any] | None:
        """Check if the asset is cached."""
        # In production, check Redis/Vercel KV
        # For now, return None to always generate
        return None

    async def _generate_image(
        self,
        prompt: str,
        width: int,
        height: int,
        context: SkillContext
    ) -> dict[str, Any]:
        """Generate an image using available tools."""
        # Check for image generation tools
        if hasattr(context, "tools") and context.tools:
            # Try Hugging Face
            hf_tool = context.tools.get("huggingface") or context.tools.get("hf_inference")
            if hf_tool:
                try:
                    result = await hf_tool(
                        model="stabilityai/stable-diffusion-2-1",
                        inputs=prompt,
                        parameters={"width": width, "height": height}
                    )
                    return {"url": result.get("url", ""), "format": "png"}
                except Exception as e:
                    logger.warning("HF generation failed: %s", e)

            # Try Replicate
            replicate_tool = context.tools.get("replicate")
            if replicate_tool:
                try:
                    result = await replicate_tool(
                        model="stability-ai/sdxl",
                        input={"prompt": prompt, "width": width, "height": height}
                    )
                    return {"url": result.get("output", [""])[0], "format": "png"}
                except Exception as e:
                    logger.warning("Replicate generation failed: %s", e)

        # Mock response for testing
        return {
            "url": f"https://placeholder.com/polly/{width}x{height}?text=Generated+Asset",
            "format": "png",
            "mock": True,
            "message": "No image generation tool available. Install HuggingFace or Replicate MCP.",
        }
