# Week 1
Started project plan
Learned TwinCat 3
    Learned Ladder diagrams, function block diagrams, and structured text via fridge example
    Translated LD, FBD parts into ST since this is used within D&M
Wrote PID simulation from existing python implementation
Wrote PID simulation with heating
Collected information about tuners regarding this use case
    Implemented Ziegler-Nichols tuner on heating simulation

# Week 2
Finished Ziegler-Nichols tuner implementation on simulation
    Refactored simulation code (following D&M conventions)
Collected information about tuners
Physics makes big difference, needs special tuning
Created basic HMI for heater simulation
Added possible tuners
    Started writing tuning methods evaluation
Understand IFT tuning gradient descent method
    Decided to use Ziegler-Nichols for sure as a baseline result

# Week 3
Implemented project plan feedback
Handed in project plan
Refined tuner evaluation
    Added Skogestad's IMC to tuner evaluation
    Started python simulation
Made python simulation modular (like target system)

# Week 4
Store measured system dynamics in file for faster manual tuning
Add tuning and evaluation plotting
Created simulation experiment runner for automation
Store generated plots per experiment
Improved performance of simulation
    Collected simulation results
    Wrote discussion on simulation results
Added use cases to report
    Started binding IO on test-setup PLC

# Week 5
Implement parallel PID on test-setup
Start working on Skogestad tuner
Implemented stability detection
Implemented Skogestad tuner

# ?
    - How long is the measurement time / time constant?
    - How large is the dead-time compared to cycle-time? 0.5x? 2x?
    - Do you use integral clamping?
    - Using a parallel, series or ideal PID?
    - !!D? Only PI?
    - Proof of work (sim || test setup)
      - Simulate actual scenario
      - Match test setup
      - Jasper's math?