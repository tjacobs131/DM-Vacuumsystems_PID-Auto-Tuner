from pid_controllers.pid import PID

class Parallel_PID(PID):

    def __init__(self, max_output, min_output, kp = 20.0, ki = 0.12, kd = 0.06):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
        self.max_output = max_output
        self.min_output = min_output

    def calculate_output(self, process_variable, setpoint, dt):
        # Calculate error and its components
        error = setpoint - process_variable
        proportional = self.kp * error
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error

        # Save the current integrator value to allow rollback if needed
        previous_integral = self.integral
        self.integral += error * dt

        # Compute raw output
        output = proportional + self.ki * self.integral + self.kd * derivative

        # Check for saturation and rollback integrator if necessary
        if output > self.max_output:
            output = self.max_output
            # Revert the integration step that caused windup
            self.integral = previous_integral
        elif output < self.min_output:
            output = self.min_output
            self.integral = previous_integral

        return output
