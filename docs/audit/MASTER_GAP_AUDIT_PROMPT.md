# MASTER GAP AUDIT PROMPT

You are performing a full ecosystem audit.

Your job is to:

1. Enumerate all repositories connected to this GitHub agent.
2. Clone and index each repository.
3. Extract the following from each:
   - Presence of OpenClaw fork
   - Presence of VisionClaw
   - Presence of Toolbox.md
   - Presence of LLM.txt
   - Presence of SSO logic
   - Presence of secrets vault integration
   - Presence of webhook back to Archon X
   - Presence of cron jobs
   - Presence of agent subagent definitions
   - Presence of security monitoring
   - Presence of media stack integration (Remotion, Stable Audio, StoryToolkit, Blender)
   - Presence of repo identity file
   - Presence of ecosystem registration file
4. Generate a structured report:
   - SECTION A: Fully implemented components
   - SECTION B: Partially implemented components
   - SECTION C: Missing components
   - SECTION D: Misaligned implementations
   - SECTION E: Security gaps
   - SECTION F: Agent architecture gaps
   - SECTION G: Media stack gaps
   - SECTION H: SSO and auth gaps
5. Compare all findings against `docs/audit/required_architecture_spec.json`.
6. Produce a delta table:

   | Component | Intended | Actual | Status | Required Fix |

7. For every missing component, generate:
   - Required files
   - Required folder structure
   - Required dependency changes
   - Required CI/CD updates
   - Required environment variable changes
8. Do not stop early.
9. Do not summarize.
10. Be exhaustive.
11. Output must exceed 2000 words minimum.
12. Flag all critical missing security features.
13. Identify architectural contradictions.
14. Identify redundant repos.
15. Identify repos that should be merged.

End with:

**PRIORITY REMEDIATION ORDER (High → Medium → Low)**
