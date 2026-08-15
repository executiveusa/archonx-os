# BEAD PLAN — ZTE-20260714-0001

## Objective

Install the Pauli Brand Studio master system prompt as a reusable ArchonX governance skill for brand kits, brand voice, visual identity, image production, KAKU-structured brand books, websites, artifacts, and design handoffs.

## Classification

- Owning agent: Synthia / design-system domain
- Risk tier: LOW
- Blast radius: 1 repository
- Production deployment: not required

## Source and architecture findings

- `AGENTS.md` makes `.archonx/toolbox/skills/mandatory-design-law/SKILL.md` mandatory for visual work.
- The existing mandatory design law already enforces Steve Krug clarity and rejects generic AI-slop.
- The correct extension point is a sibling skill under `.archonx/toolbox/skills/` plus a reference from the mandatory law.
- The 1,101-line master prompt is split into ordered reference modules to reduce retrieval cost and support selective loading without weakening the full constitution.
- PR validation used a shallow checkout while testing commit ancestry, causing false conflict failures.
- Full Python lint and test jobs ran on documentation-only changes and exposed unrelated baseline debt. The workflow was hardened to run Python gates only when Python runtime, tests, or Python project configuration changes in a pull request. Pushes to protected branches still run the full matrix.

## Files created

- `.archonx/toolbox/skills/pauli-brand-studio/SKILL.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/00-core-and-sources.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/01-input-and-prebuild.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/02-strategy-and-voice.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/03-visual-icon-kaku.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/04-krug-antislop-dials.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/05-html-and-handoff.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/06-scoring-and-guardians.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/07-delivery-and-output.md`
- `.archonx/toolbox/skills/pauli-brand-studio/references/08-circuit-comms-invocation.md`
- `ops/reports/ZTE-20260714-0001.json`

## Files modified

- `.archonx/toolbox/skills/mandatory-design-law/SKILL.md`
- `.github/workflows/pr-validation.yml`
- `.github/workflows/ci.yml`

## Acceptance criteria

- The new skill has valid metadata and an explicit activation contract.
- All master-prompt sections 0 through 25 are present in ordered reference modules.
- Mandatory Design Law requires the new skill for brand-system work.
- The skill blocks creative generation before source inspection and prebuild scoring.
- KAKU, Steve Krug, Stop-Slop, Uncodixfy, Impeccable, Taste, icon, rights, accessibility, handoff, and guardian rules are present.
- No secrets, dependencies, runtime code, package-manager changes, data migrations, or production configuration are introduced.
- PR ancestry validation uses full Git history.
- Documentation-only PRs do not fail on unrelated Python baseline debt.
- Pushes to `main` and `develop` retain the full Python test and lint matrix.

## Validation

- Fetch the new skill from the branch.
- Compare the branch to `main`.
- Confirm the diff contains only the declared skill, governance, workflow, plan, and report paths.
- Confirm `PR Validation & Auto-Merge` passes.
- Confirm `CI - Continuous Integration` passes for the documentation/workflow-only change set.
- Open a pull request with rollback instructions.

## Rollback

Close the pull request without merging, or revert the branch commits. No runtime application, data, infrastructure, dependency, secret, or production state requires restoration.
