# SOP: Autonomous Agency (BMAD / Ralphy Loop)

## Overview
This Standard Operating Procedure (SOP) defines the architecture and methodology for deploying and managing autonomous AI agents within the ArchonX OS ecosystem, specifically focusing on the "King Mode" objective of achieving a $100M goal by New Year's 2030.

## Core Methodologies
1. **BMAD (Breakthrough Method of Agile AI-driven Development)**: A framework for rapid, iterative development driven by AI agents.
2. **Ralphy Loop**: The continuous execution cycle for agents: PLAN -> IMPLEMENT -> TEST -> EVALUATE -> PATCH -> REPEAT.

## Architecture
The autonomous agency architecture relies on the following components:
- **Local LLMs (Ollama)**: For cost-effective, private, and local inference.
- **Docker**: Containerization of agent environments to ensure consistency and reproducibility.
- **Ngrok**: Secure tunneling to expose local agent webhooks to the internet for external integrations.
- **GitHub Actions (Runners)**: CI/CD pipelines for automated testing, deployment, and scheduled agent tasks.
- **Vercel**: Hosting for preview environments and frontend dashboards.

## Deployment Steps
1. **Containerization**: Ensure all agents are containerized using Docker.
2. **Tunneling**: Use Ngrok to expose local endpoints during development and testing.
3. **Automation**: Configure GitHub Actions to trigger agent workflows based on repository events or schedules.
4. **Monitoring**: Utilize the Beads protocol (`bd`) for tracking agent tasks, blockers, and progress.

## The $100M Goal (King Mode)
All agents operating within this framework must be aligned with the primary objective: achieving a $100M valuation/revenue by New Year's 2030. This goal must be injected into the core prompts of all autonomous agents.

## Security (Iron Claw)
All autonomous operations must adhere to the Iron Claw security protocols, ensuring that agents operate within defined boundaries and cannot execute destructive commands without explicit authorization.
