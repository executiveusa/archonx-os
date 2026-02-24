#!/bin/bash
# BEAD-P1-001 AUDIT SCRIPT
# Checks all markdown files for spec conformance

SPEC_SECTIONS=(
  "Objective"
  "Scope"
  "Requirements"
  "Workflow"
  "Contracts"
  "Gates"
  "Acceptance"
  "Handoff"
)

REPORT_FILE="ops/reports/P1_AUDIT_REPORT.json"
mkdir -p ops/reports

# Start JSON report
cat > "$REPORT_FILE" << 'EOF'
{
  "phase": 1,
  "bead_id": "BEAD-P1-001",
  "stage": "PLAN",
  "timestamp": "2026-02-24T00:00:00Z",
  "audit_results": {
    "total_files": 0,
    "conformant": 0,
    "non_conformant": 0,
    "files": []
  },
  "missing_sections_summary": {},
  "patch_priorities": {
    "critical": [],
    "high": [],
    "medium": [],
    "low": []
  }
}
EOF

# Audit each file
echo "Auditing files..."

find plans docs -name "*.md" -type f | sort | while read file; do
  echo "Checking: $file"

  # Count section occurrences
  has_objective=$(grep -c "## Objective\|# Objective" "$file" 2>/dev/null || echo 0)
  has_scope=$(grep -c "## Scope\|# Scope" "$file" 2>/dev/null || echo 0)
  has_requirements=$(grep -c "## Requirements\|# Requirements" "$file" 2>/dev/null || echo 0)
  has_workflow=$(grep -c "## Workflow\|## Implementation\|# Implementation" "$file" 2>/dev/null || echo 0)
  has_contracts=$(grep -c "## Contract\|## Data Contract" "$file" 2>/dev/null || echo 0)
  has_gates=$(grep -c "## Gate\|## Compliance" "$file" 2>/dev/null || echo 0)
  has_acceptance=$(grep -c "## Acceptance\|## Success Criteria" "$file" 2>/dev/null || echo 0)
  has_handoff=$(grep -c "## Handoff" "$file" 2>/dev/null || echo 0)

  # Count missing
  missing=0
  missing_list=""

  [ "$has_objective" -eq 0 ] && missing=$((missing+1)) && missing_list="$missing_list Objective"
  [ "$has_scope" -eq 0 ] && missing=$((missing+1)) && missing_list="$missing_list Scope"
  [ "$has_acceptance" -eq 0 ] && missing=$((missing+1)) && missing_list="$missing_list 'Acceptance/Success'"

  if [ "$missing" -eq 0 ]; then
    echo "  ✅ CONFORMANT"
  else
    echo "  ⚠️  NEEDS PATCHES (missing: $missing_list)"
  fi
done

# Generate summary
echo ""
echo "========================================"
echo "AUDIT COMPLETE"
echo "========================================"
echo "Report generated: $REPORT_FILE"
