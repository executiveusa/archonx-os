# Tool Configurations

## Overview

This document provides configuration details for all external tools and services used by the Autonomous AI Agency Platform.

---

## 1. Apollo.io (Lead Scraping)

### Purpose
B2B lead generation and contact data extraction.

### Configuration
```json
{
  "apollo": {
    "api_endpoint": "https://api.apollo.io/v1",
    "rate_limit": "100 requests/minute",
    "search_types": [
      "people",
      "organizations",
      "mixed"
    ],
    "filters": {
      "person_titles": [
        "Owner",
        "Marketing Director",
        "General Manager"
      ],
      "organization_locations": [
        "Puerto Vallarta, Jalisco, Mexico",
        "Mexico City, CDMX, Mexico"
      ],
      "organization_industries": [
        "Hospitality",
        "Travel & Tourism",
        "Restaurants",
        "Real Estate"
      ]
    }
  }
}
```

### Usage via Apify
```javascript
// Apify Apollo Scraper
const apify = require('apify-client');

const client = new ApifyClient({
  token: process.env.APIFY_TOKEN
});

const run = await client.actor('apify/apollo-scraper').call({
  searchQueries: ['luxury hotels Puerto Vallarta'],
  maxResults: 100
});
```

---

## 2. Firecrawl (Web Scraping)

### Purpose
Convert websites into structured data for AI processing.

### Configuration
```json
{
  "firecrawl": {
    "api_endpoint": "https://api.firecrawl.dev/v1",
    "output_formats": ["markdown", "json"],
    "max_depth": 3,
    "timeout": 30000,
    "features": {
      "extract_main_content": true,
      "remove_boilerplate": true,
      "include_links": true,
      "include_images": false
    }
  }
}
```

### Usage Example
```typescript
// Firecrawl integration
import Firecrawl from '@mendable/firecrawl-js';

const firecrawl = new Firecrawl({
  apiKey: process.env.FIRECRAWL_API_KEY
});

// Scrape single URL
const result = await firecrawl.scrapeUrl('https://example-hotel.com', {
  formats: ['markdown', 'json']
});

// Crawl entire domain
const crawlResult = await firecrawl.crawlUrl('https://example-hotel.com', {
  limit: 50,
  scrapeOptions: {
    formats: ['markdown']
  }
});
```

---

## 3. Twilio (Voice AI)

### Purpose
Phone call handling for AI voice agents.

### Configuration
```json
{
  "twilio": {
    "account_sid": "${TWILIO_ACCOUNT_SID}",
    "phone_numbers": [
      "+52 322 XXX XXXX (Puerto Vallarta)",
      "+52 55 XXXX XXXX (Mexico City)"
    ],
    "voice_settings": {
      "language": "es-MX",
      "voice": "Polly.Lupe-Neural",
      "rate": "1.0",
      "pitch": "0%"
    },
    "webhooks": {
      "voice_url": "/api/voice/incoming",
      "status_callback": "/api/voice/status"
    }
  }
}
```

### Voice Agent Implementation
```typescript
// Twilio Voice Handler
import twilio from 'twilio';

const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_SECRET
);

// Handle incoming call
export async function handleIncomingCall(req: Request) {
  const twiml = new twilio.twiml.VoiceResponse();
  
  // Gather speech
  const gather = twiml.gather({
    input: ['speech'],
    action: '/api/voice/process',
    speechTimeout: 'auto',
    language: 'es-MX'
  });
  
  gather.say({
    voice: 'Polly.Lupe-Neural',
    language: 'es-MX'
  }, 'Hola, soy su asistente de viajes. ¿En qué puedo ayudarle?');
  
  return new Response(twiml.toString(), {
    headers: { 'Content-Type': 'text/xml' }
  });
}

// Process speech with AI
export async function processSpeech(req: Request) {
  const formData = await req.formData();
  const speechResult = formData.get('SpeechResult');
  
  // Send to AI for processing
  const aiResponse = await processWithAI(speechResult);
  
  const twiml = new twilio.twiml.VoiceResponse();
  twiml.say({
    voice: 'Polly.Lupe-Neural',
    language: 'es-MX'
  }, aiResponse);
  
  return new Response(twiml.toString(), {
    headers: { 'Content-Type': 'text/xml' }
  });
}
```

---

## 4. Open Hands (Autonomous Coding)

### Purpose
Autonomous code generation and task execution.

