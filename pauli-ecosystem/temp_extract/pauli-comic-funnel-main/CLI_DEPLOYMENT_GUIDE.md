# 🖥️ CLI Integration Guide - Pauli Comic Funnel

**Status:** ✅ Ready for CLI deployment  
**Frontend:** React 18.3 + Vite + TypeScript  
**Deployment Platform:** Railway.app  

---

## 🚀 CLI DEPLOYMENT METHODS

### Method 1: Railway CLI (Recommended)

#### Installation
```bash
# Global npm
npm install -g @railway/cli

# macOS with Homebrew
brew install railway

# Windows with Scoop
scoop install railway

# Windows with Choco
choco install railway

# Verify installation
railway --version
```

#### Deployment Steps
```bash
# Step 1: Navigate to project
cd pauli-comic-funnel-main

# Step 2: Login to Railway
railway login
# Opens browser → Sign in with GitHub/Email → Returns to CLI

# Step 3: Link project
railway link
# Choose: Create new project
# Name: pauli-comic-funnel-frontend
# Environment: Production

# Step 4: Deploy
railway up
# Watches logs automatically
# Builds in real-time
# Completes with public URL

# Step 5: Get URL
railway open
# Opens your deployed app in browser!
```

#### Common Commands
```bash
# View deployment status
railway status

# Watch live logs
railway logs -f

# Get public domain
railway domain --list

# Add environment variable
railway env add KEY=VALUE

# Remove environment variable
railway env remove KEY

# View all variables
railway env

# Trigger redeploy
railway up

# View deployment history
railway deployments

# Rollback to previous
railway rollback <deployment-id>

# Stop the app
railway down

# View metrics (CPU, memory, etc)
railway metrics

# SSH into container (advanced)
railway shell
```

---

### Method 2: Docker CLI (Advanced)

If you want to build locally first:

```bash
# Build Docker image locally
docker build -t pauli-comic-funnel:latest .

# Run locally to test
docker run -p 3000:3000 pauli-comic-funnel:latest

# Visit http://localhost:3000 to test

# Push to Railway container registry
docker tag pauli-comic-funnel:latest railway.app/pauli-comic-funnel:latest
docker push railway.app/pauli-comic-funnel:latest

# Then deploy via Railway CLI
railway up
```

---

### Method 3: Git Push Deploy (Automatic)

Set up GitHub Actions:

```bash
# In your repo, Railway auto-detects and deploys on push
# Just push to master
git add .
git commit -m "Update app"
git push origin master

# Railway automatically:
# 1. Detects changes
# 2. Builds Docker image
# 3. Deploys to production
# 4. Updates your domain
```

---

## 🔧 CLI CONFIGURATION

### Global Configuration
```bash
# Set default project
railway project select pauli-comic-funnel-frontend

# Check current project
railway project current

# List all projects
railway project list

# Switch environment
railway env select production
```

### Local .env (Optional)
Create `.env` in project root:
```env
RAILWAY_TOKEN=your_token_here
RAILWAY_PROJECT_ID=your_project_id
RAILWAY_ENVIRONMENT_ID=your_environment_id
```

Then Railway CLI will auto-use these.

---

## 📱 DEPLOYMENT WORKFLOW

### First Deployment
```bash
npm install -g @railway/cli    # Install CLI
railway login                  # Authenticate
cd pauli-comic-funnel-main     # Navigate
railway link                   # Link project
railway up                     # Deploy
railway open                   # View app
```

**Time:** 5 minutes ⚡

### Subsequent Deployments
```bash
# Make changes locally
git add .
git commit -m "Update"
git push origin master

# Auto-deploys OR manual:
railway up

# View progress:
railway logs -f
```

**Time:** 2-3 minutes ⚡

---

## 🎯 TYPICAL WORKFLOW

### Development Loop
```bash
# 1. Make local changes
npm run dev              # Test locally
npm run build           # Build locally

# 2. Commit changes
git add .
git commit -m "Your message"

# 3. Push to GitHub
git push origin master

# 4. Monitor Railway
railway logs -f         # Watch deployment

# 5. Test live
railway open            # Open in browser
```

### Troubleshooting
```bash
# See build logs
railway logs --show-past

# Check recent deployments
railway deployments

# View errors
railway logs | grep -i error

# Full diagnostics
railway logs -f
```

---

## 🌍 DOMAIN MANAGEMENT

### Add Custom Domain
```bash
# List current domains
railway domain --list

# Add new domain
railway domain --add your-domain.com

# Railway provides nameservers
# Update DNS at your registrar
# Takes 24-48 hours to propagate

# Check status
railway domain --list
```

### Remove Domain
```bash
railway domain --remove your-domain.com
```

---

## 🔐 ENVIRONMENT VARIABLES

