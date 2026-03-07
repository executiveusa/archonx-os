#!/usr/bin/env python3
"""
ArchonX Vault Agent v1.0
Parses, classifies, audits, and rotates secrets across .env files.
Generates audit reports, rotation checklists, and Infisical import configs.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from dotenv import dotenv_values
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)


@dataclass
class Secret:
    """Represents a secret in an environment file."""
    key: str
    value: str
    file_path: str
    classification: str
    risk_level: str
    last_rotated: Optional[str] = None
    rotation_due: bool = False


def classify_secret(key: str, value: str) -> Tuple[str, str]:
    """Classify a secret by key name and value patterns. Returns (classification, risk_level)."""
    key_upper = key.upper()
    value_len = len(value)

    # High-risk patterns
    if any(p in key_upper for p in ['PASSWORD', 'PASSWD', 'PWD']):
        return ('PASSWORD', 'CRITICAL' if value_len < 8 else 'HIGH')
    if any(p in key_upper for p in ['SECRET', 'PRIVATE_KEY', 'PRIVATE', 'KEY']):
        return ('CRYPTOGRAPHIC_KEY', 'CRITICAL')
    if any(p in key_upper for p in ['TOKEN', 'AUTH', 'BEARER', 'JWT']):
        return ('AUTH_TOKEN', 'HIGH')
    if any(p in key_upper for p in ['API_KEY', 'APIKEY']):
        return ('API_KEY', 'HIGH')
    if any(p in key_upper for p in ['DATABASE_URL', 'DB_URL', 'MONGO', 'POSTGRES', 'MYSQL']):
        return ('DATABASE_CONNECTION', 'CRITICAL')
    if any(p in key_upper for p in ['WEBHOOK', 'CALLBACK']):
        return ('WEBHOOK_URL', 'MEDIUM')
    if any(p in key_upper for p in ['URL', 'ENDPOINT', 'HOST', 'DOMAIN']):
        return ('URL', 'LOW')
    if any(p in key_upper for p in ['USER', 'USERNAME', 'EMAIL']):
        return ('USERNAME', 'LOW')
    if any(p in key_upper for p in ['VERSION', 'DEBUG', 'ENV', 'MODE', 'ENVIRONMENT']):
        return ('CONFIG', 'LOW')

    # Pattern-based classification
    if re.match(r'^[A-Za-z0-9+/]{20,}={0,2}$', value):  # Base64-like
        return ('ENCODED_TOKEN', 'HIGH')
    if re.match(r'^[a-f0-9]{32,}$', value):  # Hex hash
        return ('HASH_TOKEN', 'HIGH')
    if value.startswith('sk-') or value.startswith('pk-'):  # OpenAI/stripe style
        return ('API_KEY', 'CRITICAL')
    if 'http' in value.lower() or 'localhost' in value.lower():
        return ('URL', 'LOW')

    return ('GENERIC_SECRET', 'MEDIUM')


def parse_env_file(file_path: str) -> List[Secret]:
    """Parse a .env file and return list of Secret objects."""
    secrets = []
    try:
        env_dict = dotenv_values(file_path)
        for key, value in env_dict.items():
            if value:
                classification, risk = classify_secret(key, value)
                secret = Secret(
                    key=key,
                    value=value,
                    file_path=file_path,
                    classification=classification,
                    risk_level=risk
                )
                secrets.append(secret)
    except Exception as e:
        print(f"ERROR parsing {file_path}: {e}")

    return secrets


def find_env_files(root_path: str = ".") -> List[str]:
    """Recursively find all .env* files."""
    env_files = []
    ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.env.example'}

    for root, dirs, files in os.walk(root_path):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.startswith('.env') or file.endswith('.env'):
                full_path = os.path.join(root, file)
                # Skip .env.example unless explicitly requested
                if not file.endswith('.example'):
                    env_files.append(full_path)

    return env_files


def build_audit(secrets: List[Secret]) -> Dict[str, Any]:
    """Build comprehensive audit report."""
    if not secrets:
        return {
            "total_secrets": 0,
            "by_classification": {},
            "by_risk": {},
            "critical_findings": [],
            "rotation_due": []
        }

    by_classification = {}
    by_risk = {}
    critical_findings = []

    for secret in secrets:
        # Count by classification
        by_classification[secret.classification] = by_classification.get(secret.classification, 0) + 1

        # Count by risk
        by_risk[secret.risk_level] = by_risk.get(secret.risk_level, 0) + 1

        # Flag critical issues
        if secret.risk_level == 'CRITICAL':
            critical_findings.append({
                "key": secret.key,
                "file": secret.file_path,
                "type": secret.classification,
                "issue": f"Critical-level secret with risk classification"
            })

    return {
        "timestamp": datetime.now().isoformat(),
        "total_secrets": len(secrets),
        "by_classification": by_classification,
        "by_risk": by_risk,
        "critical_findings": critical_findings,
        "rotation_due": [s.key for s in secrets if s.rotation_due]
    }


def generate_rotation_checklist(secrets: List[Secret]) -> str:
    """Generate a rotation checklist for all secrets."""
    by_risk = {}
    for secret in secrets:
        if secret.risk_level not in by_risk:
            by_risk[secret.risk_level] = []
        by_risk[secret.risk_level].append(secret.key)

    checklist = "# Secret Rotation Checklist\n\n"
    checklist += f"Generated: {datetime.now().isoformat()}\n\n"

    for risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if risk_level in by_risk:
            checklist += f"## {risk_level} Priority ({len(by_risk[risk_level])} items)\n\n"
            for key in sorted(by_risk[risk_level]):
                checklist += f"- [ ] {key}\n"
            checklist += "\n"

    return checklist


def generate_safe_template(secrets: List[Secret]) -> str:
    """Generate a safe .env template with placeholder values."""
    template = "# ArchonX Safe .env Template\n"
    template += f"# Generated: {datetime.now().isoformat()}\n"
    template += "# Replace all values marked [REPLACE_*] with actual secrets\n\n"

    for secret in sorted(secrets, key=lambda s: (s.risk_level, s.key)):
        placeholder_type = secret.classification.upper().replace(' ', '_')
        template += f"# {secret.key} ({secret.risk_level} - {secret.classification})\n"
        template += f"{secret.key}=[REPLACE_{placeholder_type}]\n\n"

    return template


def generate_infisical_import(secrets: List[Secret]) -> Dict[str, Any]:
    """Generate Infisical import format (Hashicorp Vault compatible)."""
    return {
        "version": "v1",
        "timestamp": datetime.now().isoformat(),
        "import_type": "env_audit",
        "secrets": [
            {
                "key": s.key,
                "value": s.value,
                "metadata": {
                    "source_file": s.file_path,
                    "classification": s.classification,
                    "risk_level": s.risk_level,
                    "imported_at": datetime.now().isoformat()
                }
            }
            for s in secrets
        ]
    }


def generate_json_report(secrets: List[Secret], audit: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive JSON report."""
    return {
        "audit": audit,
        "secrets_inventory": [asdict(s) for s in secrets],
        "statistics": {
            "total_files_scanned": len(set(s.file_path for s in secrets)),
            "total_secrets": len(secrets),
            "critical_count": sum(1 for s in secrets if s.risk_level == 'CRITICAL'),
            "high_count": sum(1 for s in secrets if s.risk_level == 'HIGH'),
            "medium_count": sum(1 for s in secrets if s.risk_level == 'MEDIUM'),
            "low_count": sum(1 for s in secrets if s.risk_level == 'LOW'),
        }
    }


