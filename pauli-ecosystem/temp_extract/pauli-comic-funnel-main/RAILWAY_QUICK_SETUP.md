# 🚀 Railway CLI Quick Setup - 5 Minute Deploy

**Goal:** Get your Pauli Comic Funnel frontend live in 5 minutes  
**Status:** ✅ Ready to go  

---

## Step 1: Install Railway CLI (2 min)

### macOS
```bash
brew install railway
```

### Windows
```powershell
scoop install railway
# OR
choco install railway
```

### Linux / Any OS
```bash
npm install -g @railway/cli
```

**Verify:**
```bash
railway --version
```

---

## Step 2: Login to Railway (1 min)

```bash
railway login
```

This opens a browser window. Sign in with:
- GitHub (recommended)
- Email + password
- Or your preferred method

**Verify:**
```bash
railway whoami
```

---

## Step 3: Link Project (1 min)

```bash
# Navigate to project directory
cd pauli-comic-funnel-main

# Link to Railway project
railway link

# If first time, select "Create new project"
# Project name: pauli-comic-funnel-frontend
# Environment: Production
```

---

## Step 4: Deploy (1 min)

```bash
railway up
```

**What this does:**
- Builds Docker container (multi-stage)
- Installs dependencies
- Builds frontend with Vite
- Serves with Node.js
- Exposes on public Railway domain

**Sits and watches logs automatically.**

---

## Step 5: View Your App! (When deployment completes)

```bash
# Get your deployment URL
railway open

# Or view logs
railway logs -f

# Or check domains
railway domain --list
```

**Result:** Your app is live! 🎉

---

## Quick Command Reference

```bash
# View deployment status
railway status

# See recent logs
railway logs

# Watch live logs
railway logs -f

# Get public URL
railway open

# View environment variables
railway env

# Add environment variable
railway env add KEY=VALUE

# View deployments history
railway deployments

# Rollback to previous deploy
railway rollback <deployment-id>

# View metrics
railway metrics

# Stop deployment
railway down

# Delete project
railway project delete
```

---

## Next Steps After Deploy

### Add Custom Domain
```bash
railway domain --add your-domain.com
# Follow DNS instructions from Railway
```

### Configure CI/CD
```bash
# Enable auto-deploy on GitHub push
# See full DEPLOYMENT.md for GitHub workflow setup
```

### Monitor & Scale
```bash
# View metrics in dashboard
railway metrics

# Scale resources via dashboard
# Settings → Resources → Adjust CPU/Memory
```

### Add Backend (Optional)
If you want to connect the Poly Second Brain backend:
```bash
# In poly-second-brain directory
cd ../poly-second-brain/backend
railway up

# Get backend URL
railway domain --list

# Add to frontend environment
railway env add VITE_API_URL=<backend-url>
```

---

## Troubleshooting

### Deployment stuck?
```bash
# Check logs
railway logs -f

# Look for build errors, fix locally, push
# Then redeploy
railway up
```

### Want to redeploy?
```bash
# Just run again
railway up

# Or push to GitHub if CI enabled
git push origin master
```

### Need to change settings?
```bash
# View/edit in Railway dashboard
# Or use CLI
railway env add/remove KEY

# Then redeploy
railway up
```

---

## 🎉 Done!

Your Pauli Comic Funnel frontend is now live!

- **URL:** Check via `railway open`
- **Status:** Check via `railway status`
- **Logs:** Watch via `railway logs -f`
- **Metrics:** View in Railway dashboard

**Total time:** ~5-10 minutes ⚡

---

Need more details? See `DEPLOYMENT.md` for comprehensive guide.

