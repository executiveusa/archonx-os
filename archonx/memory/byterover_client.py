"""
ByteRover Client
================
Persistent memory client for multi-layer context storage.

Integration with ByteRover API for:
- Project memory (project-specific patterns)
- Team memory (shared team knowledge)
- Global patterns (cross-project reusable patterns)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger("archonx.memory.byterover")


class MemoryLayer(Enum):
    """Memory layer types for context storage."""
    PROJECT = "project_local"
    TEAM = "team_shared"
    GLOBAL = "global_patterns"


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    key: str
    value: dict[str, Any]
    layer: MemoryLayer
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    access_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "layer": self.layer.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "confidence": self.confidence,
            "access_count": self.access_count
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        """Create from dictionary."""
        return cls(
            key=data["key"],
            value=data["value"],
            layer=MemoryLayer(data["layer"]),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            tags=data.get("tags", []),
            confidence=data.get("confidence", 1.0),
            access_count=data.get("access_count", 0)
        )


@dataclass
class SearchResult:
    """Result from memory search."""
    entry: MemoryEntry
    score: float
    highlights: list[str] = field(default_factory=list)


class ByteRoverClient:
    """
    Client for ByteRover persistent memory system.
    
    Provides multi-layer memory storage with:
    - Vector-based semantic search
    - Git-like version control for memories
    - Context Composer for curated knowledge
    - Team memory sharing
    
    Usage:
        client = ByteRoverClient()
        await client.save("pattern:hero_coffee_shop", {...}, MemoryLayer.PROJECT)
        results = await client.search("coffee shop patterns")
    """

    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        local_cache_dir: Optional[Path] = None,
        retrieval_threshold: float = 0.75
    ):
        """
        Initialize ByteRover client.
        
        Args:
            api_endpoint: ByteRover API endpoint (default: from env or local mode)
            api_key: API key for authentication (default: from env)
            local_cache_dir: Directory for local memory cache
            retrieval_threshold: Minimum score for search results
        """
        self.api_endpoint = api_endpoint or os.getenv("BYTEROVER_ENDPOINT", "local")
        self.api_key = api_key or os.getenv("BYTEROVER_API_KEY")
        self.retrieval_threshold = retrieval_threshold
        
        # Local cache setup
        self.cache_dir = local_cache_dir or Path.home() / ".archonx" / "memory"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Layer directories
        for layer in MemoryLayer:
            (self.cache_dir / layer.value).mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for fast access
        self._cache: dict[str, MemoryEntry] = {}
        self._initialized = False
        
        logger.info(f"ByteRover client initialized (mode: {'remote' if self.api_key else 'local'})")

    async def initialize(self) -> None:
        """Initialize the client and load cached memories."""
        if self._initialized:
            return
            
        # Load all cached memories into memory
        for layer in MemoryLayer:
            layer_dir = self.cache_dir / layer.value
            for file_path in layer_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        entry = MemoryEntry.from_dict(data)
                        self._cache[entry.key] = entry
                except Exception as e:
                    logger.warning(f"Failed to load memory {file_path}: {e}")
        
        self._initialized = True
        logger.info(f"Loaded {len(self._cache)} cached memories")

    async def save(
        self,
        key: str,
        value: dict[str, Any],
        layer: MemoryLayer = MemoryLayer.PROJECT,
        tags: Optional[list[str]] = None,
        confidence: float = 1.0
    ) -> MemoryEntry:
        """
        Save a memory entry.
        
        Args:
            key: Unique key for the memory (e.g., "pattern:hero_coffee_shop")
            value: The memory content
            layer: Memory layer (PROJECT, TEAM, or GLOBAL)
            tags: Optional tags for categorization
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            The created MemoryEntry
        """
        if not self._initialized:
            await self.initialize()
        
        entry = MemoryEntry(
            key=key,
            value=value,
            layer=layer,
            tags=tags or [],
            confidence=confidence
        )
        
        # Save to cache
        self._cache[key] = entry
        
        # Persist to disk
        file_path = self.cache_dir / layer.value / f"{self._key_to_filename(key)}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry.to_dict(), f, indent=2)
        
        # If remote mode, sync with API
        if self.api_key and self.api_endpoint != "local":
            await self._sync_to_remote(entry)
        
        logger.debug(f"Saved memory: {key} (layer: {layer.value})")
        return entry

    async def get(self, key: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry by key.
        
        Args:
            key: The memory key
            
        Returns:
            MemoryEntry if found, None otherwise
        """
        if not self._initialized:
            await self.initialize()
        
        entry = self._cache.get(key)
        if entry:
            # Increment access count
            entry.access_count += 1
            return entry
        
        return None

    async def search(
        self,
        query: str,
        layer: Optional[MemoryLayer] = None,
        limit: int = 10,
        threshold: Optional[float] = None
    ) -> list[SearchResult]:
        """
        Search memories by query.
        
        Args:
            query: Search query
            layer: Optional layer filter
            limit: Maximum results to return
            threshold: Minimum score threshold (uses default if not provided)
            
        Returns:
            List of SearchResult objects
        """
        if not self._initialized:
            await self.initialize()
        
        threshold = threshold or self.retrieval_threshold
        results: list[SearchResult] = []
        
        # Simple keyword matching for local mode
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        for entry in self._cache.values():
            # Layer filter
            if layer and entry.layer != layer:
                continue
            
            # Calculate simple relevance score
            score = self._calculate_relevance(entry, query_terms, query_lower)
            
            if score >= threshold:
                results.append(SearchResult(
                    entry=entry,
                    score=score,
                    highlights=self._extract_highlights(entry, query_terms)
                ))
        
        # Sort by score and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    async def delete(self, key: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            key: The memory key to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not self._initialized:
            await self.initialize()
        
        entry = self._cache.pop(key, None)
        if not entry:
            return False
        
        # Remove from disk
        file_path = self.cache_dir / entry.layer.value / f"{self._key_to_filename(key)}.json"
        if file_path.exists():
            file_path.unlink()
        
        logger.debug(f"Deleted memory: {key}")
        return True

    async def list_keys(
        self,
        layer: Optional[MemoryLayer] = None,
        prefix: Optional[str] = None,
        tags: Optional[list[str]] = None
    ) -> list[str]:
        """
        List memory keys with optional filters.
        
        Args:
            layer: Optional layer filter
            prefix: Optional key prefix filter
            tags: Optional tags filter (AND logic)
            
        Returns:
            List of matching keys
        """
        if not self._initialized:
            await self.initialize()
        
        keys = []
        for key, entry in self._cache.items():
            # Layer filter
            if layer and entry.layer != layer:
                continue
            
            # Prefix filter
            if prefix and not key.startswith(prefix):
                continue
            
            # Tags filter
            if tags and not all(tag in entry.tags for tag in tags):
                continue
            
            keys.append(key)
        
        return keys

    async def get_stats(self) -> dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory stats
        """
        if not self._initialized:
            await self.initialize()
        
        stats = {
            "total_memories": len(self._cache),
            "by_layer": {},
            "total_access_count": 0,
            "avg_confidence": 0.0
        }
        
        for layer in MemoryLayer:
            stats["by_layer"][layer.value] = 0
        
        total_confidence = 0.0
        for entry in self._cache.values():
            stats["by_layer"][entry.layer.value] += 1
            stats["total_access_count"] += entry.access_count
            total_confidence += entry.confidence
        
        if self._cache:
            stats["avg_confidence"] = total_confidence / len(self._cache)
        
        return stats

    def _key_to_filename(self, key: str) -> str:
        """Convert key to safe filename."""
        return hashlib.md5(key.encode()).hexdigest()

    def _calculate_relevance(self, entry: MemoryEntry, query_terms: set[str], query_lower: str) -> float:
        """Calculate relevance score for an entry."""
        score = 0.0
        
        # Check key match
        key_lower = entry.key.lower()
        if query_lower in key_lower:
            score += 0.5
        
        # Check value content
        value_str = json.dumps(entry.value).lower()
        for term in query_terms:
            if term in value_str:
                score += 0.1
        
        # Check tags
        for tag in entry.tags:
            if tag.lower() in query_terms:
                score += 0.2
        
        # Boost by confidence and access count
        score *= entry.confidence
        score *= min(1.0 + (entry.access_count * 0.05), 2.0)
        
        return min(score, 1.0)

    def _extract_highlights(self, entry: MemoryEntry, query_terms: set[str]) -> list[str]:
        """Extract highlighted snippets from entry."""
        highlights = []
        value_str = json.dumps(entry.value, indent=2)
        
        for line in value_str.split("\n"):
            line_lower = line.lower()
            if any(term in line_lower for term in query_terms):
                highlights.append(line.strip())
        
        return highlights[:3]

    async def _sync_to_remote(self, entry: MemoryEntry) -> bool:
        """Sync entry to remote ByteRover API."""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/memories",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=entry.to_dict(),
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to sync to remote: {e}")
            return False


# Singleton instance
_client: Optional[ByteRoverClient] = None


def get_client() -> ByteRoverClient:
    """Get the singleton ByteRover client."""
    global _client
    if _client is None:
        _client = ByteRoverClient()
    return _client
