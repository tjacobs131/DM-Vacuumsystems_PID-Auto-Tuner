# Use Cases
---
| __Use Case 1__                | <span style="font-weight:normal">Initial Tuning</span> | 
|---|---|
| __Actor__                     | Control Engineer
| __Goal__                      | Determine stable PID settings for a new system automatically |
| __Preconditions__             | - New vacuum system is installed and functional.<br>- Auto-tuner software is deployed on the Beckhoff PLC.<br>- System is in a safe state to begin heating tests. |
| __Postconditions__            | - System is ready for initial operation with tuned PID settings.<br>- Engineer has saved significant time compared to manual tuning.
| __Main Event Flow__           | 1. Process Engineer initiates the auto-tuner program on the Beckhoff PLC.<br>2. The auto-tuner starts the PID tuning algorithm.<br>3. The auto-tuner interacts with the heating element and temperature sensor to collect system response data.<br>4. The auto-tuner analyzes the data and iteratively adjusts the PID parameters (P, I, D).<br>5. Steps 3 and 4 are repeated until a stable and acceptable temperature control performance is achieved.<br>6. The auto-tuner saves the optimal PID settings.<br>7. The auto-tuner indicates completion to the Process Engineer (e.g., via a log message or visual indicator).
| __Alternative Event Flow__    | a. Tuning Failure: If the algorithm cannot converge to stable settings within a reasonable timeframe or predefined limits, the auto-tuner will stop and report a failure, requiring manual intervention.<br>b. User Abort: The Process Engineer can manually abort the tuning process at any time if necessary.
---
| __Use Case 2__                | <span style="font-weight:normal">Re-Tuning for Maintenance</span> | 
|---|---|
| __Actor__                     | Maintenance Engineer
| __Goal__                      | Re-optimize PID settings after major system maintenance or repair
| __Preconditions__             | - Vacuum system has undergone major maintenance or component replacement.<br>- Auto-tuner software is deployed on the Beckhoff PLC.<br>- System is in a safe state to begin heating tests.
| __Postconditions__            | - PID settings are re-optimized for the current system configuration.<br>- System performance is restored or improved after maintenance.<br>- Engineer has re-tuned the system.
| __Main Event Flow__           | See Use Case 1
| __Alternative Event Flow__    | a. No Improvement Found: If the auto-tuner determines that the existing PID settings are already optimal, it may report that no significant changes were made.<br>b. Tuning Failure/User Abort: See Use Case 1