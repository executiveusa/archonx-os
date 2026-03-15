#!/usr/bin/env python3
"""
BEAD-PROD-CALL-001: Production readiness call to Pauli
Run: python scripts/production_call.py
Requires: TWILIO_ACCOUNT_SID, TWILIO_SECRET, TWILIO_PAULI_NUMBER in env
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Try to load master.env
master_env = Path("E:/THE PAULI FILES/master.env")
if master_env.exists():
    load_dotenv(master_env)
else:
    load_dotenv(".env")

from archonx.agents.archon_x_phone import ArchonXPhone


def main() -> None:
    phone = ArchonXPhone()
    if phone._mock:
        print("ERROR: Twilio credentials not set. Set TWILIO_ACCOUNT_SID, TWILIO_SECRET, TWILIO_PAULI_NUMBER")
        sys.exit(1)

    print("Placing production readiness call to +13234842914...")
    result = ArchonXPhone.production_call()
    print(f"Call placed: {result}")


if __name__ == "__main__":
    main()