### Add Variables
```bash
# Single variable
railway env add NODE_ENV=production

# Multiple variables
railway env add \
  VITE_API_URL=https://api.example.com \
  VITE_ENV=production

# With spaces (use quotes)
railway env add LONG_VALUE="This is a long string"
```

### View Variables
```bash
# All variables
railway env

# Specific variable (if viewing plain text)
railway env | grep VITE_API_URL
```

### Remove Variables
```bash
railway env remove NODE_ENV
```

### Update Variables
```bash
# Remove old value
railway env remove OLD_KEY

# Add new value
railway env add NEW_KEY=new_value
```

---

## 📊 MONITORING & DEBUGGING

### Real-Time Logs
```bash
# Latest logs
railway logs -f

# Specific number of lines
railway logs -f --lines 50

# See errors only
railway logs -f | grep -i "error\|warn"

# Export logs
railway logs > build.log
```

### Health Checks
```bash
# View service status
railway status

# Check if service is running
railway status | grep -i "running"

# Restart service
railway up  # Redeploys (same effect)
```

### Resource Usage
```bash
# Real-time metrics
railway metrics

# View in dashboard (prettier)
# Or via: railway metrics --verbose
```

### Deployment History
```bash
# See all deployments
railway deployments

# See recent deployments
railway deployments --limit 10

# Rollback to specific deployment
railway rollback <deployment-id>
```

---

## 🐛 TROUBLESHOOTING CLI

### Issue: "railway: command not found"
**Solution:**
```bash
# Reinstall globally
npm install -g @railway/cli

# Or verify PATH
which railway
npm list -g @railway/cli
```

### Issue: "Authentication failed"
**Solution:**
```bash
# Re-login
railway logout
railway login

# Or check token
railway whoami
```

### Issue: "Cannot link project"
**Solution:**
```bash
# Create project first via dashboard
# Then link
railway link

# Or try explicit project ID
railway link -p project-id
```

### Issue: "Build timeout"
**Solution:**
```bash
# Increase timeout in railway.json
# Or check logs for actual error
railway logs -f

# May be actual build issue (package size, etc)
```

### Issue: "Out of memory during build"
**Solution:**
```bash
# Add memory limit to environment
railway env add NODE_OPTIONS="--max-old-space-size=512"

# Or restart with:
railway up
```

---

## 🔄 CI/CD INTEGRATION

### GitHub Actions
Create `.github/workflows/railway-deploy.yml`:

```yaml
name: Deploy to Railway
on:
  push:
    branches: [master, main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          railway up --force
```

**Setup:**
1. Generate Railway token: https://railway.app/account/tokens
2. Add to GitHub Secrets as `RAILWAY_TOKEN`
3. Push workflow file
4. Auto-deploys on every push!

---

## 📚 CLI REFERENCE

| Command | Purpose | Example |
|---------|---------|---------|
| `railway login` | Authenticate | `railway login` |
| `railway logout` | Sign out | `railway logout` |
| `railway link` | Connect to project | `railway link` |
| `railway up` | Deploy | `railway up` |
| `railway logs` | View logs | `railway logs -f` |
| `railway status` | Check status | `railway status` |
| `railway open` | Open in browser | `railway open` |
| `railway env add` | Add variable | `railway env add KEY=VALUE` |
| `railway env remove` | Remove variable | `railway env remove KEY` |
| `railway domain` | Manage domains | `railway domain --add domain.com` |
| `railway deployments` | View history | `railway deployments` |
| `railway rollback` | Undo deployment | `railway rollback id` |
| `railway metrics` | View resources | `railway metrics` |
| `railway project` | Manage projects | `railway project select` |
| `railway env select` | Switch environment | `railway env select staging` |

---

## ✅ QUICK START CHECKLIST

- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`
- [ ] Navigate: `cd pauli-comic-funnel-main`
- [ ] Link project: `railway link`
- [ ] Deploy: `railway up`
- [ ] Open app: `railway open`
- [ ] Watch logs: `railway logs -f`
- [ ] Test app in browser
- [ ] Add domain (optional): `railway domain --add`
- [ ] Set env vars (optional): `railway env add KEY=VALUE`

---

## 🎉 YOU'RE READY!

Everything is configured. Just run:

```bash
npm install -g @railway/cli
railway login
cd pauli-comic-funnel-main
railway up
```

**Your app will be live in 5 minutes!**

---

## 📖 Related Documentation

- **Full Deploy Guide:** [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Quick Setup:** [RAILWAY_QUICK_SETUP.md](./RAILWAY_QUICK_SETUP.md)
- **Status Report:** [../RAILWAY_DEPLOYMENT_STATUS.md](../RAILWAY_DEPLOYMENT_STATUS.md)
- **Railway Docs:** https://docs.railway.app

