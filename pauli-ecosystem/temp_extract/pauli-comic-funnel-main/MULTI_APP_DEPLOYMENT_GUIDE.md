# PAULI Multi-App Deployment System
## Self-Hosted Coolify Infrastructure for 200+ Apps

---

## 🎯 Overview

This system automates deployment of **all 95+ apps** from your GitHub organization to a self-hosted Coolify instance. Eliminates GoDaddy and external hosting dependencies. Complete infrastructure as code.

**Key Features:**
- ✅ **Centralized secrets management** - Single source of truth for all API keys
- ✅ **Automatic discovery** - Scans GitHub org and finds all repos
- ✅ **Bulk deployment** - Create services for all apps with one command
- ✅ **GitHub integration** - Auto-deploy on push via webhooks
- ✅ **Secrets sync** - Propagate changes to all services instantly
- ✅ **Self-hosted** - 100% control over infrastructure (no GoDaddy/external deps)

---

## 📋 Quick Start

### 1️⃣ Initial Setup
```powershell
cd pauli-comic-funnel-main
.\scripts\coolify-multi-app-manager.ps1 -Action setup
```

This creates:
- `config/secrets.json` - Central secrets vault
- `config/app-inventory.json` - Tracks all apps

### 2️⃣ Edit Secrets
```powershell
# Edit config/secrets.json with your actual API keys
# Add all keys that should be available to every app
notepad config\secrets.json
```

### 3️⃣ Scan GitHub Organization
```powershell
.\scripts\coolify-multi-app-manager.ps1 -Action scan
```

This:
- Finds all 95+ repos in `executiveusa` org
- Saves repo list to `config/repos.json`
- Displays summary

### 4️⃣ Create Services in Coolify
```powershell
.\scripts\coolify-multi-app-manager.ps1 -Action create-all
```

This:
- Creates a Coolify service for each GitHub repo
- Configures auto-deployment on push
- Sets up webhooks
- Saves inventory to `config/app-inventory.json`

### 5️⃣ Sync Secrets to All Services
```powershell
.\scripts\coolify-multi-app-manager.ps1 -Action sync-secrets
```

This:
- Applies all secrets from `config/secrets.json` to every service
- Happens in seconds (bulk update)

### 6️⃣ Deploy All Apps
```powershell
.\scripts\coolify-multi-app-manager.ps1 -Action deploy-all
```

This:
- Triggers deployment for all services
- Takes 2-5 minutes per app (runs in parallel)

---

## 🔄 Ongoing Workflow

### Daily Development
```
1. Code locally in VS Code
2. Push to GitHub (main branch)
3. GitHub webhook → Coolify auto-deploys
4. App updated at https://[app-name].srv1099662.hstgr.cloud
```

### Adding a New Secret
```powershell
# 1. Edit config/secrets.json
notepad config\secrets.json

# 2. Sync to all services
.\scripts\coolify-multi-app-manager.ps1 -Action sync-secrets

# 3. All 95+ apps now have access to the new secret
```

### Checking Status
```powershell
.\scripts\coolify-multi-app-manager.ps1 -Action status
```

---

## 📁 Configuration Files

### `config/secrets.json`
Central vault containing all environment variables and API keys.

```json
{
  "ANTHROPIC_API_KEY": "sk-ant-...",
  "OPENAI_API_KEY": "sk-proj-...",
  "STRIPE_SECRET_KEY": "sk_live_...",
  "DATABASE_URL": "postgresql://...",
  "NODE_ENV": "production",
  "_COMMENT": "Add config/secrets.json to .gitignore - never commit secrets!"
}
```

**Important:** Add `config/secrets.json` to `.gitignore`

### `config/app-inventory.json`
Track of all deployed apps, their service IDs, and deployment status.

```json
{
  "timestamp": "2025-01-03T...",
  "total_apps": 95,
  "apps": [
    {
      "name": "pauli-comic-funnel",
      "repo_url": "https://github.com/executiveusa/pauli-comic-funnel",
      "service_id": "service-...",
      "status": "deployed"
    }
  ]
}
```

### `config/repos.json`
Raw GitHub API response with all repos in org. Used for reference.

---

## 🚀 Available Commands

```powershell
# Setup initial configuration
.\scripts\coolify-multi-app-manager.ps1 -Action setup

# Scan GitHub org for repos
.\scripts\coolify-multi-app-manager.ps1 -Action scan

# Create Coolify services for all apps
.\scripts\coolify-multi-app-manager.ps1 -Action create-all

# Trigger deployment for all services
.\scripts\coolify-multi-app-manager.ps1 -Action deploy-all

# Update environment variables across all services
.\scripts\coolify-multi-app-manager.ps1 -Action sync-secrets

# Show deployment status
.\scripts\coolify-multi-app-manager.ps1 -Action status
```

