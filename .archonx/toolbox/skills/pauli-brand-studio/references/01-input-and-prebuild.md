## 5. INPUT ADAPTERS

Classify the intake before work begins.

### A. Blank / from scratch

Run the Brand Genesis interview. Establish business purpose, audience, offer, differentiation, values, personality, proof, constraints, legal name, languages, channels, physical/digital applications, and success criteria.

### B. URL

Inspect the live site and repository when available. Capture:

- screenshots at desktop, tablet, and mobile;
- logo and asset inventory;
- current palette, typography, spacing, components, imagery, iconography, motion, information architecture, copy, offers, CTAs, forms, states, accessibility, and technical stack;
- observed facts separately from inferences;
- broken, fake, provisional, or inconsistent elements.

Do not ask questions whose answers exist in the site or repository.

### C. Logo

Lock the supplied logo before exploration:

- preserve geometry, proportions, letterforms, spelling, colors, negative space, and symbol details;
- do not redraw, simplify, recolor, or reinterpret unless the user approves a redesign;
- inspect symbol meaning, wordmark meaning, clear space, minimum size, monochrome behavior, responsive variants, favicon/app icon behavior, and forbidden uses;
- never treat an AI-generated raster mark as final production artwork. Produce or request vector construction and optical correction.

### D. Single image or mood reference

Extract visual DNA without assuming the business:

- composition;
- palette;
- lighting;
- materiality;
- texture;
- geometry;
- rhythm;
- emotional temperature;
- photographic or illustrative treatment;
- cultural signals;
- what must not be copied.

Present these as hypotheses and confirm them.

### E. Existing repository / brownfield system

Preserve working behavior, routes, approved copy, backend contracts, package manager, and design tokens. Audit before redesign. Prefer targeted upgrades over replacement.

### F. Mixed intake

Use all sources. Resolve contradictions through source priority and explicit user confirmation.

Classify the project as:

- `greenfield`
- `brownfield`
- `hybrid`
- `recovery`
- `asset-extension`
- `brand-refresh`
- `full-rebrand`

---

## 6. PREBUILD GATE: RATE BEFORE CREATING ANYTHING

No design, image, logo, brand book, copy, artifact, or website may be generated before the prebuild gate passes.

Score these 20 readiness axes from 0-10:

1. Source completeness
2. Business clarity
3. Audience clarity
4. Offer and conversion clarity
5. Differentiation
6. Brand purpose and values
7. Proof and claim safety
8. Voice evidence
9. Visual evidence
10. Logo status
11. Application requirements
12. Accessibility requirements
13. Language and localization requirements
14. Rights and licensing status
15. Technical environment clarity
16. Deliverable scope
17. Approval authority
18. Budget/time/production constraints
19. Repository and handoff readiness
20. Contradiction resolution

Rules:

- Overall readiness must be at least 8.5.
- No critical axis may be below 8.0.
- Missing proof, rights, logo status, approval authority, or protected assets blocks final production.
- If readiness fails, continue discovery instead of generating filler.

Output:

```json
{
  "prebuild_score": 0,
  "critical_gaps": [],
  "confirmed_facts": [],
  "inferences": [],
  "contradictions": [],
  "next_question": "",
  "prebuild_gate": "PASS | FAIL | PROVISIONAL"
}
```

---

## 7. RELENTLESS DISCOVERY INTERVIEW

Ask one question at a time.

For each question:

1. summarize what is already known;
2. state the unresolved decision;
3. give a professional recommendation and short reason;
4. ask one precise question;
5. record the answer and confidence;
6. detect contradictions with earlier answers or source evidence;
7. revisit unresolved contradictions before completion.

Do not ask the user to repeat information available in files, URLs, repositories, screenshots, or prior confirmed answers.

Do not stop because a checklist was visited. Stop only when the prebuild gate passes and the user confirms the shared understanding.

Mandatory discovery domains:

- founder and business story;
- mission, purpose, values, and boundaries;
- audience segments, pains, language, objections, and desired transformation;
- offers, pricing model, CTA hierarchy, and conversion path;
- competitive category and distinct position;
- proof, claims, testimonials, metrics, and permissions;
- brand personality and anti-personality;
- cultural and geographic context;
- language and translation rules;
- logo meaning and preservation/redesign decision;
- desired and forbidden visual references;
- photography, illustration, icon, pattern, texture, and motion direction;
- physical and digital applications;
- accessibility and inclusion;
- ownership, licensing, trademark, consent, and image rights;
- approval workflow and human sign-off;
- maintenance and governance.

---
