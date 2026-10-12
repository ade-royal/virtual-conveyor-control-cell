# Industrial Conveyor Control System

A locally hosted industrial automation testbed for a simulated conveyor sorting cell. The system uses OpenPLC for PLC control logic, Python to simulate the physical conveyor process, Modbus TCP for communication, and Node-RED for an HMI/SCADA-style operator dashboard.

> **Project status:** Initial development

## Project Overview

This project models a conveyor that transports and sorts two item types. A simulated sensor detects and classifies each item, the PLC tracks it through the process, and a diverter routes it to the correct destination.

The system is designed around a core industrial-controls principle: **the PLC owns the control decisions**. The Python simulator represents the physical process, while the Node-RED dashboard provides supervision and operator requests without bypassing PLC interlocks.

## Objectives

- Program PLC sequencing, operating modes, interlocks, and fault recovery
- Build a stateful Python simulation of a conveyor, sensors, items, and actuators
- Exchange process data and commands through Modbus TCP
- Develop an HMI for controls, alarms, production counts, and trends
- Inject realistic faults such as jams and failed sensors
- Verify normal operation and safe failure behavior with repeatable tests
- Document the system architecture, I/O list, and Modbus register map

## System Architecture

```text
+-----------------------------+
| Node-RED HMI                |
| - Operator requests         |
| - Status and alarms         |
| - Counts and trends         |
+--------------+--------------+
               |
               | Modbus TCP
               |
+--------------v--------------+
| OpenPLC Runtime             |
| - Sequence control          |
| - Modes and interlocks      |
| - Fault handling            |
| - Output decisions          |
+--------------+--------------+
               |
               | Modbus TCP
               |
+--------------v--------------+
| Python Process Simulator    |
| - Conveyor and item motion  |
| - Sensors and actuators     |
| - Classification            |
| - Fault injection           |
+-----------------------------+
```

## How the System Works

1. The Python simulator creates a Type A or Type B item.
2. A simulated photoelectric sensor detects the approaching item.
3. The simulator exposes sensor and classification data over Modbus TCP.
4. OpenPLC evaluates the inputs and advances the control sequence.
5. The PLC commands the conveyor and diverter only when all interlocks are satisfied.
6. The simulator applies those commands to the virtual equipment.
7. Node-RED displays system status, alarms, and production metrics.
8. Integration tests verify sorting, emergency-stop behavior, jam handling, and recovery.

## Planned Operating Modes

- **Stopped:** Outputs are placed in their defined stopped state.
- **Automatic:** The PLC runs the complete sorting sequence.
- **Manual:** Authorized individual outputs can be requested for testing, subject to safety interlocks.
- **Faulted:** Unsafe motion is stopped and the active fault is reported.
- **Emergency Stop:** Motion commands are removed until the emergency-stop condition is cleared and the system is deliberately reset.

## Initial Scope

The first working version will include:

- One conveyor
- Two item types
- One diverter
- Entry, classification, and exit sensors
- Automatic start/stop/reset controls
- Type A, Type B, and total production counters
- Emergency-stop and jam conditions
- A basic Node-RED operator dashboard
- Unit and integration tests

## Technology Stack

- **OpenPLC:** PLC program development and runtime
- **Structured Text or Ladder Diagram:** IEC 61131-3 control logic
- **Python:** Process simulation, fault injection, and tests
- **Modbus TCP:** Communication among the PLC, simulator, and HMI
- **Node-RED:** HMI/SCADA-style visualization and operator requests
- **pytest:** Automated Python and integration testing
- **YAML:** Shared configuration and register-map documentation
- **Git/GitHub:** Version control and project documentation

## Repository Structure

```text
industrial-conveyor-control-system/
├── README.md
├── AGENTS.md
├── LICENSE
├── .gitignore
├── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── state-machine.md
│   ├── modbus-register-map.md
│   ├── io-list.md
│   ├── fault-scenarios.md
│   └── testing-plan.md
│
├── plc/
│   ├── programs/
│   ├── function-blocks/
│   ├── configuration/
│   └── README.md
│
├── simulator/
│   ├── pyproject.toml
│   ├── README.md
│   ├── src/
│   │   └── conveyor_sim/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── process.py
│   │       ├── conveyor.py
│   │       ├── item.py
│   │       ├── sensors.py
│   │       ├── actuators.py
│   │       ├── faults.py
│   │       ├── modbus_client.py
│   │       ├── register_map.py
│   │       └── config.py
│   └── tests/
│
├── hmi/
│   ├── flows.json
│   ├── package.json
│   ├── settings.example.js
│   ├── README.md
│   └── screenshots/
│
├── integration/
├── config/
│   ├── register-map.yaml
│   ├── simulator.example.yaml
│   └── fault-scenarios.yaml
│
├── scripts/
└── data/
```

