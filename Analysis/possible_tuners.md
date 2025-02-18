Ziegler–Nichols
• Requirements:
 – Requires dead time to be less than 0.5× the time constant.
 – Requires a large overshoot compared to the actual target temperature.
 – Generally produces aggressive PID values that may be less accurate compared to more modern methods.
• Test Methods:
 – Bump (Step) Test: An open‐loop step test is used to extract process gain, dead time, and time constant from the reaction curve.
 – Relay Method: A relay test forces a safe limit cycle so that the ultimate gain and period can be measured.
• Estimated tuning time:
Step (Bump) Test: One open‐loop step test takes roughly 7 hours for heating (plus minimal computation).
Relay Test: Forcing oscillations typically requires 2–3 full cycles. Depending on whether you count only the heating period (about 7 hours per cycle, giving 14–21 hours) or the complete cycle (approximately 17 hours per cycle, leading to 34–51 hours).

    Relay Method Details: https://www.controleng.com/relay-method-automates-pid-loop-tuning/
    https://yilinmo.github.io/EE3011/Lec9.html 

Åström–Hägglund
• Characteristics:
 – Requires little prior process knowledge.
 – Avoids loop instability by preventing controller output from hitting full scale.
 – Ideally produces square oscillations, though in practice these are approximated.
 – Later extensions address issues such as sluggish response and excessive derivative action.
• Test Method:
 – Relay Auto-tuning: Uses a controlled relay test to generate a limit cycle for parameter estimation, safely producing oscillations without pushing the process into dangerous conditions.
• Estimated tuning time:
Uses a safe relay test to force a limit cycle.
Estimated duration: Approximately 15–20 hours (over 2–3 cycles).

Cohen–Coon
• Requirements:
 – Requires dead time to be less than 2× the time constant.
 – Relies on a measurable overshoot relative to a lower target temperature than the actual setpoint.
 – Assumes the process can be well approximated by a first‐order model (without integrators).
• Test Method:
 – Step (Bump) Test: A step change is applied to capture the open-loop reaction curve, from which process gain, dead time, and time constant are derived for tuning equations.
• Estimated tuning time:
Based on a single open‑loop step test to capture the process reaction curve.
Estimated time: About 7 hours (or 7–17 hours if waiting for cooling between tests).

    Further Details: https://blog.opticontrols.com/archives/383 

Lambda Tuner / Internal Model Control (IMC)
• Characteristics:
 – Based on Åström–Hägglund
 – Only applicable to PI controllers, D is not taken into consideration.
 – Not ideal when speed is a strict requirement, as it tends to produce a slower, more conservative response.
 – Robust against inaccuracies in dead time estimation and process characteristic variations.
• Test Methods:
 – Bump (Step) Test: An open-loop test measures process gain, dead time, and time constant.
 – The user then selects a desired closed-loop time constant (λ), typically between one and three times the process time constant, and applies the Lambda tuning equations (integral time is set equal to the process time constant) to achieve an overdamped, non-oscillatory response.
• Estimated tuning time:
Requires a step test to identify the process model, with little extra time needed for selecting λ.
Estimated time: Roughly 7 hours.

    Lambda Tuning Fundamentals: https://blog.opticontrols.com/archives/260
    https://www.controleng.com/fundamentals-of-lambda-tuning/

Simple Control Rule (SIMC)
• Characteristics:
 – Introduces an extra tuning parameter that the operator sets, providing flexibility in the closed-loop response speed.
 – Particularly effective on time-delayed processes.
• Test Method:
 – Step (Bump) Test: Used to derive a simplified first-order plus dead time model, which SIMC then uses—along with the extra tuning parameter—to adjust the closed-loop speed of response.
• Estimated tuning time:
Also derived from a step test and a user‑defined extra parameter.
Estimated duration: Approximately 7 hours per test.

Tyreus–Luyben
• Characteristics:
 – Provides less aggressive controller settings compared to Ziegler–Nichols, favoring stability and robustness.
 – Tends to produce more conservative tuning results with reduced overshoot and oscillatory behavior.
