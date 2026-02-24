# PAULI Deployment Guide - One-Click Automation

## ✅ Setup Complete!

Your PAULI platform can now be deployed with **ONE CLICK** from VS Code. No manual steps required.

## 🚀 Quick Deployment Options

### Option 1: Full Pipeline (Recommended)
**Commit → Push to GitHub → Deploy to Coolify**

Press `Ctrl+Shift+B` (Open Tasks) and select:
```
✅ Full Pipeline: Commit → Push → Deploy
```

This will:
1. Stage all changes
2. Commit to git
3. Push to GitHub (auto-syncs Lovable)
4. Deploy to Coolify on Hostinger VPS

---

### Option 2: Deploy Only
If you've already pushed changes to GitHub:

Press `Ctrl+Shift+B` and select:
```
🚀 Deploy to Coolify (One-Click)
```

This directly triggers deployment to your VPS.

---

### Option 3: Manual Git Operations
**Commit & Push** (without deploying):

Press `Ctrl+Shift+B` and select:
```
📝 Commit & Push to GitHub
```

---

## 🔗 Quick Links

Press `Ctrl+Shift+B` and select any of:
- `🌐 Open Lovable Preview` - https://pauli-comic-funnel.lovable.app
- `🔄 Open Live App (Coolify)` - https://srv1099662.hstgr.cloud
- `🔗 Open Coolify Dashboard` - https://srv1099662.hstgr.cloud (admin)

---

## ⚙️ Deployment Configuration

**Infrastructure:**
- Hosting: Coolify on Hostinger VPS
- Domain: https://srv1099662.hstgr.cloud
- Server: root@31.220.58.212 (SSH)

**Deployment Automation:**
- Script: `scripts/deploy-coolify.ps1`
- Trigger: Coolify API with bearer token
- Environment: 12 variables (API keys, Supabase, Stripe) auto-configured

**Repository Integration:**
- GitHub: https://github.com/executiveusa/pauli-comic-funnel
- Branch: `main` (auto-syncs to Lovable)
- Last commit: `src/App.tsx` formatting normalized

---

## 📊 Environment Variables Configured

✅ ANTHROPIC_API_KEY
✅ OPENAI_API_KEY
✅ GOOGLE_API_KEY
✅ NEXT_PUBLIC_SUPABASE_URL
✅ NEXT_PUBLIC_SUPABASE_ANON_KEY
✅ SUPABASE_SERVICE_ROLE_KEY
✅ GH_PAT (GitHub token)
✅ NEXT_PUBLIC_BASE_URL
✅ NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
✅ STRIPE_SECRET_KEY
✅ NODE_ENV (production)
✅ NEXT_PUBLIC_API_BASE_URL

---

## 🔍 How It Works

1. **Local Development**: Edit files in VS Code
2. **One-Click Deploy**: 
   - `Ctrl+Shift+B` → Select task
   - Changes are committed, pushed, and deployed automatically
3. **Live Updates**:
   - Lovable syncs automatically from GitHub (within seconds)
   - Coolify deploys your app (2-5 minutes)
   - Both update simultaneously

---

## ✨ You're all set!

No more manual deployments. Just code, save, and hit the deploy button.

Happy coding! 🎉
