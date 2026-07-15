## 18. AUDIT AND RELEASE SCORING

Score every completed project on these 20 axes:

1. Strategic clarity
2. Audience specificity
3. Offer and CTA clarity
4. Creative rationale
5. Distinctiveness
6. Logo system integrity
7. Typography
8. Color and contrast
9. Image and media system
10. Voice authenticity
11. Information architecture
12. Steve Krug usability
13. Accessibility
14. Responsive and native feel
15. Interaction states
16. Motion purpose and restraint
17. Anti-slop score
18. Performance and technical stability
19. Rights, provenance, and claim safety
20. Handoff and governance completeness

Scoring:

```text
0.0-5.9 fail
6.0-6.9 weak
7.0-7.9 usable but not client-ready
8.0-8.4 good but blocked from release
8.5-8.9 approval-ready
9.0-9.4 strong client-ready
9.5-10 exceptional
```

Caps:

- Any P0 issue caps the total at 6.9.
- Fake claims cap the total at 6.5.
- Generic AI-slop caps the total at 7.0.
- Unclear primary CTA caps the total at 7.4.
- Broken mobile behavior caps the total at 7.4.
- Broken links, buttons, routes, or forms cap the total at 7.9.
- Accessibility blockers cap the total at 7.9.
- Missing screenshot evidence caps audit quality at 6.9.
- Missing rollback before edits caps implementation quality at 6.9.
- Missing source ledger or repository inspection blocks the build entirely.

Release requires:

- overall score at least 8.5;
- target score 9.0;
- no P0 or unresolved P1 issue;
- every critical axis at least 8.0;
- Brand Guardian approval;
- Design Guardian approval;
- Voice Guardian approval for public copy;
- rights/provenance check;
- mobile, keyboard, reduced-motion, link, form, console, and performance evidence;
- rollback proof;
- user approval where required.

---

## 19. GUARDIAN REVIEW

The agent that creates a design may not be the sole approver.

Run independent passes:

### Brand Guardian

Checks strategy, differentiation, logo integrity, applications, coherence, and governance.

### Design Guardian

Checks Krug usability, hierarchy, anti-slop, accessibility, responsive behavior, states, motion, and technical feasibility.

### Voice Guardian

Checks authenticity, proof, claim safety, platform rules, localization, and Stop-Slop score.

### Rights Guardian

Checks licenses, attribution, consent, provenance, trademark risk flags, and prohibited asset transformations.

Guardians file findings. They do not hide or silently waive them.

---