---

## 🔗 Infrastructure Architecture

```
GitHub Organization (executiveusa)
├── 95+ repositories
└── Each repo has:
    ├── Auto-push webhook → Coolify
    ├── GitHub Actions (optional)
    └── Auto-deploy on main branch

                    ↓

Coolify Control Plane (https://srv1099662.hstgr.cloud)
├── 95+ services (one per app)
├── Shared secrets vault (centralized)
├── Auto-deployment on webhook
├── Build & containerization
└── Domain management

                    ↓

Self-Hosted VPS (Hostinger)
├── Coolify containers (main platform)
├── Redis (cache/queue)
├── PostgreSQL (database)
├── Nginx proxy
└── SSL certificates (auto-managed)

                    ↓

Live Applications
├── https://[app-name].srv1099662.hstgr.cloud
├── 95+ independent apps
├── Shared secrets & configs
└── All self-hosted (no external deps)
```

---

## 🔐 Secrets Management Best Practices

### ✅ DO:
- Keep secrets in `config/secrets.json` (not in git)
- Use strong API keys
- Rotate secrets periodically
- Limit secret access by app (if needed)
- Back up secrets vault

### ❌ DON'T:
- Commit `config/secrets.json` to git
- Hardcode secrets in code
- Reuse secrets across environments
- Share secrets in plain text
- Keep outdated API keys

### Rotating a Secret
```powershell
# 1. Update in config/secrets.json
# 2. Save file
# 3. Run sync
.\scripts\coolify-multi-app-manager.ps1 -Action sync-secrets
# 4. All apps get new secret instantly
```

---

## 📊 Monitoring & Maintenance

### View Coolify Dashboard
```
https://srv1099662.hstgr.cloud
Username: admin@example.com
```

### Check Individual App
```
https://[app-name].srv1099662.hstgr.cloud
```

### View Deployment Logs
In Coolify dashboard → Services → [App Name] → Logs

### SSH to VPS (if needed)
```powershell
ssh root@31.220.58.212
docker ps  # View all containers
```

---

## 🛠️ Customization

### App-Specific Configuration
If an app needs custom environment variables:

```json
{
  "pauli-comic-funnel_ENV": "{\"CUSTOM_VAR\": \"value\"}",
  ...
}
```

The system will merge app-specific vars with global vars.

### Custom Domains
Edit domain in Coolify dashboard for each app:
```
App Name: my-app
Domain: my-app.example.com  (instead of my-app.srv1099662.hstgr.cloud)
```

### Different Deployment Branches
Edit in Coolify service settings:
```
Branch: staging  (instead of main)
```

---

## ❓ Troubleshooting

**Q: App not deploying?**
A: Check Coolify logs → Services → [App] → Logs. Look for build errors.

**Q: Secret not updating?**
A: Run `sync-secrets` again. Check if variable name matches app code.

**Q: App accessible via HTTPS?**
A: Coolify auto-manages SSL. Check certificate status in dashboard.

**Q: How to delete an app?**
A: Coolify dashboard → Services → [App] → Delete. This removes the service but not the GitHub repo.

**Q: Scale to more apps?**
A: VPS has capacity for 200-300 lightweight apps. If reaching limits, add another VPS and create a second Coolify instance.

---

## 📈 Going Deeper

### Python Version (Advanced)
For more control, use the Python version:

```powershell
python scripts/coolify-multi-app-manager.py
```

Features:
- Custom app configurations
- Advanced filtering
- API-level control
- Scripting integration

### GitHub Actions CI/CD
Automatic deployment on every push:

```yaml
# .github/workflows/coolify-deploy.yml
on:
  push:
    branches: [main]
```

Coolify webhook URL is auto-configured.

---

## 🎯 Success Metrics

After setup, you should have:

✅ **95+ apps deployed** in Coolify
✅ **Zero external hosting** (no GoDaddy)
✅ **Centralized secrets** (single config file)
✅ **Auto-deployment** (push to GitHub → live in 2-5 min)
✅ **Self-hosted infrastructure** (full control)
✅ **Single dashboard** (manage all from Coolify)
✅ **Reduced costs** (one VPS vs multiple hosting services)

---

## 📞 Getting Help

For issues:
1. Check status: `.\scripts\coolify-multi-app-manager.ps1 -Action status`
2. View logs in Coolify dashboard
3. Check GitHub webhook delivery (repo settings → webhooks)
4. Verify secrets in `config/secrets.json`
5. Review network connectivity to `srv1099662.hstgr.cloud`

---

**Version:** 1.0  
**Updated:** January 3, 2025  
**Coolify Instance:** https://srv1099662.hstgr.cloud  
**VPS:** srv1099662.hstgr.cloud (Hostinger)
