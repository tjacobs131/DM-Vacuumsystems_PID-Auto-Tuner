from pid_controllers.pid import PID
import pid_config
from abc import ABC, abstractmethod
import sys
import heat_simulation.heat_sim as hs
from time import sleep
from tuners.astrom_hagglund import AstromHagglund
from tuners.skogestad import Skogestad

class EvaluateParallelPID(PID):
    def __init__(self, max_output, min_output, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
        self.max_output = max_output
        self.min_output = min_output
        self.initial_setpoint = 100
        self.setpoints = [
            self.initial_setpoint,            # Initial setpoint
            self.initial_setpoint * 0.25,      # 25% of initial
            self.initial_setpoint * 0.50,       # Perform setpoint drag test at 50%
            self.initial_setpoint * 1.25     # 125% of initial
        ]
        self.drag_test_index = 2
        self.current_setpoint = self.initial_setpoint
        self.setpoint_index = 0
        self.ramp_rate = 100                  # ramp rate (per second)
        self.phase = 'initial_stabilization'
        self.stable_threshold = 0.5           # Temperature threshold for stability
        self.stable_duration = 5.0            # Duration to consider stable (seconds)
        self.dwell_time = 5.0                # Time to stay at each setpoint after stability (seconds)
        self.stable_time = 0                  # Time counter for stability check
        self.dwell_counter = 0                # Time counter for dwelling at stable setpoint
        self.evaluation_complete = False
        self.target_setpoint = self.setpoints[0]
        self.is_dwelling = False              # Flag to track if we're in dwell phase

    def check_stability(self, process_variable, dt, threshold, duration):
        """Check if temperature has stabilized within threshold for duration"""
        if abs(process_variable - self.current_setpoint) < threshold:
            self.stable_time += dt
            if self.stable_time >= duration:
                return True
        else:
            self.stable_time = 0  # Reset if we went outside threshold
        return False

    def calculate_output(self, process_variable, setpoint, dt):
        if self.evaluation_complete:
            raise KeyboardInterrupt
        if self.phase == 'initial_stabilization':
            # Wait for temperature to stabilize at initial setpoint
            if not self.is_dwelling:
                if self.check_stability(process_variable, dt, self.stable_threshold, self.stable_duration):
                    print(f"Stabilized at {self.current_setpoint}°C, dwelling for {self.dwell_time} seconds")
                    self.is_dwelling = True
                    self.stable_time = 0  # Reset stability timer
            else:
                # Dwell at this setpoint for specified time
                self.dwell_counter += dt
                if self.dwell_counter >= self.dwell_time:
                    self.phase = 'transition'
                    self.setpoint_index = 1
                    self.target_setpoint = self.setpoints[self.setpoint_index]
                    self.dwell_counter = 0
                    self.is_dwelling = False
                    print(f"Dwell complete, transitioning to {self.target_setpoint}°C (50%)")
        
        elif self.phase == 'transition':
            # Ramp to target setpoint
            if self.current_setpoint > self.target_setpoint:
                self.current_setpoint -= self.ramp_rate * dt
                if self.current_setpoint <= self.target_setpoint:
                    self.current_setpoint = self.target_setpoint
            else:
                self.current_setpoint += self.ramp_rate * dt
                if self.current_setpoint >= self.target_setpoint:
                    self.current_setpoint = self.target_setpoint
            
            # If we reached target, wait for stabilization and dwell
            if self.current_setpoint == self.target_setpoint:
                if not self.is_dwelling:
                    if self.check_stability(process_variable, dt, self.stable_threshold, self.stable_duration):
                        print(f"Stabilized at {self.current_setpoint}°C, dwelling for {self.dwell_time} seconds")
                        self.is_dwelling = True
                        self.stable_time = 0  # Reset stability timer
                else:
                    # Dwell at this setpoint for specified time
                    self.dwell_counter += dt
                    if self.dwell_counter >= self.dwell_time:
                        self.setpoint_index += 1
                        self.dwell_counter = 0
                        self.is_dwelling = False
                        
                        if self.setpoint_index < len(self.setpoints):
                            self.target_setpoint = self.setpoints[self.setpoint_index]
                            if self.setpoint_index == self.drag_test_index:
                                self.ramp_rate = 0.1
                            else:
                                self.ramp_rate = 100
                            print(f"Dwell complete, transitioning to {self.target_setpoint}°C")
                        else:
                            self.phase = 'final_stabilization'
                            print(f"All setpoints tested, finalizing at {self.current_setpoint}°C")
        
        elif self.phase == 'final_stabilization':
            # Final stabilization and dwell at last setpoint
            if not self.is_dwelling:
                if self.check_stability(process_variable, dt, self.stable_threshold, self.stable_duration):
                    print(f"Stabilized at final setpoint, dwelling for {self.dwell_time} seconds")
                    self.is_dwelling = True
            else:
                self.dwell_counter += dt
                if self.dwell_counter >= self.dwell_time:
                    self.evaluation_complete = True
                    print("Evaluation complete")

        pid_config.setpoint = self.current_setpoint

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