from collections import deque
from abc import ABC, abstractmethod
import sys
import pid_config

class PID(ABC):
    stable_buffer = []
    last_initial_value = None

    def __init__(self, max_output, min_output, kp=20.0, ki=0.12, kd=0.06):
        self.max_output = max_output
        self.min_output = min_output
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.previous_error = 0.0

    @abstractmethod
    def calculate_output(self, process_variable, setpoint, dt):
        pass

    def check_stability(self, current_value: float, dt: float, threshold: float, initial_value=None, duration: float = 5.0) -> bool:
        if initial_value != self.last_initial_value:
            self.last_initial_value = initial_value
            self.stable_buffer = []
        
        stable_samples_required = int(duration / dt)
        self.stable_buffer.append(current_value)
        
        if initial_value is not None and abs(initial_value - current_value) <= threshold * 2:
            self.stable_buffer = []
        
        if len(self.stable_buffer) > stable_samples_required:
            self.stable_buffer.pop(0)
        
        is_stable = (len(self.stable_buffer) == stable_samples_required and
                    (max(self.stable_buffer) - min(self.stable_buffer) < threshold))
        return is_stable

    def get_stabilized_output(self) -> float:
        stabilized_part = self.stable_buffer[int(-0.2 * len(self.stable_buffer)):]
        return sum(stabilized_part) / len(stabilized_part)