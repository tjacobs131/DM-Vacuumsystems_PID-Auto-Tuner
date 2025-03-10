from tuners.tuner import Tuner
import pid_config
from typing import List
import os

class Skogestad(Tuner):
    final_cooldown = False
    initial_output = 40
    step_amplitude = 20

    current_output = initial_output
    baseline = None
    reached_baseline = False

    time_data = []
    output_data = []

    stable_threshold = 0.3

    dead_time = None
    rise_time = None
    lambda_param = None
    k = None

    initial_process_variable = None

    def __init__(self, load_from_config: bool):
        self.load_from_config = load_from_config
        if load_from_config and os.path.exists("tuner_config.ini"):
            conf = Tuner.load_tuner_config("skogestad", self.get_config_names())
            if conf:
                self.load_config(conf)
                self.final_cooldown = True
                self.cooldown_start_temp = 9999
        else:
            self.time_data = []
            self.output_data = []

    def calculate_output(self, process_variable: float, setpoint: float, dt: float) -> float:
        if self.initial_process_variable is None:
            self.initial_process_variable = process_variable
        self.time_data.append(dt)
        self.output_data.append(process_variable)

        if self.final_cooldown:
            if self.check_stability(process_variable, dt, self.stable_threshold, self.cooldown_start_temp, 30):
                k1 = 0.5
                self.lambda_param = max(self.dead_time, dt)
                Kp = self.rise_time / (self.k * (self.lambda_param + self.dead_time))
                Ti = min(self.rise_time, k1 * (self.lambda_param + self.dead_time))
                # Ti = k1 * (self.lambda_param + self.dead_time)
                pid_config.kp = Kp
                pid_config.ki = Kp / Ti
                pid_config.kd = 0
                Tuner.store_tuner_config("skogestad", self.get_config())
            return 0

        if not self.reached_baseline:
            if self.check_stability(process_variable, dt, self.stable_threshold, self.initial_process_variable, 15):
                self.current_output = self.initial_output + self.step_amplitude
                self.baseline = process_variable
                self.reached_baseline = True
                self.step_time = 0
            return self.current_output
        else:
            self.step_time += dt
            if self.check_stability(process_variable,dt, self.stable_threshold, self.baseline, 15):
                final_output = self.get_stabilized_output()
                self.k = (final_output - self.baseline) / self.step_amplitude
                self.dead_time = 0
                lowest_y = float("inf")
                for i, y in enumerate(self.output_data):
                    if y < lowest_y:
                        lowest_y = y
                    self.dead_time += self.time_data[i]
                    if y >= lowest_y + 0.005 * (final_output - lowest_y):
                        self.dead_time -= dt
                        break

                target = self.baseline + 0.632 * (final_output - self.baseline)
                self.rise_time = 0
                for i, y in enumerate(self.output_data):
                    self.rise_time += self.time_data[i]
                    if y >= self.baseline:
                        self.baseline = 99999
                        self.baseline_time = self.rise_time
                    if y >= target:
                        break
                self.rise_time -= self.baseline_time
                if self.rise_time <= 0:
                    self.rise_time = dt
                self.cooldown_start_temp = process_variable
                self.final_cooldown = True
                return 0
            return self.current_output

    def get_config(self) -> dict:
        return {
            "rise_time": self.rise_time,
            "k": self.k,
            "dead_time": self.dead_time
        }

    def load_config(self, config: dict):
        self.rise_time = float(config.get("rise_time", 0))
        self.k = float(config.get("k", 0))
        self.dead_time = float(config.get("dead_time", 0))

    def get_config_names(self) -> List[str]:
        return ["rise_time", "k", "dead_time"]
