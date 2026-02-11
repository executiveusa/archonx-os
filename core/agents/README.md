# Core Agents

This directory contains the implementation of all ARCHONX agents.

## Primary Agents

### Pauli Agent (`pauli.py`)
The analytical heart of the system, responsible for:
- Data analysis and pattern recognition
- Logic verification and validation
- System diagnostics and monitoring
- Mathematical computations

### Synthia Agent (`synthia.py`)
The creative heart of the system, responsible for:
- Content synthesis and generation
- Creative problem solving
- Natural language processing
- User interaction and communication

## Usage

### Running Pauli Agent
```python
from core.agents.pauli import PauliAgent

agent = PauliAgent()
result = agent.analyze_data([1, 2, 3, 4, 5])
print(result)
```

### Running Synthia Agent
```python
from core.agents.synthia import SynthiaAgent

agent = SynthiaAgent()
result = agent.synthesize_content(["input1", "input2"], style="informative")
print(result)
```

## Additional Agents

The system is designed to support 62 additional specialized agents beyond Pauli and Synthia. These agents will be added as the system grows to handle domain-specific tasks.