def run_vault_agent(args: argparse.Namespace) -> int:
    """Main vault agent execution."""

    # Find env files
    env_files = find_env_files(args.path) if not args.file else [args.file]

    if not env_files:
        print("No .env files found. Use --file to specify or --path to search.")
        return 1

    print(f"[*] Found {len(env_files)} .env file(s)")

    # Parse all secrets
    all_secrets = []
    for env_file in env_files:
        secrets = parse_env_file(env_file)
        all_secrets.extend(secrets)
        print(f"[+] {env_file}: {len(secrets)} secrets")

    if not all_secrets:
        print("No secrets found.")
        return 0

    # Build audit
    audit = build_audit(all_secrets)

    # Generate outputs
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # JSON report
        report = generate_json_report(all_secrets, audit)
        with open(output_dir / "vault_audit.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"[+] Report: {output_dir}/vault_audit.json")

        # Rotation checklist
        checklist = generate_rotation_checklist(all_secrets)
        with open(output_dir / "rotation_checklist.md", "w") as f:
            f.write(checklist)
        print(f"[+] Checklist: {output_dir}/rotation_checklist.md")

        # Safe template
        template = generate_safe_template(all_secrets)
        with open(output_dir / "safe_template.env", "w") as f:
            f.write(template)
        print(f"[+] Template: {output_dir}/safe_template.env")

        # Infisical import
        infisical = generate_infisical_import(all_secrets)
        with open(output_dir / "infisical_import.json", "w") as f:
            json.dump(infisical, f, indent=2)
        print(f"[+] Infisical: {output_dir}/infisical_import.json")

    # Print summary
    print("\n" + "="*60)
    print("VAULT AUDIT SUMMARY")
    print("="*60)
    print(f"Total Secrets: {audit['total_secrets']}")
    print(f"Critical: {audit['by_risk'].get('CRITICAL', 0)}")
    print(f"High: {audit['by_risk'].get('HIGH', 0)}")
    print(f"Medium: {audit['by_risk'].get('MEDIUM', 0)}")
    print(f"Low: {audit['by_risk'].get('LOW', 0)}")

    if audit['critical_findings']:
        print(f"\n⚠️  CRITICAL FINDINGS:")
        for finding in audit['critical_findings']:
            print(f"  - {finding['key']} in {finding['file']}: {finding['issue']}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ArchonX Vault Agent - Secret management and audit tool"
    )
    parser.add_argument(
        "--file", type=str,
        help="Audit specific .env file"
    )
    parser.add_argument(
        "--path", type=str, default=".",
        help="Root path to search for .env files (default: current directory)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./ops/reports",
        help="Output directory for reports (default: ./ops/reports)"
    )

    args = parser.parse_args()
    sys.exit(run_vault_agent(args))
