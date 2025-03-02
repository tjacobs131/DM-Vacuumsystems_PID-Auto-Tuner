class Parallel_PID():

    stable_buffer = []

    def __init__(self, kp = 20.0, ki = 0.12, kd = 0.06):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

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
    
    def check_stability(self, current_value: float, dt: float, threshold: float, duration: float = 5.0) -> bool:
        stable_samples_required = int(duration / dt)
        
        # Update stability buffer
        self.stable_buffer.append(current_value)
        if len(self.stable_buffer) > stable_samples_required:
            self.stable_buffer.pop(0)
        
        # Check if values have been stable for the required duration
        is_stable = (len(self.stable_buffer) == stable_samples_required and
                    (max(self.stable_buffer) - min(self.stable_buffer) < threshold))
        
        return is_stable

    def get_stabilized_output(self) -> float:
        # Return the average of last 20% of the stable buffer
        return sum(self.stable_buffer[int(-0.2 * len(self.stable_buffer)):]) / len(self.stable_buffer[int(-0.2 * len(self.stable_buffer)):])