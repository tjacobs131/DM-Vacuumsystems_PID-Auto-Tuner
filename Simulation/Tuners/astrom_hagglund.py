from pid_controllers.parallel_pid import Parallel_PID
import pid_config
import math
from typing import List
from tuners.tuner import Tuner
import os

class AstromHagglund(Parallel_PID):
    def __init__(self, target_iterations: int = 10, load_from_config: bool = False):
        # Config averaging parameters
        self.pAvg = 0
        self.iAvg = 0
        self.dAvg = 0
        self.iterations = 0
        self.iterations_to_skip = 1
        self.target_iterations = target_iterations

        # PID gains (calculated later)
        self.kp = 0
        self.ki = 0
        self.kd = 0

        # Ultimate gain and period
        self.ku = 0
        self.tu = 0

        # Mode and output
        self.heating = True
        self.max_controller_output = 100
        self.min_controller_output = 0
        self.controller_output = self.max_controller_output

        # Timer and switching times
        self.timer = 0
        self.time1 = 0
        self.time2 = 0
        self.thigh = 0
        self.tlow = 0

        # Recorded extreme values
        self.max_recorded_output = -float('inf')
        self.min_recorded_output = float('inf')

        # Final flag (once testing is done or config loaded)
        self.final_cooldown = False
        self.stable_threshold = 0.5

        # If a config is available, skip system testing.
        if load_from_config and os.path.exists("tuner_config.ini"):
            conf = Tuner.load_tuner_config("astromhagglund", self.get_config_names())
            if conf:
                self.load_config(conf)
                self.heating = False
                self.final_cooldown = True

    def calculate_output(self, process_variable: float, setpoint: float, dt: float) -> float:
        # If in final cooldown, just output the minimum value and wait to stabilize
        if self.final_cooldown:
            if abs(self.cooldown_start_temp - process_variable) <= self.stable_threshold * 2:
                self.stable_buffer = []
            if self.check_stability(process_variable, dt, self.stable_threshold, 5):
                pid_config.kp = self.pAvg / self.iterations
                pid_config.ki = self.iAvg / self.iterations
                pid_config.kd = self.dAvg / self.iterations
                Tuner.store_tuner_config("astromhagglund", self.get_config())
            return self.min_controller_output

        # Check if all iterations have been completed.
        if self.iterations > self.target_iterations + self.iterations_to_skip:
            self.heating = False
            self.final_cooldown = True
            self.cooldown_start_temp = process_variable  
            # Save the averaged values to config.
            Tuner.store_tuner_config("astromhagglund", self.get_config())
            return self.min_controller_output

        # Record min/max process values.
        if process_variable > self.max_recorded_output:
            self.max_recorded_output = process_variable
        if process_variable < self.min_recorded_output:
            self.min_recorded_output = process_variable

        self.timer += dt

        # Switch between heating and cooling modes.
        if self.heating and process_variable > setpoint:
            self.heating = False
            self.time1 = self.timer
            self.thigh = self.time1 - self.time2
            self.max_recorded_output = setpoint
        elif not self.heating and process_variable < setpoint:
            self.heating = True
            self.time2 = self.timer
            self.tlow = self.time2 - self.time1

            amplitude_pv = self.max_recorded_output - self.min_recorded_output
            if amplitude_pv > 0:
                self.ku = (4 * self.max_controller_output - self.min_controller_output) / (math.pi * amplitude_pv)
                self.tu = self.thigh + self.tlow

                self.kp = 0.6 * self.ku
                self.ki = 0.5 * self.tu
                self.kd = 0.125 * self.tu

                if self.iterations >= self.iterations_to_skip:
                    self.pAvg += self.kp
                    self.iAvg += self.ki
                    self.dAvg += self.kd
                    
                       
                
                self.min_recorded_output = setpoint

                self.iterations += 1

        # Set controller output based on mode.
        self.controller_output = self.max_controller_output if self.heating else self.min_controller_output
        return self.controller_output

    def get_config(self) -> dict:
        # Save averages; later the PID gains are computed as avg / (iterations - skip)
        return {"pAvg": self.pAvg, "iAvg": self.iAvg, "dAvg": self.dAvg, "iterations": self.iterations}

    def load_config(self, config: dict):
        # Convert loaded values to float and assign.
        self.pAvg = float(config.get("pAvg", 0))
        self.iAvg = float(config.get("iAvg", 0))
        self.dAvg = float(config.get("dAvg", 0))
        self.iterations = int(config.get("iterations", self.iterations_to_skip))
        count = max(1, self.iterations - self.iterations_to_skip)
        pid_config.kp = self.pAvg / count
        pid_config.ki = self.iAvg / count
        pid_config.kd = self.dAvg / count

    def get_config_names(self) -> List[str]:
        return ["pAvg", "iAvg", "dAvg", "iterations"]