class PID():
    def __init__(self, kp, ki, kd, setpoint, dt):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.dt = dt
        self.prev_error = 0
        self.integral = 0

    def update_parallel(self, process_variable):
        # Update the PID controller using parallel form

        # Calculate the error
        error = self.setpoint - process_variable

        # Calculate the proportional term
        proportional = self.kp * error

        # Calculate the integral term
        self.integral += error * self.dt

        # Calculate the derivative term
        derivative = (error - self.prev_error) / self.dt

        # Update the previous error
        self.prev_error = error

        # Calculate the control signal
        return proportional + self.ki * self.integral + self.kd * derivative

    def update_series(self, process_variable):
        # Update the PID controller using series form
        pass

    def update_ideal(self, process_variable):
        # Update the PID controller using ideal form
        pass

    def update_setpoint(self, setpoint):
        # Update the setpoint
        self.setpoint = setpoint