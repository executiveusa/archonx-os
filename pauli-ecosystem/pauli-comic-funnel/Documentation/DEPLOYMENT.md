# 🚀 Railway Deployment Guide - Pauli Comic Funnel Frontend

**Status:** ✅ Ready for immediate deployment  
**Build Time:** ~3-5 minutes  
**Frontend Framework:** React 18.3 + Vite + TypeScript  

---

## 📋 Pre-Deployment Checklist

- ✅ Dockerfile configured (multi-stage build)
- ✅ railway.json configuration created
- ✅ .railwayignore patterns defined
- ✅ Port 3000 exposed and ready
- ✅ Health checks configured
- ✅ Frontend fully built with Vite
- ✅ All dependencies in package.json
- ✅ Environment variables configured

---

## 🚀 Deployment Options

### Option 1: Railway CLI (Recommended - Fastest)

**Prerequisites:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Or via Homebrew (macOS)
brew install railway

# Or via Scoop (Windows)
scoop install railway
```

**Deploy:**
```bash
# Navigate to project
cd pauli-comic-funnel-main

# Login to Railway
railway login

# Link to Railway project (or create new)
railway link

# Deploy
railway up

# View logs
railway logs -f

# Get deployment URL
railway domain
```

**Time:** 2-3 minutes ⚡

---

### Option 2: Railway Web Dashboard (Most User-Friendly)

1. **Visit:** https://railway.app

2. **Sign in** with GitHub/Email

3. **Create new project:**
   - Click "Create New Project"
   - Select "Deploy from GitHub"
   - Connect your GitHub account
   - Select `executiveusa/pauli-comic-funnel` repository

4. **Select branch:** `master` (or `main` if you prefer)

5. **Configure:**
   - Service name: `pauli-comic-funnel-frontend`
   - Build method: `Dockerfile` (auto-detected)
   - Start command: `serve -s dist -l $PORT` (auto-configured)

6. **Add variables:**
   - No environment variables needed for basic deployment
   - Optional: Add `NODE_ENV=production`

7. **Deploy:** Click "Deploy"

8. **Monitor:**
   - Watch deployment progress in real-time
   - View logs in the Logs tab
   - Get your public URL once deployment completes

**Time:** 3-5 minutes via UI ⚙️

---

### Option 3: GitHub Integration (Continuous Deployment)

1. **Connect GitHub to Railway:**
   - Visit Railway Dashboard
   - Go to "Account" → "Integrations"
   - Connect GitHub account

2. **Add GitHub Workflow:**
   ```yaml
   # .github/workflows/railway-deploy.yml
   name: Deploy to Railway
   on:
     push:
       branches: [master, main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Deploy to Railway
           run: |
             npm install -g @railway/cli
             railway up
           env:
             RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
   ```

3. **Set GitHub Secrets:**
   - Get `RAILWAY_TOKEN` from Railway Dashboard
   - Add to GitHub Repository Secrets

4. **Auto-deploy:** Every push to master/main now auto-deploys!

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│      Railway.app (Deployment)           │
├─────────────────────────────────────────┤
│  Docker Container (Node.js 20-Alpine)   │
│  ┌─────────────────────────────────────┐│
│  │  Frontend (React 18.3 + Vite)       ││
│  │  ├── dist/ (built assets)           ││
│  │  ├── Served via `serve` (Node)      ││
│  │  └── Port 3000 (exposed)            ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│  Automatic Health Checks (30s interval) │
│  Auto-restart on failure (max 5 retries)│
└─────────────────────────────────────────┘
        ↓
   Public URL: https://your-app.railway.app
```

---

## ⚙️ Configuration Details

### Dockerfile Strategy
- **Stage 1 (Builder):** Node 20-Alpine, build frontend with `npm run build`
- **Stage 2 (Runtime):** Node 20-Alpine, serve with `serve` package
- **Size:** ~200-300 MB (multi-stage optimization)
- **Build time:** 3-5 minutes (optimized with layer caching)

### Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', ...)"
```
- Ensures app stays healthy
- Auto-restarts if unhealthy
- Configurable via Railway dashboard

### Start Command
```bash
serve -s dist -l 3000
```
- Serves built frontend from `dist/` directory
- Listens on port 3000
- Railway automatically proxies to public domain

---

## 🔧 Environment Variables (Optional)

Add to Railway dashboard or `.env`:

```env
# Frontend (Optional)
VITE_API_URL=https://your-api.railway.app  # If using backend
VITE_ENV=production

# Node
NODE_ENV=production
NODE_OPTIONS=--max_old_space_size=512

# Optional: Analytics, Tracking, etc.
VITE_GA_ID=your-google-analytics-id
VITE_SENTRY_DSN=your-sentry-dsn
```

---

## 📱 Accessing Your Deployed App

**After deployment completes:**

1. **Public URL:** `https://your-project-name.railway.app`
   - Click the "Visit" button in Railway dashboard
   - Or find URL in "Deployments" tab

2. **Custom Domain:**
   ```bash
   railway domain --add
   ```
   - Add your custom domain (e.g., paulieffect.com)
   - Point DNS to Railway nameservers

3. **Monitoring:**
   - View logs: Railway Dashboard → Logs
   - View metrics: Railway Dashboard → Metrics
   - View deployments: Railway Dashboard → Deployments

---

## 🐛 Troubleshooting

### Issue: "Cannot find module 'serve'"
**Solution:** Ensure `serve` is installed in Dockerfile (it is, globally)

### Issue: "Port already in use"
**Solution:** Railway automatically assigns PORT, ensure start command uses `$PORT` environment variable
(Current: uses port 3000, Railway will handle proxying)

### Issue: "Build fails - out of memory"
**Solution:** Add to Railway environment:
```
NODE_OPTIONS=--max_old_space_size=512
```

### Issue: "App keeps restarting"
**Solution:** Check logs for errors:
```bash
railway logs -f
```

### Issue: "Build time too slow"
**Solution:** Current setup is optimized with:
- Multi-stage Docker build
- Node.js 20-Alpine (lightweight)
- npm layer caching

---

## 📊 Performance Metrics

After deployment, monitor:

**Expected Response Times:**
- First load: 200-500ms
- API calls: <100ms
- Static assets: <50ms

**Expected Resource Usage:**
- Memory: 150-300 MB
- CPU: <5% idle, <50% under load
- Disk: ~300 MB (Docker layer)

**Cost:** Free tier supports up to 5GB/month

---

## 🔐 Security

### Current Setup
- ✅ HTTPS auto-enabled (Railway default)
- ✅ Dockerfile best practices (Alpine, multi-stage)
- ✅ Node.js production mode enabled
- ✅ Health checks prevent zombie processes

### Additional Hardening (Optional)
```bash
# Add rate limiting middleware in src/App.tsx or create API proxy
# Add CORS headers for API security
# Add CSP headers for XSS protection
# Add security headers via Railway middleware
```

---

## 🔄 Updating Deployments

### Via CLI
```bash
# Make changes locally
git add .
git commit -m "Update: frontend changes"
git push origin master

# Redeploy
railway up
```

### Via Dashboard
```
1. Go to Deployments tab
2. Click "Redeploy"
3. Or push to GitHub and it auto-redeploys (if CI enabled)
```

### Rollback
```bash
# Via CLI
railway logs --show-past

# Via Dashboard
1. Deployments tab
2. Select previous deployment
3. Click "Redeploy"
```

---

## 📚 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **Vite Build Guide:** https://vitejs.dev/guide/build.html
- **Docker Best Practices:** https://docs.docker.com/develop/dev-best-practices/
- **Node.js Performance:** https://nodejs.org/en/docs/guides/simple-profiling/

---

## ✅ Deployment Checklist (One Final Time)

- [ ] Code committed to GitHub
- [ ] All dependencies in package.json
- [ ] Environment variables configured
- [ ] Dockerfile exists and is correct
- [ ] railway.json configured
- [ ] Health checks enabled
- [ ] Node.js version compatible (20+)
- [ ] npm scripts working locally (`npm run build`, `npm run dev`)
- [ ] No hardcoded local paths
- [ ] No sensitive data in environment

---

## 🎉 Ready to Deploy!

**Choose your deployment method above and get your frontend live in minutes!**

**Expected Result:**
- ✅ Frontend accessible at: `https://your-app.railway.app`
- ✅ React app fully functional
- ✅ All routes working (powered by React Router)
- ✅ Styling applied (Tailwind CSS)
- ✅ Components rendering (shadcn/ui)
- ✅ Auto-restarts on failure
- ✅ Health checks monitoring

**Questions?** Check Railway dashboard logs or refer to troubleshooting section above.

---

**Deployment Status:** 🟢 **READY TO DEPLOY**

