from abc import ABC, abstractmethod
class PID(ABC):
    
    stable_buffer = []

    @property
    @abstractmethod
    def __init__(self, max_output, min_output, kp = 20.0, ki = 0.12, kd = 0.06):
        pass
    
    @property
    @abstractmethod
    def calculate_output(self, process_variable, setpoint, dt):
        pass
        
    def check_stability(self, current_value: float, initial_value, dt: float, threshold: float, duration: float = 5.0) -> bool:
        stable_samples_required = int(duration / dt)
        # Update stability buffer
        self.stable_buffer.append(current_value)
        
        # Prevent from reaching stabilization before the value moves
        if abs(initial_value - current_value) <= threshold * 2:
            self.stable_buffer = []
        
        if len(self.stable_buffer) > stable_samples_required:
            self.stable_buffer.pop(0)
        
        # Check if values have been stable for the required duration
        is_stable = (len(self.stable_buffer) == stable_samples_required and
                    (max(self.stable_buffer) - min(self.stable_buffer) < threshold))
        
        return is_stable

    def get_stabilized_output(self) -> float:
        # Return the average of last 20% of the stable buffer
        return sum(self.stable_buffer[int(-0.2 * len(self.stable_buffer)):]) / len(self.stable_buffer[int(-0.2 * len(self.stable_buffer)):])
