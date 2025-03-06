from collections import deque
from pid_controllers.pid import PID
from pid_controllers.parallel_pid import Parallel_PID
import pid_config
from abc import ABC, abstractmethod
import sys
import heat_simulation.heat_sim as hs
from time import sleep, time
import numpy as np
import math

class EvaluateParallelPID(PID):
    def __init__(self, max_output, min_output, kp, ki, kd):
        super().__init__(kp, ki, kd)
        self.max_output = max_output
        self.min_output = min_output
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.pid = Parallel_PID(max_output, min_output, kp, ki, kd)

        self.initial_setpoint = 100
        self.setpoints = [
            self.initial_setpoint,
            self.initial_setpoint * 0.40,
            self.initial_setpoint * 0.60,  # Drag test
            self.initial_setpoint * 1.10,
        ]
        self.drag_test_index = 2
        self.current_setpoint = self.initial_setpoint
        self.target_setpoint = self.initial_setpoint
        self.setpoint_index = 0
        self.ramp_rate = 100
        self.slow_ramp_rate = 0.1

        self.phase = 'initial_stabilization'
        self.stable_threshold = 0.4
        self.stable_duration = 5.0
        self.dwell_time = 10.0
        self.stable_time = 0
        self.dwell_counter = 0
        self.evaluation_complete = False
        self.is_dwelling = False

        self.output_history = deque(maxlen=200)  # Stores (timestamp, output_value)
        self.periods = deque(maxlen=5)           # Buffer for last 3 periods
        self.amplitudes = deque(maxlen=5)        # Buffer for last 3 amplitudes
        self.last_max = (None, None)             # (time, value)
        self.last_min = (None, None)             # (time, value)
        self.direction = None
        self.oscillation_count = 0
        self.max_oscillations = 4                # Require 4 consistent cycles
        self.deadband = 5.0                      # Minimum output change to consider
        self.min_amplitude = (max_output - min_output) * 0.05  # 5% of output range
        self.period_variation = 0.15             # 15% period variation allowed
        self.amp_variation = 0.15                # 15% amplitude variation allowed

        # Error History for derivative filtering
        self.derivative_filter = deque(maxlen=5)

        # Time tracking
        self.last_time = time()
        self.total_time = 0

    def _update_time(self):
        current_time = hs.current_time() if hasattr(hs, 'current_time') else time()
        dt = current_time - self.last_time
        self.last_time = current_time
        return dt

    def _check_stability(self, process_variable, dt):
        if abs(process_variable - self.current_setpoint) < self.stable_threshold:
            self.stable_time += dt
            if self.stable_time >= self.stable_duration:
                return True
        else:
            self.stable_time = 0
        return False

    
    def _detect_oscillation(self):
        # Failsafe
        if self.total_time > 3000:
            print("Failsafe: Ran too long.")
            raise KeyboardInterrupt()
        
        # 
        # Oscillation detection currently commented out. It's not reliable enough
        # 
        
        # if len(self.output_history) < 2:
        #     return

        # # Get current and previous output values
        # (t1, y1), (t0, y0) = self.output_history[-1], self.output_history[-2]
        
        # # Calculate output change and determine direction
        # delta = y1 - y0
        # if abs(delta) < self.deadband:
        #     return  # Ignore small changes
        
        # new_direction = 'rising' if delta > 0 else 'falling'
        
        # # Detect peak when direction changes
        # if self.direction and new_direction != self.direction:
        #     # Previous point was a peak
        #     peak_time, peak_value = t0, y0
        #     peak_type = 'max' if self.direction == 'rising' else 'min'
            
        #     # Update period and amplitude buffers
        #     if peak_type == 'max':
        #         if self.last_max[0] is not None:
        #             self.periods.append(peak_time - self.last_max[0])
        #             if self.last_min[1] is not None:
        #                 self.amplitudes.append(peak_value - self.last_min[1])
        #         self.last_max = (peak_time, peak_value)
        #     else:
        #         if self.last_min[0] is not None:
        #             self.periods.append(peak_time - self.last_min[0])
        #             if self.last_max[1] is not None:
        #                 self.amplitudes.append(self.last_max[1] - peak_value)
        #         self.last_min = (peak_time, peak_value)
            
        #     # Check for consistent oscillations
        #     if len(self.periods) >= 3 and len(self.amplitudes) >= 3:
        #         # Calculate variation metrics
        #         period_cv = np.std(self.periods) / np.mean(self.periods)
        #         amp_cv = np.std(self.amplitudes) / np.mean(self.amplitudes)
                
        #         # Check consistency thresholds
        #         if (period_cv < self.period_variation and 
        #             amp_cv < self.amp_variation and
        #             np.mean(self.amplitudes) > self.min_amplitude):
        #             self.oscillation_count += 1
        #         else:
        #             self.oscillation_count = max(0, self.oscillation_count - 1)

        #         if self.oscillation_count >= self.max_oscillations:
        #             print("Consistent oscillations detected! Interrupting...")
        #             raise KeyboardInterrupt

        # self.direction = new_direction

    def _ramp_to_setpoint(self, dt):
        if self.current_setpoint < self.target_setpoint:
            self.current_setpoint += self.ramp_rate * dt
            if self.current_setpoint > self.target_setpoint:
                self.current_setpoint = self.target_setpoint
        elif self.current_setpoint > self.target_setpoint:
            self.current_setpoint -= self.ramp_rate * dt
            if self.current_setpoint < self.target_setpoint:
                self.current_setpoint = self.target_setpoint

    def _handle_initial_stabilization(self, process_variable, dt):
        if not self.is_dwelling:
            if self._check_stability(process_variable, dt):
                print(f"Stabilized at {self.current_setpoint}°C, dwelling for {self.dwell_time} seconds")
                self.is_dwelling = True
                self.reset_oscillation_detection()
        else:
            self.dwell_counter += dt
            if self.dwell_counter >= self.dwell_time:
                self.phase = 'transition'
                self.setpoint_index = 1
                self.target_setpoint = self.setpoints[self.setpoint_index]
                self.dwell_counter = 0
                self.is_dwelling = False
                self.ramp_rate = 100
                self.reset_oscillation_detection()
                print(f"Dwell complete, transitioning to {self.target_setpoint}°C")

    def _handle_transition(self, process_variable, dt):
        self._ramp_to_setpoint(dt)

        if self.current_setpoint == self.target_setpoint:
            if not self.is_dwelling:
                if self._check_stability(process_variable, dt):
                    print(f"Stabilized at {self.current_setpoint}°C, dwelling for {self.dwell_time} seconds")
                    self.is_dwelling = True
                    self.reset_oscillation_detection()
            else:
                self.dwell_counter += dt
                if self.dwell_counter >= self.dwell_time:
                    self.setpoint_index += 1
                    self.dwell_counter = 0
                    self.is_dwelling = False
                    self.reset_oscillation_detection()

                    if self.setpoint_index < len(self.setpoints):
                        self.target_setpoint = self.setpoints[self.setpoint_index]
                        if self.setpoint_index == self.drag_test_index:
                            self.ramp_rate = self.slow_ramp_rate
                        else:
                            self.ramp_rate = 100
                        print(f"Dwell complete, transitioning to {self.target_setpoint}°C")
                    else:
                        self.phase = 'final_stabilization'
                        self.reset_oscillation_detection()
                        print(f"All setpoints tested, finalizing at {self.current_setpoint}°C")

    def _handle_final_stabilization(self, process_variable, dt):
        if not self.is_dwelling:
            if self._check_stability(process_variable, dt):
                print(f"Stabilized at final setpoint, dwelling for {self.dwell_time} seconds")
                self.is_dwelling = True
                self.reset_oscillation_detection()
        else:
            self.dwell_counter += dt
            if self.dwell_counter >= self.dwell_time:
                self.evaluation_complete = True
                print("Evaluation complete")
                raise KeyboardInterrupt

    def calculate_output(self, process_variable, setpoint, dt=None):
        pid_config.setpoint = self.current_setpoint

        if dt is None:
            dt = self._update_time()
        if dt <= 0 or dt > 1:
            return 0

        self.total_time += dt
        
        if self.phase == 'initial_stabilization':
            self._handle_initial_stabilization(process_variable, dt)
        elif self.phase == 'transition':
            self._handle_transition(process_variable, dt)
        elif self.phase == 'final_stabilization':
            self._handle_final_stabilization(process_variable, dt)
        if self.evaluation_complete:
            return self.min_output
        output = self.pid.calculate_output(process_variable, self.current_setpoint, dt)
        
        self.output_history.append((time(), output))
        
        try:
            self._detect_oscillation()
        except KeyboardInterrupt:
            self.evaluation_complete = True
            raise

        return output

    def reset_oscillation_detection(self):
        self.output_history.clear()
        self.periods.clear()
        self.amplitudes.clear()
        self.last_max = (None, None)
        self.last_min = (None, None)
        self.direction = None
        self.oscillation_count = 0