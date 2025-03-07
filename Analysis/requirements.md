# Requirements

## Functional Requirements
1.	The tuner will be implemented on a Beckhoff PLC (IPC).
2.	The tuner will be used for heating systems.
3.	The heating system will have a slow response to output signal.
4.	The vacuum system will have multiple PID controllers.

1.	The tuner shall run automatically and find PID variables.
2.	The tuner shall function on full-scale vacuum systems with multiple heating zones.
3.	The tuner shall not need to be re-run on the same system.
4.	The tuning time shall be minimized.
5.	The system shall stabilize with 1°C on the set temperature.

## Non-Functional Requirements
1. 	The tuner should be easy to integrate in an existing vacuum system.
2. 	Overshoot should be minimized.
3. 	System should reach the set-temperature as quickly as possible.
4.	All PID controllers should be tuned at the same time.