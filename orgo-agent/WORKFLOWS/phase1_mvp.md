# Phase 1: MVP Development Workflow

## Objective

Build and deploy the minimum viable product for the Luxury Travel Directory with AI enhancements.

## Timeline

**Start:** Immediate
**Duration:** 2-4 weeks
**Deployment Target:** Vercel (Free Tier)

## Prerequisites

- [x] Orgo sandbox environment initialized
- [x] Agent identities created
- [x] Environment variables configured
- [x] Repositories cloned

## Task Breakdown

### Week 1: Foundation

#### Day 1-2: Project Setup
- [ ] **ARIA**: Initialize Next.js 13 project with App Router
- [ ] **ARIA**: Configure Shadcn UI and Tailwind CSS
- [ ] **CIPHER**: Setup Supabase connection and authentication
- [ ] **VECTOR**: Configure Vercel project and deployment pipeline

```bash
# Initialize project
npx create-next-app@latest luxury-travel-directory --typescript --tailwind --app
cd luxury-travel-directory
npx shadcn-ui@latest init
```

#### Day 3-4: Database Schema
- [ ] **ARIA**: Design database schema for listings
- [ ] **CIPHER**: Create Supabase migrations
- [ ] **CIPHER**: Setup Row Level Security (RLS)

```sql
-- Core tables
CREATE TABLE listings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  category TEXT,
  location TEXT,
  coordinates POINT,
  website_url TEXT,
  phone TEXT,
  email TEXT,
  images TEXT[],
  amenities TEXT[],
  rating DECIMAL(2,1),
  price_range TEXT,
  languages TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT,
  email TEXT,
  phone TEXT,
  source TEXT,
  interest TEXT,
  status TEXT DEFAULT 'new',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE agent_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_name TEXT,
  task TEXT,
  status TEXT,
  result JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Day 5-7: Core Features
- [ ] **SYNTHIA**: Build listing CRUD operations
- [ ] **SYNTHIA**: Create directory browse page
- [ ] **PRISM**: Implement multi-language support (EN/ES/FR)
- [ ] **PHANTOM**: Setup Firecrawl integration for content extraction

### Week 2: AI Integration

#### Day 8-10: BFF Architecture
- [ ] **ARIA**: Design BFF API endpoints
- [ ] **NEXUS**: Implement context injection system
- [ ] **CIPHER**: Setup secure vault for API keys
- [ ] **SYNTHIA**: Build AI chat endpoint

```typescript
// BFF API Structure
// /api/bff/
// ├── chat.ts          - AI conversation endpoint
// ├── listings.ts      - Directory operations
// ├── leads.ts         - Lead management
// ├── voice.ts         - Voice AI integration
// └── context.ts       - Context injection
```

#### Day 11-12: AI Concierge
- [ ] **SYNTHIA**: Implement AI chatbot component
- [ ] **SYNTHIA**: Connect to Claude API via BFF
- [ ] **ORACLE**: Setup conversation logging
- [ ] **PRISM**: Create prompt templates for travel concierge

```typescript
// AI Concierge System Prompt
const CONCIERGE_PROMPT = `
You are a luxury travel concierge for Puerto Vallarta and Mexico City.
Your role is to help visitors discover the best experiences, restaurants,
hotels, and activities. Be knowledgeable, friendly, and helpful.

Available tools:
- search_listings: Search the directory for businesses
- get_details: Get detailed information about a listing
- check_availability: Check availability for bookings
- make_recommendation: Provide personalized recommendations

Always maintain a professional yet warm tone.
Respond in the user's preferred language (English, Spanish, or French).
`;
```

#### Day 13-14: Voice Integration
- [ ] **ECHO**: Setup Twilio phone number
- [ ] **ECHO**: Implement voice webhook handlers
- [ ] **ECHO**: Connect Whisper for transcription
- [ ] **ECHO**: Setup text-to-speech response

### Week 3: Content & Polish

#### Day 15-17: Content Population
- [ ] **PHANTOM**: Scrape top 100 luxury businesses in PV/CDMX
- [ ] **PRISM**: Generate AI descriptions for each listing
- [ ] **NOVA**: Create placeholder images where needed
- [ ] **ATLAS**: Add geolocation data

```bash
# Content enrichment pipeline
node scripts/enrich-listings.js \
  --source apollo \
  --categories "hotels,restaurants,spas,tours" \
  --locations "Puerto Vallarta,Mexico City" \
  --output ./data/listings.json
```

#### Day 18-19: UI Polish
- [ ] **SYNTHIA**: Implement responsive design
- [ ] **SYNTHIA**: Add dark mode support
- [ ] **PRISM**: Create marketing landing page
- [ ] **VECTOR**: Optimize for performance (Lighthouse >90)

#### Day 20-21: Testing & Deployment
- [ ] **ORACLE**: Write integration tests
- [ ] **VECTOR**: Deploy to Vercel
- [ ] **CIPHER**: Setup monitoring and alerts
- [ ] **NEXUS**: Create status dashboard

## Deployment Checklist

### Pre-Deployment
- [ ] All environment variables configured
- [ ] Database migrations run
- [ ] API endpoints tested
- [ ] Voice integration verified
- [ ] Multi-language working

### Vercel Deployment
```bash
# Deploy to Vercel
vercel --prod

# Set environment variables
vercel env add ANTHROPIC_API_KEY
vercel env add OPENAI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add TWILIO_ACCOUNT_SID
vercel env add TWILIO_SECRET
```

### Post-Deployment
- [ ] Verify site loads correctly
- [ ] Test AI chat functionality
- [ ] Test voice call handling
- [ ] Verify lead capture
- [ ] Check analytics tracking

## Success Metrics

| Metric | Target |
|--------|--------|
| Page Load Time | < 3 seconds |
| Lighthouse Score | > 90 |
| AI Response Time | < 5 seconds |
| Voice Response Time | < 3 seconds |
| Uptime | 99.9% |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limits | Implement caching and rate limiting |
| High AI costs | Set token budgets and monitoring |
| Voice quality issues | Test multiple TTS providers |
| Scraping blocks | Use rotating proxies and delays |

## Next Phase

After MVP is deployed and stable:
1. Monitor usage signals
2. Gather user feedback
3. Optimize high-traffic features
4. Begin Phase 2: Signal Gathering
