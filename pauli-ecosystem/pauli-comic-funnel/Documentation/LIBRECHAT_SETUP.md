# LibreChat Integration for Pauli Effect (Internal Team Use Only)

## 🔒 Overview

LibreChat is configured for **internal team use only** to control the Pauli Agent UI system and AGI Open automation. This provides a secure, team-only interface for AI-powered development workflows.

## 🎯 Purpose

- Internal-facing chat interface for team
- Control Pauli Agent UI (CopilotKit) for frontend generation
- Execute AGI Open Lux automation tasks
- Monitor and manage AI agent activities
- Secure, authenticated access only

## 🔐 Authentication & Access Control

### Team-Only Access

```bash
# Environment Configuration
LIBRECHAT_ENABLED=true
LIBRECHAT_AUTH_SECRET=your_secure_secret_here
LIBRECHAT_TEAM_EMAILS=team@paulieffect.com,dev@paulieffect.com,admin@paulieffect.com
```

### Access Restrictions

- ✅ Only whitelisted team emails can access
- ✅ Session-based authentication required
- ✅ IP whitelist (optional, configure as needed)
- ❌ No public access allowed
- ❌ No external API exposure

## 📦 Installation (Docker-based)

### Prerequisites

- Docker & Docker Compose installed
- `.env` configured with required keys
- Team email whitelist configured

### Quick Setup

```bash
# Clone LibreChat
git clone https://github.com/danny-avila/LibreChat.git librechat
cd librechat

# Copy our custom configuration
cp ../librechat.config.yaml .

# Set up environment
cp .env.example .env
# Edit .env with Pauli Effect credentials

# Start LibreChat
docker-compose up -d
```

### Configuration File

```yaml
# librechat.config.yaml
version: 1.0.0

endpoints:
  custom:
    - name: "Pauli Agent UI"
      apiKey: "${COPILOTKIT_API_KEY}"
      baseURL: "http://host.docker.internal:3001/api/copilotkit"
      models:
        default: ["pauli-agent-ui"]
      titleConvo: true
      titleModel: "pauli-agent-ui"

    - name: "AGI Open Lux"
      apiKey: "${AGI_OPEN_API_KEY}"
      baseURL: "http://host.docker.internal:3001/api/agi-open"
      models:
        default: ["lux-actor", "lux-thinker", "lux-tasker"]
      titleConvo: true

interface:
  privacyPolicy:
    externalUrl: "https://paulieffect.com/privacy"
  termsOfService:
    externalUrl: "https://paulieffect.com/terms"

registration:
  socialLogins: []
  allowedDomains: ["paulieffect.com"]

fileConfig:
  endpoints:
    assistants:
      fileLimit: 10
      fileSizeLimit: 10
    default:
      totalSizeLimit: 50

rateLimits:
  fileUploads:
    ipMax: 50
    ipWindowInMinutes: 60
  conversationsImport:
    ipMax: 10
    ipWindowInMinutes: 60
```

## 🎮 Usage - Chat Commands

### Pauli Agent UI Commands

```bash
# Generate UI Component
/ui Create a user profile card with avatar, name, bio, and social links

# Generate Form
/form Build a contact form with validation

# Generate Dashboard
/dashboard Create a metrics dashboard with charts
```

### AGI Open Automation Commands

```bash
# Execute Quick Task (Actor Mode)
/automate Take a screenshot of the current page

# Plan Complex Workflow (Thinker Mode)
/plan Update all package dependencies and run tests

# Execute Scripted Task (Tasker Mode)
/task Run the deployment checklist step by step
```

### System Commands

```bash
# Check System Health
/health

# List Active Tasks
/tasks

# Get Task Status
/status <task-id>
```

## 🔧 Backend Integration

### API Proxy Configuration

LibreChat proxies to our internal APIs:

- **Pauli Agent UI**: `http://localhost:3001/api/copilotkit`
- **AGI Open**: `http://localhost:3001/api/agi-open`
- **Health Check**: `http://localhost:3001/api/health`

### Authentication Flow

1. User authenticates with team email
2. LibreChat validates against whitelist
3. Session created with secure token
4. All API calls include team authentication
5. Requests logged for audit trail

## 📊 Monitoring & Logging

### Activity Logging

All LibreChat interactions are logged:

```typescript
{
  timestamp: "2025-12-31T15:00:00.000Z",
  user: "developer@paulieffect.com",
  action: "ui_generation",
  endpoint: "/api/copilotkit/a2ui",
  prompt: "Create a login form",
  result: "success",
  taskId: "task-123456"
}
```

### Audit Trail

- Who used which AI features
- What UIs were generated
- Which automations were executed
- Performance metrics per user
- Cost tracking per operation

## 🚀 Deployment

### Development

```bash
# Local development with hot reload
npm run dev

# Access at http://localhost:3000
```

### Production (Internal Server)

```bash
# Build for production
docker-compose -f docker-compose.prod.yml up -d

# Behind internal VPN/firewall
# HTTPS with internal certificates
# Only accessible on company network
```

### Security Checklist

- [ ] Environment variables configured
- [ ] Team email whitelist updated
- [ ] Auth secret is strong (32+ characters)
- [ ] HTTPS enabled in production
- [ ] VPN/firewall configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Backup strategy in place

## 💡 Best Practices

### For Team Members

1. **Use Descriptive Prompts**
   - "Create a signup form with email validation"
   - NOT: "make form"

2. **Specify Context**
   - "Build dashboard for user analytics with charts"
   - NOT: "dashboard"

3. **Review Generated Code**
   - Always review A2UI output
   - Test components before deployment

4. **Use Appropriate Modes**
   - Simple tasks: Use Actor mode
   - Complex workflows: Use Thinker mode
   - Scripted sequences: Use Tasker mode

### For Administrators

1. **Regular Updates**
   - Keep LibreChat updated
   - Update team email whitelist
   - Rotate auth secrets quarterly

2. **Monitor Usage**
   - Review logs weekly
   - Check cost metrics
   - Monitor error rates

3. **Security Audits**
   - Quarterly security reviews
   - Access audit logs
   - Update dependencies

## 🔗 Integration Architecture

```
┌─────────────────────────────────────────┐
│           LibreChat                      │
│      (Internal Team Interface)           │
│                                          │
│  Authentication & Session Management     │
└──────────────┬───────────────────────────┘
               │
               │ HTTPS (Internal Network)
               │
┌──────────────▼───────────────────────────┐
│      Pauli Effect Backend API            │
│                                          │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Pauli Agent  │  │   AGI Open      │ │
│  │ UI (CopilotKit)│  │   (Lux)         │ │
│  └──────────────┘  └─────────────────┘ │
└──────────────────────────────────────────┘
```

## 📝 Notes

- **Not Public**: LibreChat is internal only
- **Team Access**: Whitelist-based authentication
- **Secure**: All traffic on internal network
- **Monitored**: Full audit logging enabled
- **Integrated**: Connected to Pauli Agent UI + AGI Open

## 🆘 Support

### Common Issues

**Issue**: Can't access LibreChat
- **Solution**: Check VPN connection and email whitelist

**Issue**: UI generation not working
- **Solution**: Verify COPILOTKIT_API_KEY in .env

**Issue**: Automation failing
- **Solution**: Check AGI_OPEN_API_KEY and endpoint configuration

### Getting Help

- Check logs: `docker-compose logs -f`
- Review health: `http://localhost:3001/api/health`
- Contact team lead for access issues

---

**Status**: Configuration documented, ready for deployment
**Access**: Internal team only
**Updated**: 2025-12-31
