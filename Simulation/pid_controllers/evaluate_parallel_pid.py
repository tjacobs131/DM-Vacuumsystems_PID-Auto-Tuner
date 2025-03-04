from collections import deque
from pid_controllers.pid import PID
import pid_config
from abc import ABC, abstractmethod
import sys
import heat_simulation.heat_sim as hs
from time import sleep, time

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
            self.initial_setpoint * 0.40,     # 40% of initial
            self.initial_setpoint * 0.60,     # 60% of initial (drag test)
            self.initial_setpoint * 1.10      # 110% of initial
        ]
        self.drag_test_index = 2
        self.current_setpoint = self.initial_setpoint
        self.setpoint_index = 0
        self.ramp_rate = 100                  # Ramp rate (per second)
        self.phase = 'initial_stabilization'
        self.stable_threshold = 0.2           # Temperature threshold for stability
        self.stable_duration = 5.0            # Duration to consider stable (seconds)
        self.dwell_time = 10.0                # Time to stay at each setpoint after stability (seconds)
        self.stable_time = 0                  # Time counter for stability check
        self.dwell_counter = 0                # Time counter for dwelling at stable setpoint
        self.evaluation_complete = False
        self.target_setpoint = self.setpoints[0]
        self.is_dwelling = False              # Flag to track dwell phase

        # Oscillation detection variables
        self.phase_start_time = 0
        self.phase_max_error = -float('inf')
        self.phase_min_error = float('inf')
        self.last_max_min_update_time = 0
        self.minimum_oscillation_amplitude = 0.5
        self.noise_tolerance = 0.05  # Tolerance for noise in error signal


    def reset_oscillation_detection(self, current_time):
        self.phase_start_time = current_time
        self.phase_max_error = -float('inf')
        self.phase_min_error = float('inf')
        self.last_max_min_update_time = current_time

    def check_stability(self, process_variable, dt, threshold, duration):
        """Check if temperature has stabilized within threshold for duration"""
        if abs(process_variable - self.current_setpoint) < threshold:
            self.stable_time += dt
            if self.stable_time >= duration:
                return True
        else:
            self.stable_time = 0  # Reset if outside threshold
        return False

    def detect_oscillation(self, error, current_time):
        updated_max_min = False
        if error > (self.phase_max_error + self.noise_tolerance):
            self.phase_max_error = error
            updated_max_min = True
        if error < (self.phase_min_error - self.noise_tolerance):
            self.phase_min_error = error
            updated_max_min = True

        if updated_max_min:
            self.last_max_min_update_time = current_time

        time_since_last_change = current_time - self.last_max_min_update_time
        if time_since_last_change > self.stable_duration:
            amplitude = self.phase_max_error - self.phase_min_error
            if amplitude > self.minimum_oscillation_amplitude:
                print(f"Oscillation detected: Max error: {self.phase_max_error:.2f}, Min error: {self.phase_min_error:.2f}, Amplitude: {amplitude:.2f} "
                      f"for longer than {self.stable_duration}s")
                raise KeyboardInterrupt

    def calculate_output(self, process_variable, setpoint, dt):
        # Get the current time (using time.time() if hs doesn't provide one)
        current_time = hs.current_time() if hasattr(hs, 'current_time') else time()

        # Calculate current error and detect oscillations before PID computations
        error = setpoint - process_variable

        if self.phase == 'initial_stabilization' and self.phase_start_time == 0:
            self.reset_oscillation_detection(current_time)
        elif self.phase == 'transition' and self.phase_start_time == 0:
            self.reset_oscillation_detection(current_time)
        elif self.phase == 'final_stabilization' and self.phase_start_time == 0:
            self.reset_oscillation_detection(current_time)

        self.detect_oscillation(error, current_time)


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
                # Dwell at this setpoint for the specified time
                self.dwell_counter += dt
                if self.dwell_counter >= self.dwell_time:
                    self.phase = 'transition'
                    self.setpoint_index = 1
                    self.target_setpoint = self.setpoints[self.setpoint_index]
                    self.dwell_counter = 0
                    self.is_dwelling = False
                    self.phase_start_time = 0 # Reset for next phase oscillation detection
                    print(f"Dwell complete, transitioning to {self.target_setpoint}°C (25%)")

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

            # Once reached, wait for stabilization and dwell
            if self.current_setpoint == self.target_setpoint:
                if not self.is_dwelling:
                    if self.check_stability(process_variable, dt, self.stable_threshold, self.stable_duration):
                        print(f"Stabilized at {self.current_setpoint}°C, dwelling for {self.dwell_time} seconds")
                        self.is_dwelling = True
                        self.stable_time = 0  # Reset timer
                else:
                    self.dwell_counter += dt
                    if self.dwell_counter >= self.dwell_time:
                        self.setpoint_index += 1
                        self.dwell_counter = 0
                        self.is_dwelling = False
                        self.phase_start_time = 0 # Reset for next phase oscillation detection

                        if self.setpoint_index < len(self.setpoints):
                            self.target_setpoint = self.setpoints[self.setpoint_index]
                            if self.setpoint_index == self.drag_test_index:
                                self.ramp_rate = 0.1
                            else:
                                self.ramp_rate = 100
                            print(f"Dwell complete, transitioning to {self.target_setpoint}°C")
                        else:
                            self.phase = 'final_stabilization'
                            self.phase_start_time = 0 # Reset for next phase oscillation detection
                            print(f"All setpoints tested, finalizing at {self.current_setpoint}°C")

        elif self.phase == 'final_stabilization':
            # Final stabilization and dwell at the last setpoint
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

        # PID calculations
        proportional = self.kp * error
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        self.prev_error = error

        previous_integral = self.integral
        self.integral += error * dt

        output = proportional + self.ki * self.integral + self.kd * derivative

        # Check for saturation and prevent windup
        if output > self.max_output:
            output = self.max_output
            self.integral = previous_integral
        elif output < self.min_output:
            output = self.min_output
            self.integral = previous_integral

        return output