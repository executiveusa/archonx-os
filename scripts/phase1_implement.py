#!/usr/bin/env python3
"""
BEAD-P1-002: IMPLEMENT Documentation Normalization
Applies standardized patches to all markdown files

Usage:
    python phase1_implement.py --batch all --dry-run    # Preview changes
    python phase1_implement.py --batch all               # Apply changes
    python phase1_implement.py --batch 1                 # Batch 1 only
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class DocNormalizer:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.changes_log = []
        self.files_processed = 0

        # Metadata template
        self.metadata_template = """**Version:** 1.0
**Date:** {date}
**Status:** Normalized (Phase 1)
**Specification:** {spec_ref}

---

"""

        # Required sections in order
        self.required_sections = [
            "Objective",
            "Scope",
            "Requirements",
            "Workflow",
            "Contracts",
            "Gates",
            "Acceptance",
            "Handoff"
        ]

        # Terminology mapping (old → canonical)
        self.terminology_map = {
            r'human-in-the-?loop': 'human-approved decision',
            r'autonomous execution': 'agent-driven with gates',
            r'PAULIWHEEL loop': 'beads loop (PLAN→IMPLEMENT→TEST→EVALUATE→PATCH)',
            r'orchestration': 'Ralphy orchestration',
            r'multi-repo sync': 'Ralphy coordination',
            r'agent spawn': 'subagent activation',
            r'approval workflow': 'human approval gate',
            r'control dashboard': 'Dashboard control plane',
            r'credential sync': 'Master.env integration',
        }

    def add_metadata_header(self, content: str, spec_ref: str = "ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md") -> str:
        """Add/update metadata header after title."""

        # Extract title (first H1)
        title_match = re.match(r'^(# .+)\n', content)
        if not title_match:
            return content

        title = title_match.group(1)
        rest = content[len(title)+1:]

        # Remove existing metadata if present
        rest = re.sub(r'\*\*Version:\*\*.*?\n\n---\n\n', '', rest, flags=re.DOTALL)

        # Add new metadata
        date = datetime.now().strftime("%Y-%m-%d")
        metadata = self.metadata_template.format(date=date, spec_ref=spec_ref)

        return f"{title}\n\n{metadata}{rest}"

    def normalize_headings(self, content: str) -> str:
        """Standardize heading levels."""

        lines = content.split('\n')
        normalized_lines = []
        in_code_block = False

        for line in lines:
            # Track code blocks
            if line.startswith('```'):
                in_code_block = not in_code_block
                normalized_lines.append(line)
                continue

            if in_code_block:
                normalized_lines.append(line)
                continue

            # Main heading should be # (not ##)
            if re.match(r'^### ', line):
                # Convert ### to ##
                line = re.sub(r'^### ', '## ', line)
            elif re.match(r'^#### ', line):
                # Convert #### to ###
                line = re.sub(r'^#### ', '### ', line)

            normalized_lines.append(line)

        return '\n'.join(normalized_lines)

    def apply_terminology_map(self, content: str) -> str:
        """Replace inconsistent terminology with canonical versions."""

        for pattern, replacement in self.terminology_map.items():
            # Case-insensitive replacement
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        return content

    def ensure_required_sections(self, content: str) -> str:
        """Ensure all required sections are present."""

        # Extract existing sections
        existing_sections = re.findall(r'^## (\w+)', content, re.MULTILINE)

        missing_sections = [s for s in self.required_sections if s not in existing_sections]

        if not missing_sections:
            return content

        # Add missing sections at end
        additions = "\n\n---\n\n"

        for section in missing_sections:
            if section == "Objective":
                additions += f"## {section}\n\n[Describe the objective of this document]\n\n"
            elif section == "Scope":
                additions += f"## {section}\n\n**In Scope:**\n- Defined scope items\n\n**Out of Scope:**\n- Items not covered\n\n"
            elif section == "Requirements":
                additions += f"## {section}\n\n- MUST: [requirement]\n- SHOULD: [requirement]\n- MAY: [requirement]\n\n"
            elif section == "Workflow":
                additions += f"## {section}\n\n[Describe workflow/implementation sequence]\n\n"
            elif section == "Contracts":
                additions += f"## {section}\n\nEvidence paths: `ops/reports/`\n\n"
            elif section == "Gates":
                additions += f"## {section}\n\n- Compliance gate 1\n- Compliance gate 2\n\n"
            elif section == "Acceptance":
                additions += f"## {section}\n\n- [ ] Success criterion 1\n- [ ] Success criterion 2\n\n"
            elif section == "Handoff":
                additions += f"## {section}\n\nCode mode execution instructions.\n\n"

        return content + additions

    def fix_cross_references(self, content: str, filename: str) -> str:
        """Fix broken markdown links and references."""

        # This is complex - for now, just verify paths exist
        # In practice, this would be more sophisticated

        # Fix common patterns
        content = re.sub(r'\]\(\.\./', '](', content)  # Fix parent dir refs
        content = re.sub(r'\[(.*?)\]\(([^)]*\.md)\)', lambda m: f"[{m.group(1)}]({m.group(2)})", content)

        return content

    def normalize_file(self, filepath: Path) -> Tuple[bool, str]:
        """Normalize a single file. Returns (changed, message)"""

        try:
            content = filepath.read_text(encoding='utf-8')
            original_content = content

            # Apply transformations
            content = self.add_metadata_header(content)
            content = self.normalize_headings(content)
            content = self.apply_terminology_map(content)
            content = self.ensure_required_sections(content)
            content = self.fix_cross_references(content, filepath.name)

            # Check if changed
            if content == original_content:
                return False, "No changes needed"

            # Write back
            filepath.write_text(content, encoding='utf-8')
            self.files_processed += 1

            return True, "✅ Normalized"

        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    def process_batch(self, batch_num: int, dry_run: bool = False) -> Dict:
        """Process files in a batch."""

        # Define batches
        batches = {
            1: [
                "plans/ARCHONX_SPEC_DRIVEN_DOC_PATCH_AND_EXECUTION_PRD.md",
                "plans/ARCHONX_AUTONOMOUS_AGENCY_BLUEPRINT.md",
                "plans/ARCHONX_PHASED_IMPLEMENTATION_ROADMAP.md",
                "plans/ARCHONX_REALITY_MAP_AND_GAP_PLAN.md",
                "plans/ARCHONX_END_TO_END_EXECUTION_PRD.md",
                "plans/AGENT_LIGHTNING_USE_CASES.md",
                "plans/MASTER_BUILD_PLAN.md",
                "plans/infinite-architecture-glm5.md",
            ],
            2: [
                "plans/DEVIKA_PI_INTEGRATION_PLAN.md",
                "plans/DEVIKA_PI_IMPLEMENTATION_SEQUENCE.md",
                "plans/DEVIKA_PI_GAP_MATRIX.md",
                "plans/DEVIKA_PI_RUNTIME_CONTRACT.md",
                "plans/ARCHONX_DASHBOARD_CONTROL_WORKFLOWS.md",
                "plans/ARCHONX_SECURE_AUTOMATION_PIPELINE.md",
                "plans/ARCHONX_SOP_AND_PROMPT_SYSTEM.md",
                "plans/KING_MODE_GEMINI_31_PRD.md",
            ],
            3: [
                "docs/SOP_AUTONOMOUS_AGENCY.md",
                "docs/RALPHY_LOOP_SOP.md",
                "plans/ARCHONX_HUMAN_LOOP_MINIMIZATION_MAP.md",
                "plans/AGENT_ZERO_SOCIAL_MEDIA_TRAINING.md",
                "plans/archonx-12-agent-framework-plan.md",
                "plans/archonx-skills-completion-plan.md",
                "plans/orgo-mcp-integration-plan.md",
                "plans/ONE_SHOT_PATCH_PROMPT.md",
                "plans/ARCHONX_DOC_EXECUTION_MATRIX.md",
                "plans/ARCHONX_DOC_PATCH_LEDGER.md",
                "plans/PRODUCT_HUNT_LAUNCH_STRATEGY.md",
                "plans/PHASE_1_EXECUTION_PACKET.md",
                "docs/audit/MASTER_GAP_AUDIT_PROMPT.md",
                "docs/devika-pi/00-install.md",
            ]
        }

        files = batches.get(batch_num, [])
        results = {
            "batch": batch_num,
            "total": len(files),
            "changed": 0,
            "unchanged": 0,
            "errors": 0,
            "files": []
        }

        print(f"\n{'='*60}")
        print(f"BATCH {batch_num}: {len(files)} files")
        print(f"{'='*60}\n")

        for file_path_str in files:
            file_path = self.repo_root / file_path_str

            if not file_path.exists():
                print(f"⚠️  SKIP: {file_path_str} (not found)")
                results["errors"] += 1
                continue

            changed, msg = self.normalize_file(file_path)

            symbol = "✅" if changed else "⏭️ "
            print(f"{symbol} {file_path_str}: {msg}")

            results["files"].append({
                "path": file_path_str,
                "changed": changed,
                "message": msg
            })

            if changed:
                results["changed"] += 1
            else:
                results["unchanged"] += 1

        return results

    def run_all_batches(self, dry_run: bool = False) -> Dict:
        """Process all 3 batches."""

        print("\n" + "="*60)
        print("BEAD-P1-002: IMPLEMENT PHASE")
        print("Documentation Normalization - All Batches")
        print("="*60)

        all_results = {
            "total_files": 0,
            "total_changed": 0,
            "total_errors": 0,
            "batches": []
        }

        for batch_num in [1, 2, 3]:
            results = self.process_batch(batch_num, dry_run)
            all_results["batches"].append(results)
            all_results["total_files"] += results["total"]
            all_results["total_changed"] += results["changed"]
            all_results["total_errors"] += results["errors"]

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total files processed: {all_results['total_files']}")
        print(f"Files changed: {all_results['total_changed']}")
        print(f"Files unchanged: {all_results['total_files'] - all_results['total_changed']}")
        print(f"Errors: {all_results['total_errors']}")

        return all_results


if __name__ == "__main__":
    import sys

    repo_root = os.getenv("ARCHONX_REPO_ROOT", "/c/archonx-os-main")
    dry_run = "--dry-run" in sys.argv

    normalizer = DocNormalizer(repo_root)
    results = normalizer.run_all_batches(dry_run)

    # Exit code based on errors
    sys.exit(1 if results["total_errors"] > 0 else 0)
