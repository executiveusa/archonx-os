# Security Policy

ArchonX OS enforces deny-by-default privileged actions using Access Kernel grants and Gastown work item IDs.

Report vulnerabilities through private maintainers channels; do not open public exploit issues.

## ⚠️ HISTORY CLEANUP REQUIRED — BEAD-MASTER-002

Plaintext credentials were previously committed to this repository.
After this PR merges, the repo owner MUST:

1. **Rotate ALL affected credentials immediately:**
   - GitHub PAT (github.com/settings/tokens)
   - MongoDB URI password (MongoDB Atlas dashboard)
   - Supabase service role key (Supabase dashboard → Settings → API)
   - Anthropic API key (console.anthropic.com → API Keys)
   - Stripe keys (dashboard.stripe.com → Developers)
   - Twilio keys (console.twilio.com → API Keys)

2. **Purge git history with BFG:**
   ```bash
   bfg --replace-text path/to/secrets.txt archonx-os.git
   git push --force
   ```

3. **Update all deployment environments** (Coolify, Vercel, Railway) with new keys.