Folders and files will be added incrementally as real functionality is implemented. Empty architecture should not be created solely to match this planned tree.

## Control Ownership

The components have deliberately separated responsibilities:

### OpenPLC

OpenPLC owns:

- State transitions
- Conveyor and diverter commands
- Start, stop, and reset validation
- Automatic/manual mode behavior
- Interlocks
- Alarm latching
- Fault recovery rules

### Python Simulator

The simulator owns:

- Item creation and movement
- Simulated sensor states
- Actuator response
- Conveyor physics at the selected level of detail
- Item classification inputs
- Fault injection

The simulator must not make PLC control decisions. It reports process conditions and applies PLC outputs.

### Node-RED

Node-RED owns:

- Operator request controls
- Status visualization
- Alarm display and history
- Production counters and trends

The HMI must not directly force simulator actuators. Operator actions are sent to the PLC, and the PLC determines whether they are allowed.

## Modbus Register Map

The register map will be maintained in `config/register-map.yaml` and documented in `docs/modbus-register-map.md`.

Every mapped value should define:

- Symbolic name
- Modbus data type
- Address
- Direction or owner
- Valid range
- Engineering unit, when applicable
- Description

Example only:

```yaml
coils:
  start_request:
    address: 0
    direction: hmi_to_plc

  conveyor_command:
    address: 10
    direction: plc_to_simulator

discrete_inputs:
  entry_sensor:
    address: 0
    direction: simulator_to_plc

  jam_sensor:
    address: 1
    direction: simulator_to_plc

holding_registers:
  item_type:
    address: 0
    direction: simulator_to_plc

  total_count:
    address: 10
    direction: plc_to_hmi
```

The addresses above are placeholders until the initial I/O design is finalized.

## Testing Strategy

### Unit Tests

Unit tests will validate individual Python components, including:

- Conveyor movement
- Item state and classification
- Sensor activation
- Actuator response
- Fault injection
- Register encoding and decoding

### PLC Logic Tests

PLC behavior will be checked against defined scenarios, including:

- Start permitted under safe conditions
- Start rejected while the emergency stop is active
- Correct Type A and Type B diverter sequences
- Safe outputs after a jam
- Alarm latching and acknowledgment
- Reset rejected while the initiating fault remains present

### Integration Tests

End-to-end tests will validate communication and system behavior across the simulator, PLC, and HMI-facing data:

- Normal Type A cycle
- Normal Type B cycle
- Emergency stop during operation
- Conveyor jam
- Failed or stuck sensor
- Communication interruption
- Fault clearing and controlled restart

## Safety and Scope Notice

This repository is an educational simulation and portfolio project. It is not safety-certified and must not be used to control production equipment or safety-critical machinery without appropriate hardware, risk assessment, engineering review, and validation.

An emergency-stop button represented in software is a simulation of control behavior, not a replacement for a hardware safety circuit.

## Getting Started

Setup commands will be added as each subsystem is implemented. The intended local startup order is:

1. Start the OpenPLC runtime and load the conveyor program.
2. Start the Python process simulator.
3. Import and start the Node-RED HMI flow.
4. Confirm Modbus connectivity and register values.
5. Run a normal sorting cycle.
6. Run the automated tests and fault scenarios.

## Development Roadmap

- [ ] Define process behavior and state machine
- [ ] Create the I/O list and Modbus register map
- [ ] Build the minimum Python conveyor simulation
- [ ] Implement PLC start/stop and conveyor control
- [ ] Add Type A and Type B sorting
- [ ] Add the Node-RED HMI
- [ ] Add production counters and event logging
- [ ] Implement emergency-stop and jam handling
- [ ] Add sensor-failure and communication-failure scenarios
- [ ] Build automated integration tests
- [ ] Add screenshots, architecture diagrams, and a demonstration video
- [ ] Document results and engineering tradeoffs

## Portfolio Summary

This project demonstrates industrial control programming, state modeling, process simulation, Modbus TCP integration, HMI development, interlocks, fault handling, and automated testing through a virtual conveyor-sorting cell.

## License

A license has not yet been selected. Add a `LICENSE` file before distributing or accepting external contributions.