### Configuration
```json
{
  "open_hands": {
    "api_endpoint": "https://api.openhands.ai/v1",
    "api_keys": [
      "${OPEN_HANDS_API_KEY}",
      "${OPEN_HANDS_API_KEY_2}"
    ],
    "default_model": "claude-sonnet-4",
    "max_iterations": 100,
    "workspace": "/workspace",
    "capabilities": [
      "code_generation",
      "file_editing",
      "terminal_access",
      "web_browsing"
    ]
  }
}
```

### Usage Example
```python
# Open Hands API client
import requests

def create_task(prompt: str, workspace: str):
    response = requests.post(
        "https://api.openhands.ai/v1/tasks",
        headers={
            "Authorization": f"Bearer {OPEN_HANDS_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "prompt": prompt,
            "workspace": workspace,
            "model": "claude-sonnet-4"
        }
    )
    return response.json()

# Create autonomous coding task
task = create_task(
    prompt="Create a Next.js page for listing luxury hotels with filtering",
    workspace="/workspace/luxury-travel-directory"
)
```

---

## 5. Supabase (Database)

### Purpose
PostgreSQL database with built-in auth and real-time features.

### Configuration
```json
{
  "supabase": {
    "project_id": "${SUPABASE_PROJECT_ID}",
    "url": "${SUPABASE_URL}",
    "anon_key": "${SUPABASE_ANON_KEY}",
    "features": {
      "auth": true,
      "realtime": true,
      "storage": true,
      "edge_functions": true
    },
    "tables": [
      "listings",
      "leads",
      "agent_runs",
      "conversations",
      "organizations"
    ]
  }
}
```

### Client Setup
```typescript
// Supabase client
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

// Example: Insert listing
async function createListing(listing: Listing) {
  const { data, error } = await supabase
    .from('listings')
    .insert(listing)
    .select()
    .single();
  
  if (error) throw error;
  return data;
}

// Example: Search listings with vector similarity
async function searchListings(query: string) {
  const { data, error } = await supabase
    .rpc('search_listings', { query_text: query });
  
  if (error) throw error;
  return data;
}
```

---

## 6. Vercel (Deployment)

### Purpose
Frontend hosting and serverless functions.

### Configuration
```json
{
  "vercel": {
    "project_id": "${VERCEL_PROJECT_ID}",
    "project_name": "botanical-memories",
    "framework": "nextjs",
    "regions": ["iad1", "sfo1"],
    "functions": {
      "api/**": {
        "memory": 1024,
        "maxDuration": 30
      }
    }
  }
}
```

### Deployment Commands
```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod

# Set environment variables
vercel env add ANTHROPIC_API_KEY production
vercel env add SUPABASE_URL production

# View logs
vercel logs --follow
```

---

## 7. Coolify (Self-Hosting)

### Purpose
Self-hosted deployment on VPS for cost control.

### Configuration
```json
{
  "coolify": {
    "url": "https://your-coolify-instance.com",
    "api_token": "${COOLIFY_API_TOKEN}",
    "server": {
      "provider": "hostinger",
      "specs": {
        "cpu": "4 cores",
        "memory": "16GB",
        "storage": "100GB SSD"
      }
    },
    "services": [
      "web",
      "database",
      "n8n",
      "redis"
    ]
  }
}
```

---

## 8. n8n (Automation)

### Purpose
Workflow automation for scheduled tasks.

### Configuration
```json
{
  "n8n": {
    "webhook_url": "https://n8n.your-domain.com",
    "workflows": [
      {
        "name": "Lead Scraping",
        "schedule": "0 0 * * *",
        "description": "Nightly lead scraping from Apollo"
      },
      {
        "name": "Content Generation",
        "schedule": "0 6 * * *",
        "description": "Daily blog post generation"
      },
      {
        "name": "Lead Nurturing",
        "schedule": "0 */6 * * *",
        "description": "Follow-up emails every 6 hours"
      }
    ]
  }
}
```

---

## Security Best Practices

1. **API Keys**: Never expose in client-side code
2. **Rate Limiting**: Implement for all external APIs
3. **Caching**: Cache responses to reduce API calls
4. **Monitoring**: Track usage and costs
5. **Rotation**: Rotate keys every 30 days
6. **Encryption**: Encrypt sensitive data at rest

---

**Document Version:** 1.0
**Last Updated:** 2026-02-21