• Test Method:
 – Step (Bump) Test: Determines process reaction curve parameters, which are then used in Tyreus–Luyben’s specific tuning formulas to calculate the PID gains.
 – Can also utilize oscillation-based data (similar to the relay method) but applies different scaling rules to yield smoother responses.
• Estimated tuning time:
Uses step test data with conservative tuning rules.
Estimated time: About 7 hours per test.

Harris Hawks
• Overview:
 – A modern, optimization-based approach inspired by the cooperative hunting strategy of Harris’ hawks.
 – Belongs to the family of population-based metaheuristic algorithms and is used to explore the PID parameter space in a robust manner.
• Characteristics:
 – Capable of handling nonlinear and complex process dynamics by evaluating multiple candidate solutions simultaneously.
 – May offer improved performance over traditional methods in systems with highly variable behavior.
• Test Method:
 – Iterative Optimization: The algorithm iteratively evaluates candidate PID settings against a performance metric (such as minimizing integral error, overshoot, or settling time) until convergence to a near-optimal configuration is reached.
 – Typically requires simulation or real-time process data to validate and fine-tune the parameter sets.
• Estimated tuning time:
Involves iterative evaluation over multiple full cycles (e.g. 5–10 iterations).
Estimated duration: Ranges from roughly 48–72 hours (if fewer cycles are used) up to about 170 hours if each iteration requires a full 17‑hour cycle.

Neural Network Approach
• Overview:
 – Uses machine learning to model the relationship between process dynamics and optimal PID parameters.
 – Capable of adapting to nonlinear behaviors and uncertainties that are difficult to capture with traditional tuning rules.
• Characteristics:
 – Can be trained offline using historical data or adapt online through continuous learning methods.
 – Offers potential for self-tuning and real-time adjustment in dynamic operating environments.
• Test Method:
 – Model Training and Validation: A neural network is trained using process data (via simulations or actual measurements) to predict PID parameters.
 – The predicted parameters are then iteratively refined through additional training and validation against performance criteria such as response time, overshoot, and stability.
• Estimated tuning time:
Training requires several cycles of data (typically 3–5 cycles for training from scratch).
Estimated time: Around 20–40 hours of data collection (or about 170 hours if 10 full cycles are needed without prior data).

Swarm Learning
• Overview:
 – Employs swarm intelligence algorithms (such as Particle Swarm Optimization, Ant Colony Optimization, etc.) to collaboratively search for optimal PID parameters.
 – Inspired by the collective behavior of natural swarms, this method leverages the strength of distributed problem solving.
• Characteristics:
 – Excels in exploring large, multidimensional parameter spaces and escaping local optima.
 – Particularly useful in complex, nonlinear, or multi-modal control problems where conventional methods might fail.
• Test Method:
 – Swarm-Based Optimization: Multiple candidate solutions (agents) are evaluated simultaneously based on a performance index (e.g., integrated absolute error).
 – The swarm iteratively converges toward optimal PID settings through information sharing and coordinated adjustments.
 – Although computationally intensive, this method provides robust tuning across a wide range of operating conditions.
• Estimated tuning time:
Evaluates many candidate solutions over several cycles.
Estimated duration: On the order of 5–7 days (roughly 120–168 hours in real‑time operation).

Iterative feedback tuning
• Overview:
 – Allows for the tuning of multivariable systems.
 – Aims for no/minimal overshoot with fast response to setpoint changes.
 – Takes (#inputs * #outputs) number of cycles.
 – Can be optimized with randomization: https://pure.tue.nl/ws/portalfiles/portal/317655713/Efficient_MIMO_Iterative_Feedback_Tuning_via_Randomization_1_.pdf 
 • Estimated tuning time:
Typically applied to SISO systems using about 3–5 iterations.
Estimated time: Approximately 50 hours total per heating zone.
With randomized optimization this might drop to 10-20 total iterations with only partial heating (8-14 hours)

    Paper: https://www.sciencedirect.com/science/article/pii/S0967066102003039
