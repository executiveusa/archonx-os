#!/bin/bash
# ARCHONX Phase 0 Baseline Audit (Bash version)
# Generates baseline inventory and conformance report

REPO_ROOT="${ARCHONX_REPO_ROOT:-.}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REPORT_DIR="$REPO_ROOT/ops/reports"

mkdir -p "$REPORT_DIR"

echo "============================================================"
echo "ARCHONX PHASE 0 BASELINE AUDIT"
echo "============================================================"
echo ""

# Count artifacts
echo "[P0] Inventorying artifacts..."
PLAN_COUNT=$(find "$REPO_ROOT/plans" -name "*.md" 2>/dev/null | wc -l)
DOC_COUNT=$(find "$REPO_ROOT/docs" -name "*.md" 2>/dev/null | wc -l)
AGENT_COUNT=$(find "$REPO_ROOT/agents" -name "config.json" 2>/dev/null | wc -l)

echo "  ✓ Plans: $PLAN_COUNT"
echo "  ✓ Docs: $DOC_COUNT"
echo "  ✓ Agents: $AGENT_COUNT"

# Generate markdown report
cat > "$REPORT_DIR/P0_CONFORMANCE_REPORT.md" << 'EOF'
# Phase 0 Baseline Audit Report

**Generated:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Artifact Inventory

### Plan Files
EOF

find "$REPO_ROOT/plans" -name "*.md" -type f 2>/dev/null | while read f; do
  basename "$f" >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md"
done

cat >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md" << 'EOF'

### Doc Files
EOF

find "$REPO_ROOT/docs" -name "*.md" -type f 2>/dev/null | while read f; do
  echo "- $(basename "$f")" >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md"
done

cat >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md" << 'EOF'

### Configured Agents
EOF

find "$REPO_ROOT/agents" -name "config.json" -type f 2>/dev/null | while read f; do
  agent_dir=$(dirname "$f")
  agent_name=$(basename "$agent_dir")
  echo "- $agent_name" >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md"
done

cat >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md" << 'EOF'

## Repository Status

### Submodules
EOF

if [ -f "$REPO_ROOT/.gitmodules" ]; then
  grep "path =" "$REPO_ROOT/.gitmodules" | sed 's/.* = /- /' >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md"
else
  echo "- None detected" >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md"
fi

cat >> "$REPORT_DIR/P0_CONFORMANCE_REPORT.md" << 'EOF'

### Connected Repositories
- archonx-os (primary)
- dashboard-agent-swarm
- paulisworld-openclaw-3d
- paulis-pope-bot
- agents/devika
- agents/darya
- agents/lightning

### Unconnected/External References
- E:/AGENT_ZERO (external, unconnected)
- Synthia-4.2 (credentials, unconnected)

## Summary

- Total plan files: $(find "$REPO_ROOT/plans" -name "*.md" 2>/dev/null | wc -l)
- Total doc files: $(find "$REPO_ROOT/docs" -name "*.md" 2>/dev/null | wc -l)
- Configured agents: $(find "$REPO_ROOT/agents" -name "config.json" 2>/dev/null | wc -l)

## Status

✅ **Phase 0 Baseline Audit Complete**

For Phase 0 → Phase 1 gate approval, verify:
- [ ] Artifact inventory accurate
- [ ] Repository connections mapped
- [ ] No critical missing references
- [ ] Baseline established as Go-Live checkpoint

---

**Prepared for:** Human Approval Gate
**Sign-off Required:** Yes
EOF

echo ""
echo "[P0] Generating baseline report..."
echo "  ✓ Report written to $REPORT_DIR/P0_CONFORMANCE_REPORT.md"

echo ""
echo "============================================================"
echo "PHASE 0 AUDIT COMPLETE"
echo "============================================================"
echo ""
echo "Next Step: Human approval to proceed to Phase 1"
echo "Report location: $REPORT_DIR/P0_CONFORMANCE_REPORT.md"
echo ""
