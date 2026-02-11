# ARCHONX Core

This directory contains the core components of the ARCHONX operating system.

## Structure

```
core/
├── agents/             - Agent implementations
│   ├── pauli.py       - Pauli analytical agent
│   ├── synthia.py     - Synthia creative agent
│   └── ...            - Additional 62 agents
└── ...                - Other core modules
```

## Core Agents

The system is built around a dual-crew architecture featuring two primary agents:

1. **Pauli** - Analytical and logic processing
2. **Synthia** - Synthesis and creative operations

Together, these agents form the heart of the ARCHONX system, coordinating with 62 additional specialized agents to handle complex tasks.

## Development

When adding new agents, follow the existing patterns in `pauli.py` and `synthia.py`:
- Inherit common logging and metrics
- Implement standard status reporting
- Provide clear docstrings
- Include demo functionality

## See Also

- [Agent Documentation](agents/README.md)
- [System Specification](../ARCHONX_DUAL_CREW_SPEC.md)
- [Configuration Guide](../archonx-config.json)
