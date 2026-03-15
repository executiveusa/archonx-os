"""
Anti-Scraping Protection
Rate limiting, bot detection, CAPTCHA integration
"""

from __future__ import annotations
import logging
from datetime import datetime, timedelta
from typing import Any
import hashlib

logger = logging.getLogger("archonx.security.anti_scraping")

class AntiScrapingEngine:
    """
    Multi-layer protection against scraping and bot abuse.
    
    Layers:
    1. Rate limiting (requests per IP per time window)
    2. Bot detection (user-agent analysis, behavior patterns)
    3. CAPTCHA challenges for suspicious traffic
    4. IP reputation scoring
    """
    
    def __init__(self) -> None:
        self._rate_limits: dict[str, list[datetime]] = {}
        self._ip_reputation: dict[str, float] = {}
        self._blocked_ips: set[str] = set()
        logger.info("Anti-scraping engine initialized")
    
    def check_rate_limit(self, ip: str, limit: int = 100, window_minutes: int = 60) -> bool:
        """
        Check if IP is within rate limits.
        
        Args:
            ip: Client IP address
            limit: Max requests allowed
            window_minutes: Time window in minutes
        
        Returns:
            True if within limits, False if exceeded
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=window_minutes)
        
        # Initialize or clean old requests
        if ip not in self._rate_limits:
            self._rate_limits[ip] = []
        self._rate_limits[ip] = [ts for ts in self._rate_limits[ip] if ts > cutoff]
        
        # Check limit
        if len(self._rate_limits[ip]) >= limit:
            logger.warning("Rate limit exceeded for IP: %s", ip)
            self._decrease_reputation(ip, 0.1)
            return False
        
        # Record request
        self._rate_limits[ip].append(now)
        return True
    
    def is_bot(self, user_agent: str, headers: dict[str, str]) -> bool:
        """
        Detect bot traffic based on user-agent and headers.
        """
        bot_patterns = [
            "bot", "crawler", "spider", "scraper", "wget", "curl",
            "python-requests", "scrapy", "selenium"
        ]
        
        ua_lower = user_agent.lower()
        if any(pattern in ua_lower for pattern in bot_patterns):
            # Allow good bots (GPTBot, ClaudeBot, Google, etc.)
            good_bots = ["gptbot", "claudebot", "googlebot", "bingbot"]
            if any(bot in ua_lower for bot in good_bots):
                return False
            return True
        
        # Check for missing standard headers
        if not headers.get("Accept-Language") or not headers.get("Accept-Encoding"):
            return True
        
        return False
    
    def get_reputation(self, ip: str) -> float:
        """Get IP reputation score (0.0 = bad, 1.0 = good)."""
        return self._ip_reputation.get(ip, 1.0)
    
    def _decrease_reputation(self, ip: str, amount: float) -> None:
        current = self._ip_reputation.get(ip, 1.0)
        new_score = max(0.0, current - amount)
        self._ip_reputation[ip] = new_score
        
        # Auto-block IPs with very low reputation
        if new_score < 0.2:
            self._blocked_ips.add(ip)
            logger.warning("IP auto-blocked due to low reputation: %s", ip)
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        return ip in self._blocked_ips
    
    def block_ip(self, ip: str) -> None:
        """Manually block an IP."""
        self._blocked_ips.add(ip)
        logger.info("IP manually blocked: %s", ip)
    
    def unblock_ip(self, ip: str) -> None:
        """Unblock an IP."""
        self._blocked_ips.discard(ip)
        self._ip_reputation[ip] = 1.0
        logger.info("IP unblocked: %s", ip)
