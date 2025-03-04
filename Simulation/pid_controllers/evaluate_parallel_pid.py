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
            self.initial_setpoint * 0.40,      # 25% of initial
            self.initial_setpoint * 0.60,      # Perform setpoint drag test at 50%
            self.initial_setpoint * 1.10       # 110% of initial
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
        self.is_dwelling = False              # Flag to track if we're in dwell phase

        # Variables for oscillation detection
        self.error_history = []             # Recent error values
        self.history_time = []              # Timestamps for the errors
        self.minimum_oscillation_amplitude = 0.1
        self.oscillation_threshold = 8      # How many oscillations before triggering (4 full cycles)
        self.history_duration = 60          # Increased from 10 seconds
        self.min_cycles_for_oscillation = 2  # Minimum number of complete cycles
        self.last_error_sign = 0            # Track the sign of the previous error for change detection

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
        """Oscillation detection for both high and low frequency oscillations"""
        self.error_history.append((current_time, error))
        
        # Purge old entries
        while self.error_history and (current_time - self.error_history[0][0] > self.history_duration):
            self.error_history.pop(0)

        if len(self.error_history) < 2:
            return

        # Calculate amplitude and sign changes
        errors = [e for (t, e) in self.error_history]
        max_error = max(errors)
        min_error = min(errors)
        amplitude = max_error - min_error

        # Calculate sign changes with deadband
        sign_changes = 0
        prev_sign = 0
        deadband = self.stable_threshold

        for t, e in self.error_history:
            current_sign = 0
            if e > deadband:
                current_sign = 1
            elif e < -deadband:
                current_sign = -1
            
            if prev_sign != 0 and current_sign != 0 and prev_sign != current_sign:
                sign_changes += 1
            prev_sign = current_sign if current_sign != 0 else prev_sign

        # Calculate number of complete cycles
        full_cycles = sign_changes // 2

        # Check oscillation conditions
        if (amplitude >= self.minimum_oscillation_amplitude and 
            full_cycles >= self.min_cycles_for_oscillation):
            print(f"Oscillation detected: {full_cycles} cycles in {self.history_duration}s "
                f"(Amplitude: {amplitude:.2f}°C)")
            raise KeyboardInterrupt

    def calculate_output(self, process_variable, setpoint, dt):
        # Get the current time (using time.time() if hs doesn't provide one)
        current_time = hs.current_time() if hasattr(hs, 'current_time') else time()

        # Calculate current error and detect oscillations before PID computations
        error = setpoint - process_variable
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