AGENTS.md
Purpose
This file provides instructions for AI coding agents working in the `industrial-conveyor-control-system` repository.
The project is a local industrial automation testbed for a simulated conveyor sorting cell. OpenPLC owns the control logic, Python simulates the physical process, Modbus TCP connects the components, and Node-RED provides the HMI/SCADA-style interface.
Agents should help implement the system incrementally without blurring those responsibilities.
Primary Engineering Rule
The PLC owns control decisions.
The HMI sends operator requests; it does not directly command simulated actuators.
The Python simulator exposes process inputs and applies PLC outputs; it does not decide the control sequence.
OpenPLC validates requests, applies interlocks, advances the sequence, handles faults, and determines output commands.
Do not move PLC control logic into Python or Node-RED merely because it is easier to implement there.
Current Project Scope
The initial system contains:
One conveyor
Type A and Type B items
One diverter
Entry, classification, and exit sensors
Start, stop, and reset requests
Automatic and manual modes
Emergency-stop and jam inputs
Production counts
Alarm and status data
Do not add unrelated equipment, cloud services, machine learning, databases, authentication systems, or complex UI frameworks unless the user explicitly requests them.
Architecture Boundaries
`plc/`
Use for:
Structured Text, Ladder Diagram, or OpenPLC project source
State sequencing
Interlocks
Alarm logic
Operating modes
Output decisions
PLC configuration notes
Do not place Python simulation behavior or HMI presentation logic here.
`simulator/`
Use for:
Conveyor and item models
Sensor calculations
Actuator response
Fault injection
Modbus communication
Simulator configuration
Python unit tests
The simulator should remain usable without the HMI.
`hmi/`
Use for:
Sanitized Node-RED flow exports
Dashboard configuration
Operator controls
Status indicators
Alarm displays
Counts and trends
HMI setup documentation
Never commit Node-RED credential files, passwords, access tokens, or machine-specific secrets.
`integration/`
Use for end-to-end tests involving more than one subsystem.
`config/`
Use for machine-readable shared configuration, especially the Modbus register map and fault scenarios.
`docs/`
Use for architecture, state-machine, I/O, test-plan, and design-decision documentation.
Development Priorities
Implement features in this order unless the user directs otherwise:
Define the process states and I/O.
Establish one shared Modbus register map.
Build a minimal simulator that can expose sensors and apply outputs.
Implement PLC start, stop, and basic conveyor control.
Add one complete Type A sorting cycle.
Add the Type B path.
Add HMI visibility and operator requests.
Add faults, alarms, and recovery.
Add end-to-end automated tests.
Improve documentation and presentation.
Prefer one working vertical slice over many incomplete modules.
Required Workflow for Changes
Before editing:
Read `README.md`.
Inspect the relevant subsystem and its tests.
Read `config/register-map.yaml` if communication or I/O is involved.
Identify which component owns the requested behavior.
State a concise implementation plan.
While editing:
Make the smallest coherent change that satisfies the task.
Preserve subsystem boundaries.
Update tests with behavior changes.
Update documentation and configuration when interfaces change.
Avoid unrelated refactors.
After editing:
Run the relevant unit tests.
Run integration tests when interfaces or cross-component behavior changed.
Review the diff for secrets, generated files, and accidental scope expansion.
Summarize changed files, behavior, tests run, and remaining limitations.
Do not claim that a test passed unless it was actually run successfully.
Python Standards
Target Python 3.11 or later unless the project configuration specifies otherwise.
Use type hints for public functions, methods, and data models.
Prefer small modules with clear ownership.
Use `dataclasses`, enums, and explicit state models where they improve clarity.
Keep simulation timing configurable and avoid unexplained magic numbers.
Use the `logging` module instead of scattered `print()` calls in production code.
Keep external I/O at module boundaries so logic can be unit tested.
Use dependency injection or test doubles for Modbus communication when practical.
Write deterministic tests. Seed or isolate randomness.
Use `pytest` for Python tests.
Suggested simulator package:
```text
simulator/src/conveyor_sim/
├── main.py
├── process.py
├── conveyor.py
├── item.py
├── sensors.py
├── actuators.py
├── faults.py
├── modbus_client.py
├── register_map.py
└── config.py
```
PLC Logic Standards
Use descriptive symbolic variable names rather than raw addresses throughout the logic.
Keep the Modbus address mapping separate from sequence logic when possible.
Define operating states explicitly.
Use timers with named purposes and documented units.
Ensure stop and fault behavior is deterministic.
Define which alarms latch and what conditions permit reset.
Do not allow a reset command to hide an active fault.
Document assumptions about scan-cycle behavior and edge detection.
Prefer reusable function blocks when actual repeated behavior exists.
Avoid premature abstraction for a single conveyor and diverter.
HMI Standards
Treat buttons as requests to the PLC.
Clearly distinguish commands, feedback, permissives, and alarms.
Display actual PLC or process feedback, not merely the last requested state.
Show communication health.
Use consistent colors and labels.
Do not represent an unsafe condition as healthy because a command was issued.
Export sanitized flows to `hmi/flows.json` after meaningful changes.
Document required Node-RED packages in `hmi/package.json` or `hmi/README.md`.
Modbus Register-Map Rules
`config/register-map.yaml` is the machine-readable source of truth for shared addresses.
For every value, define:
Symbolic name
Modbus table or data type
Address
Direction or owner
Valid range
Engineering unit, if applicable
Description
When adding or changing a register:
Update `config/register-map.yaml`.
Update `docs/modbus-register-map.md`.
Update the PLC mapping.
Update Python mapping or codec code.
Update the Node-RED flow if the HMI uses the value.
Update tests.
Never duplicate unexplained raw addresses across source files. Centralize or generate mappings where practical.
State-Machine Guidance
Use explicit states rather than a loose collection of booleans. A reasonable starting model is:
```text
STOPPED
STARTING
RUNNING
SORTING
STOPPING
FAULTED
EMERGENCY_STOPPED
```
This list is guidance, not a mandatory final design. Add or remove states only when the process behavior requires it.
For every state, define:
Entry conditions
Allowed outputs
Transition conditions
Timeout behavior
Fault behavior
Reset behavior
Update `docs/state-machine.md` whenever state behavior materially changes.
Fault-Handling Expectations
At minimum, support testable behavior for:
Emergency stop
Conveyor jam
Sensor stuck on
Sensor missing an expected item
Communication interruption
For each fault, document:
Detection condition
PLC response
Safe output state
Alarm behavior
Operator action
Reset permissives
Expected test case
Do not imply that simulated software emergency-stop behavior is equivalent to a hardware safety system.
Testing Requirements
Unit Tests
Add unit tests for:
Item movement
Sensor activation boundaries
Diverter response
Fault injection
Configuration loading
Register encoding and decoding
PLC Scenario Tests
Verify:
Safe start permissives
Normal Type A sequence
Normal Type B sequence
Stop behavior
Emergency-stop response
Jam response
Alarm latching
Reset rejection while a fault remains active
Integration Tests
Integration tests should verify externally observable behavior rather than internal implementation details.
Examples:
A Type A item reaches the Type A destination.
A Type B item reaches the Type B destination.
Counts increment only after successful sorting.
Emergency stop removes motion commands.
A jam causes the expected state and alarm.
Recovery requires both fault clearance and a valid reset.
Configuration and Secrets
Never commit `.env` files, passwords, tokens, or Node-RED credentials.
Add safe examples as `.env.example` or `*.example.yaml`.
Use localhost defaults only when clearly documented.
Keep ports, unit IDs, scan rates, timeouts, and simulation speed configurable.
Do not silently change network defaults without updating documentation.
Generated and Runtime Files
Do not commit:
Python cache files
Virtual environments
Test caches and coverage output
Node modules
Node-RED credential files
Runtime databases
Logs
Generated PLC binaries
Machine-specific editor configuration
Do commit:
Human-editable source
Sanitized Node-RED flow exports
Dependency manifests
Example configuration
Tests
Architecture and interface documentation
Documentation Standards
Update the README only when the information is useful to a new developer or employer reviewing the repository.
Technical documentation should explain:
What was designed
Why the design was selected
Which component owns each behavior
How components communicate
How the behavior was tested
Known limitations
Avoid claiming production readiness, hardware safety certification, or real factory deployment.
Safety Notice for Agents
This is an educational simulation. Do not generate instructions that present this project as a certified safety controller. Do not recommend connecting it directly to production machinery without appropriate hardware design, risk assessment, professional review, and validation.
Commit Guidance
Use focused commits with imperative messages, for example:
```text
feat(simulator): add conveyor item movement
feat(plc): implement start permissive logic
feat(hmi): display conveyor state and alarms
test(integration): cover emergency-stop response
docs(modbus): define initial register map
fix(simulator): prevent duplicate exit counts
```
Do not combine formatting cleanup, redesign, and new functionality in one commit unless they are inseparable.
Expected Agent Response
After completing a coding task, report:
What changed
Files changed
Tests or checks run
Results
Assumptions
Remaining limitations or the next logical task
Keep the report concise and factual.
Definition of Done
A change is complete when:
The requested behavior is implemented in the correct subsystem.
Relevant tests pass.
Register-map and interface changes are synchronized.
Documentation reflects material behavior changes.
No secrets or generated runtime artifacts are included.
The implementation does not bypass PLC control ownership.