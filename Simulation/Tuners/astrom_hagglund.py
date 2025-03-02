from pid_controllers.parallel_pid import Parallel_PID
import pid_config
import math

class AstromHagglund(Parallel_PID):
    def __init__(self, target_iterations: int = 10):
        self.final_cooldown = False

        self.kp = 0
        self.ki = 0
        self.kd = 0

        self.pAvg = 0
        self.iAvg = 0
        self.dAvg = 0

        self.ku = 0
        self.tu = 0

        self.heating = True
        self.max_controller_output = 100
        self.min_controller_output = 0
        self.controller_output = self.max_controller_output

        self.timer = 0
        self.time1 = 0
        self.time2 = 0
        self.thigh = 0
        self.tlow = 0

        self.max_recorded_output = -float('inf')
        self.min_recorded_output = float('inf')

        self.target_iterations = target_iterations
        self.iterations_to_skip = 1
        self.iterations = 0

    def calculate_output(self, process_variable: float, setpoint: float, dt: float) -> float:
        if self.final_cooldown:
            if self.check_stability(process_variable, dt, 0.5, 5):
                self.stable_buffer = []
                # Calculate final averages
                # Changing the config triggers the PID controller to switch (see main.py)
                count = max(1, self.iterations - self.iterations_to_skip)
                pid_config.kp = self.pAvg / count
                pid_config.ki = self.iAvg / count
                pid_config.kd = self.dAvg / count
                

            return self.min_controller_output

        # Check if we've completed all iterations
        if self.iterations > self.target_iterations + self.iterations_to_skip:
            # Mark tuning as complete
            self.heating = False
            self.final_cooldown = True

            return self.min_controller_output

        # Update recorded max/min values
        if self.max_recorded_output < process_variable:
            self.max_recorded_output = process_variable
        if self.min_recorded_output > process_variable:
            self.min_recorded_output = process_variable

        # Update timer
        self.timer += dt

        # Mode switching logic
        if self.heating and process_variable > setpoint: # If we're heating, crossing the setpoint upwards
            self.heating = False
            self.time1 = self.timer
            self.thigh = self.time1 - self.time2

        elif not self.heating and process_variable < setpoint: # If we're cooling, crossing the setpoint downwards
            self.heating = True
            self.time2 = self.timer
            self.tlow = self.time2 - self.time1
            
            # Prevent division by zero
            amplitude_pv = self.max_recorded_output - self.min_recorded_output
            if amplitude_pv > 0:
                self.ku = (4 * self.max_controller_output - self.min_controller_output) / (math.pi * amplitude_pv)
                self.tu = self.thigh + self.tlow

                # Calculate PID parameters
                self.kp = 0.6 * self.ku
                self.ki = 0.5 * self.tu
                self.kd = 0.125 * self.tu

                # Update averages - only for iterations after skipping
                if self.iterations >= self.iterations_to_skip:
                    self.pAvg += self.kp
                    self.iAvg += self.ki
                    self.dAvg += self.kd
            
                self.iterations += 1
        
        # Set the controller output based on heating mode
        if self.heating:
            self.controller_output = self.max_controller_output
        else:
            self.controller_output = self.min_controller_output

        return self.controller_output



    