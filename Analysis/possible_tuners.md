Ziegler–Nichols
    - Requires dead time to be less than 0.5x time constant
    - Requires large overshoot over actual target temperature
    - Gives generally inaccurate PID values. More modern solutions are preferred.
    - Works with bump method, and relay method
Relay method: https://www.controleng.com/relay-method-automates-pid-loop-tuning/
https://yilinmo.github.io/EE3011/Lec9.html

Åström–Hägglund
    - Little prior process knowledge required
    - No loop instability
    - Dangerous oscillation can be avoided
        - Output need not be at 100%
    - Oscillations are ideally square, likely not achievable
    - Solved in later extensions:
        - Can give sluggish response
        - Excessive derivative action

Cohen–Coon
    - Requires dead time to be less than 2x time constant
    - Requires overshoot over a lower target temperature than actual
    - Requires a first-order process variable
    - Works with step models and the bump method
https://blog.opticontrols.com/archives/383 

Lambda tuner / Internal Model Control (IMC)
    - Not preferable when speed is a requirement
    - Robust against inaccurate dead time estimations
    - Robust against process characteristic changes
https://blog.opticontrols.com/archives/260
https://www.controleng.com/fundamentals-of-lambda-tuning/

Simple control rule (SIMC)
    - Additional tuning parameter, has to be set by operator
    - Works on time-delayed processes
    - Works with step-response models