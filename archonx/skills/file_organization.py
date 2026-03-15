"""
File Organization Skill
=======================
Sort, rename, tag, and organize files using pathlib.
Supports multiple organization strategies and batch operations.

Podcast use case: "organize files — sort by type, rename, tag, archive"
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from archonx.skills.base import BaseSkill, SkillCategory, SkillContext, SkillResult

logger = logging.getLogger("archonx.skills.file_organization")

# File type categories
FILE_CATEGORIES = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"},
    "videos": {".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
    "archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "code": {".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php"},
    "data": {".json", ".xml", ".csv", ".yaml", ".yml", ".sql", ".db"},
    "executables": {".exe", ".msi", ".app", ".dmg", ".deb", ".rpm"},
}


class FileOrganizationSkill(BaseSkill):
    """Sort, rename, tag, and organize files and folders."""

    name = "file_organization"
    description = "Sort, rename, tag, and organize files and folders"
    category = SkillCategory.PERSONAL

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        Organize files based on the specified action.

        Params:
            action: 'organize' | 'rename' | 'tag' | 'archive' | 'sort_by_date' | 'deduplicate'
            path: Target directory path (required)
            pattern: Glob pattern for file selection (default: '*')
            destination: Destination path for move/archive operations
            rename_pattern: Pattern for renaming (supports {index}, {date}, {name})
            create_subfolders: Whether to create category subfolders (default: True)
            dry_run: Preview changes without executing (default: False)
        """
        action = context.params.get("action", "organize")
        path = context.params.get("path", "")
        pattern = context.params.get("pattern", "*")
        destination = context.params.get("destination")
        rename_pattern = context.params.get("rename_pattern", "{name}")
        create_subfolders = context.params.get("create_subfolders", True)
        dry_run = context.params.get("dry_run", False)

        if not path:
            return SkillResult(
                skill=self.name,
                status="error",
                error="Path is required for file organization",
                data={}
            )

        target_path = Path(path).expanduser().resolve()

        if not target_path.exists():
            return SkillResult(
                skill=self.name,
                status="error",
                error=f"Path does not exist: {target_path}",
                data={"path": str(target_path)}
            )

        # Execute the appropriate action
        try:
            if action == "organize":
                result = await self._organize_files(
                    target_path, pattern, create_subfolders, dry_run
                )
            elif action == "rename":
                result = await self._rename_files(
                    target_path, pattern, rename_pattern, dry_run
                )
            elif action == "tag":
                result = await self._tag_files(target_path, pattern, dry_run)
            elif action == "archive":
                result = await self._archive_files(
                    target_path, pattern, destination, dry_run
                )
            elif action == "sort_by_date":
                result = await self._sort_by_date(target_path, pattern, dry_run)
            elif action == "deduplicate":
                result = await self._deduplicate_files(target_path, pattern, dry_run)
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
                    "path": str(target_path),
                    "dry_run": dry_run
                }
            )

        except Exception as e:
            logger.error("File organization failed: %s", str(e))
            return SkillResult(
                skill=self.name,
                status="error",
                error=str(e),
                data={"path": str(target_path)}
            )

    async def _organize_files(
        self,
        path: Path,
        pattern: str,
        create_subfolders: bool,
        dry_run: bool
    ) -> dict[str, Any]:
        """Organize files into category subfolders."""
        files_processed = 0
        files_moved = []
        categories_created = set()

        for file_path in path.glob(pattern):
            if not file_path.is_file():
                continue

            files_processed += 1
            category = self._get_file_category(file_path)

            if category == "other":
                continue

            category_path = path / category

            if create_subfolders:
                if not dry_run and not category_path.exists():
                    category_path.mkdir(parents=True, exist_ok=True)
                    categories_created.add(category)

            destination = category_path / file_path.name

            if not dry_run:
                shutil.move(str(file_path), str(destination))

            files_moved.append({
                "original": str(file_path.relative_to(path)),
                "destination": str(destination.relative_to(path)),
                "category": category
            })

        return {
            "files_processed": files_processed,
            "files_moved": len(files_moved),
            "moves": files_moved,
            "categories_created": list(categories_created)
        }

    async def _rename_files(
        self,
        path: Path,
        pattern: str,
        rename_pattern: str,
        dry_run: bool
    ) -> dict[str, Any]:
        """Rename files according to a pattern."""
        files_processed = 0
        files_renamed = []

        for index, file_path in enumerate(path.glob(pattern), 1):
            if not file_path.is_file():
                continue

            files_processed += 1

            # Build new name from pattern
            new_name = rename_pattern.format(
                index=index,
                date=datetime.now().strftime("%Y%m%d"),
                name=file_path.stem,
                ext=file_path.suffix
            )

            if not new_name.endswith(file_path.suffix):
                new_name += file_path.suffix

            new_path = file_path.parent / new_name

            if not dry_run:
                file_path.rename(new_path)

            files_renamed.append({
                "original": file_path.name,
                "new_name": new_name
            })

        return {
            "files_processed": files_processed,
            "files_renamed": len(files_renamed),
            "renames": files_renamed
        }

    async def _tag_files(
        self,
        path: Path,
        pattern: str,
        dry_run: bool
    ) -> dict[str, Any]:
        """Add tags to files via extended attributes or sidecar files."""
        files_processed = 0
        files_tagged = []

        for file_path in path.glob(pattern):
            if not file_path.is_file():
                continue

            files_processed += 1
            category = self._get_file_category(file_path)

            # Create a sidecar tag file
            tag_file = file_path.with_suffix(file_path.suffix + ".tags")
            tags = [category, file_path.suffix.lower().lstrip(".")]

            if not dry_run:
                tag_file.write_text("\n".join(tags))

            files_tagged.append({
                "file": file_path.name,
                "tags": tags
            })

        return {
            "files_processed": files_processed,
            "files_tagged": len(files_tagged),
            "tagged": files_tagged
        }

    async def _archive_files(
        self,
        path: Path,
        pattern: str,
        destination: str | None,
        dry_run: bool
    ) -> dict[str, Any]:
        """Archive files to a zip file."""
        files_processed = 0
        archive_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        archive_path = Path(destination) / archive_name if destination else path / archive_name

        files_to_archive = list(path.glob(pattern))
        files_to_archive = [f for f in files_to_archive if f.is_file()]

        if not dry_run and files_to_archive:
            shutil.make_archive(
                str(archive_path.with_suffix("")),
                "zip",
                path,
                base_dir=None
            )

        files_processed = len(files_to_archive)

        return {
            "files_processed": files_processed,
            "archive_path": str(archive_path),
            "files_archived": [f.name for f in files_to_archive]
        }

    async def _sort_by_date(
        self,
        path: Path,
        pattern: str,
        dry_run: bool
    ) -> dict[str, Any]:
        """Sort files into year/month subfolders based on modification date."""
        files_processed = 0
        files_moved = []

        for file_path in path.glob(pattern):
            if not file_path.is_file():
                continue

            files_processed += 1

            # Get file modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            year_month = mtime.strftime("%Y/%m")

            date_path = path / year_month

            if not dry_run and not date_path.exists():
                date_path.mkdir(parents=True, exist_ok=True)

            destination = date_path / file_path.name

            if not dry_run:
                shutil.move(str(file_path), str(destination))

            files_moved.append({
                "file": file_path.name,
                "destination": str(destination.relative_to(path))
            })

        return {
            "files_processed": files_processed,
            "files_moved": len(files_moved),
            "moves": files_moved
        }

    async def _deduplicate_files(
        self,
        path: Path,
        pattern: str,
        dry_run: bool
    ) -> dict[str, Any]:
        """Find and remove duplicate files based on content hash."""
        import hashlib

        files_processed = 0
        duplicates_found = 0
        duplicates = []
        hash_map: dict[str, list[Path]] = {}

        # Calculate hashes for all files
        for file_path in path.glob(pattern):
            if not file_path.is_file():
                continue

            files_processed += 1

            try:
                file_hash = self._calculate_file_hash(file_path)

                if file_hash in hash_map:
                    hash_map[file_hash].append(file_path)
                else:
                    hash_map[file_hash] = [file_path]
            except Exception as e:
                logger.warning("Could not hash %s: %s", file_path, e)

        # Find duplicates
        for file_hash, files in hash_map.items():
            if len(files) > 1:
                # Keep the first file, mark others as duplicates
                original = files[0]
                for dup in files[1:]:
                    duplicates_found += 1
                    duplicates.append({
                        "original": str(original.relative_to(path)),
                        "duplicate": str(dup.relative_to(path)),
                        "size": dup.stat().st_size
                    })

                    if not dry_run:
                        dup.unlink()

        return {
            "files_processed": files_processed,
            "duplicates_found": duplicates_found,
            "space_saved": sum(d["size"] for d in duplicates),
            "duplicates": duplicates
        }

    def _get_file_category(self, file_path: Path) -> str:
        """Determine the category of a file based on its extension."""
        ext = file_path.suffix.lower()

        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                return category

        return "other"

    def _calculate_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of a file."""
        import hashlib

        hasher = hashlib.md5()

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)

        return hasher.hexdigest()
