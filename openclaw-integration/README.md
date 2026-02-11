# OpenClaw Integration

This directory contains wrappers and integration code for the OpenClaw backend system.

## Overview

OpenClaw provides the backend infrastructure for:
- Resource management
- Task coordination
- State persistence
- Inter-agent communication

## Structure

```
openclaw-integration/
├── README.md           - This file
├── client/             - OpenClaw client wrappers
├── api/                - API integration layer
└── utils/              - Utility functions for OpenClaw
```

## Configuration

The OpenClaw backend URL and settings are configured in `archonx-config.json`:

```json
{
  "integration": {
    "openclaw": {
      "enabled": true,
      "backend_url": "http://localhost:8080"
    }
  }
}
```

## Usage

Integration with OpenClaw will allow agents to:
- Register with the backend
- Send and receive tasks
- Persist state across restarts
- Communicate with other agents

## Development

OpenClaw integration modules will be developed as the system architecture is finalized.
