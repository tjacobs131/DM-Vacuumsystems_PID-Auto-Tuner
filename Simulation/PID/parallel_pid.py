class Parallel_PID():
    def __init__(self, kp = 20.0, ki = 0.12, kd = 0.06):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def get_output(self, process_variable, setpoint, dt):
        # Update the PID controller using parallel form

        # Calculate the error
        error = setpoint - process_variable

        # Calculate the proportional term
        proportional = self.kp * error

        # Calculate the integral term
        self.integral += error * dt

        # Calculate the derivative term
        derivative = (error - self.prev_error) / dt

        # Update the previous error
        self.prev_error = error

        # Calculate the control signal
        return proportional + self.ki * self.integral + self.kd * derivative