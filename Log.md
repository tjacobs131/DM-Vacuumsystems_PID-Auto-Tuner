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
Created HMI for heater simulation
Added possible tuners
    Started writing tuning methods evaluation
Understand IFT tuning gradient descent method
    Decided to use Ziegler-Nichols for sure as a baseline result

# ?
    - How large is the dead-time compared to cycle-time? 0.5x? 2x?
    - Parallel or series PID?