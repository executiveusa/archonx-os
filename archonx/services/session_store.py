"""
Session Store Service

Persistent storage of agent sessions with JSON backend.
Can be upgraded to SQLite, PostgreSQL, or other backends.

ZTE-20260308-0005: Session persistence layer
"""

import json
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class SessionStore:
    """Persistent session storage"""

    def __init__(self, store_dir: str = "/tmp/archonx/sessions"):
        """Initialize session store"""
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Session store initialized at {self.store_dir}")

    async def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save session to disk"""
        try:
            session_data['updated_at'] = datetime.now().isoformat()
            session_file = self.store_dir / f"{session_id}.json"

            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)

            logger.debug(f"Session {session_id} saved")
            return True

        except Exception as e:
            logger.error(f"Save session error: {e}")
            return False

    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session from disk"""
        try:
            session_file = self.store_dir / f"{session_id}.json"

            if not session_file.exists():
                return None

            with open(session_file, 'r') as f:
                data = json.load(f)

            logger.debug(f"Session {session_id} loaded")
            return data

        except Exception as e:
            logger.error(f"Load session error: {e}")
            return None

    async def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all sessions"""
        try:
            sessions = []
            for session_file in sorted(
                self.store_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:limit]:
                with open(session_file, 'r') as f:
                    sessions.append(json.load(f))

            return sessions

        except Exception as e:
            logger.error(f"List sessions error: {e}")
            return []

    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            session_file = self.store_dir / f"{session_id}.json"

            if session_file.exists():
                session_file.unlink()
                logger.info(f"Session {session_id} deleted")
                return True

            return False

        except Exception as e:
            logger.error(f"Delete session error: {e}")
            return False

    async def save_artifact(self, session_id: str, filename: str, data: bytes) -> Optional[str]:
        """Save session artifact (screenshot, etc.)"""
        try:
            artifacts_dir = self.store_dir / session_id / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)

            artifact_path = artifacts_dir / filename

            with open(artifact_path, 'wb') as f:
                f.write(data)

            relative_path = str(artifact_path.relative_to(self.store_dir))
            logger.debug(f"Artifact saved: {relative_path}")
            return relative_path

        except Exception as e:
            logger.error(f"Save artifact error: {e}")
            return None

    async def load_artifact(self, session_id: str, filename: str) -> Optional[bytes]:
        """Load session artifact"""
        try:
            artifact_path = self.store_dir / session_id / "artifacts" / filename

            if not artifact_path.exists():
                return None

            with open(artifact_path, 'rb') as f:
                return f.read()

        except Exception as e:
            logger.error(f"Load artifact error: {e}")
            return None

    async def list_artifacts(self, session_id: str) -> List[str]:
        """List session artifacts"""
        try:
            artifacts_dir = self.store_dir / session_id / "artifacts"

            if not artifacts_dir.exists():
                return []

            return [f.name for f in artifacts_dir.glob("*")]

        except Exception as e:
            logger.error(f"List artifacts error: {e}")
            return []

    async def cleanup_old_sessions(self, days: int = 7) -> int:
        """Delete sessions older than N days"""
        try:
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(days=days)
            deleted_count = 0

            for session_file in self.store_dir.glob("*.json"):
                file_time = datetime.fromtimestamp(session_file.stat().st_mtime)
                if file_time < cutoff:
                    session_file.unlink()
                    deleted_count += 1

            logger.info(f"Deleted {deleted_count} old sessions")
            return deleted_count

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0

    async def get_statistics(self) -> Dict[str, Any]:
        """Get store statistics"""
        try:
            sessions = await self.list_sessions(limit=None)

            return {
                "total_sessions": len(sessions),
                "store_path": str(self.store_dir),
                "total_size_mb": sum(
                    f.stat().st_size for f in self.store_dir.rglob("*") if f.is_file()
                ) / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return {"error": str(e)}


# Global store instance
_store_instance: Optional[SessionStore] = None


def get_store() -> SessionStore:
    """Get or create global session store"""
    global _store_instance
    if _store_instance is None:
        store_dir = os.getenv("ARCHONX_SESSIONS_DIR", "/tmp/archonx/sessions")
        _store_instance = SessionStore(store_dir)
    return _store_instance
