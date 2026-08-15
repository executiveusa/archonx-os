## 16. HTML-FIRST PRODUCTION AND HOST ROUTING

Use HTML as the primary human review surface for audits, design decisions, prototypes, fixes, reports, and handoffs.

Required files when applicable:

```text
audit.html
prd.html
creative-brief.html
brandbook.html
voice-examples.html
fix-lab.html
implementation-report.html
handoff.html
batch-audit-index.html
```

### Environment routing

- **Standalone document:** produce a complete self-contained HTML document.
- **Production website/app:** follow the existing repository framework and architecture.
- **Claude-compatible artifact iframe:** follow the exact compatible artifact constraints from the supplied artifact skill.
- **ChatGPT or another artifact host:** detect and follow that host's current constraints. Do not assume Claude-specific APIs, storage, or markup.
- **PDF:** author from the appropriate HTML, DOCX, or slide source, render, and visually verify.

Every visual fix follows:

`evidence -> audit.html -> prd.html -> fix-lab.html -> approval -> implementation -> implementation-report.html`

No screenshot evidence means no visual QA claim.

---

## 17. DESIGN HANDOFF CONTRACT

When a design is ready for engineering, create a complete handoff that specifies rather than implies.

Required sections:

- overview and user context;
- layout and grid;
- design tokens;
- components, variants, and props;
- default, hover, focus, active, selected, disabled, loading, empty, error, offline, and success states;
- click, tap, keyboard, gesture, and navigation behavior;
- responsive breakpoints and behavior;
- content limits, truncation, long text, international text, missing data, and slow connection behavior;
- motion trigger, property, duration, easing, and reduced-motion fallback;
- accessibility roles, names, focus order, announcements, contrast, and touch targets;
- edge cases;
- file allowlist;
- implementation risks;
- acceptance criteria;
- screenshot references;
- rollback path.

Use tokens as the source of truth. Include raw values in the token table for implementation, but components should reference token names.

Outputs:

```text
handoff.html
handoff.md
component-specs.json
acceptance-matrix.json
```

---
