from pid_controllers.pid import PID
import pid_config

class Skogestad(PID):
    final_cooldown = False

    initial_output = 40
    step_amplitude = 10
    step_time = 0

    current_output = initial_output

    baseline = None
    reached_baseline = False

    time_data = []
    output_data = []

    stable_threshold = 0.3  # allowed variation in °C

    dead_time = None
    rise_time = None  # estimated process time constant τ
    lambda_param = None  # closed-loop time constant λ
    k = None  # process gain

    def __init__(self):
        pass

    def calculate_output(self, process_variable: float, setpoint: float, dt: float) -> float:
        # If in final cooldown, compute PID settings according to SIMC rules.
        if self.final_cooldown:
            if abs(self.cooldown_start_temp - process_variable) <= self.stable_threshold * 2:
                self.stable_buffer = []
            if (self.check_stability(process_variable, dt, self.stable_threshold, 5)):
                
                # SIMC formulas for a PI controller (first-order plus delay process):
                # Kp = τ / (K*(λ + θ))
                # Ti = min(τ, k1*(λ + θ))
                k1 = 10  # Lower this for faster disturbance rejection
                # Choose λ as a user-tunable parameter, here we ensure it is at least the dead time.
                self.lambda_param = max(self.dead_time, dt)
                Kp = self.rise_time / (self.k * (self.lambda_param + self.dead_time))
                Ti = min(self.rise_time, k1 * (self.lambda_param + self.dead_time))
                # Assuming a parallel PID form: controller = Kp*(1 + 1/(Ti*s))
                pid_config.kp = Kp
                pid_config.ki = Kp / Ti  # if controller uses ki = Kp/Ti
                pid_config.kd = 0       # no derivative action for a PI controller
                
            return 0
            

        # Before reaching baseline, apply a step and record baseline.
        if not self.reached_baseline:
            if self.check_stability(process_variable, dt, self.stable_threshold):
                self.current_output = self.initial_output + self.step_amplitude
                self.stable_buffer = []
                self.baseline = process_variable
                self.reached_baseline = True
                # Reset measurement data for the post-step experiment
                self.time_data = [0]
                self.output_data = [process_variable]
                self.step_time = 0
            return self.current_output
        else:
            # Collect data after the step is applied.
            self.step_time += dt
            self.time_data.append(self.step_time)
            self.output_data.append(process_variable)

            if self.check_stability(process_variable, dt, self.stable_threshold):
                # The output has stabilized.
                final_output = self.get_stabilized_output()
                self.stable_buffer = []
                # Process gain: output change divided by step amplitude.
                self.k = (final_output - self.baseline) / self.step_amplitude

                # Estimate dead time (θ): first time when output increases by 2% of total change.
                self.dead_time = None
                for i, y in enumerate(self.output_data):
                    if y >= self.baseline + 0.02 * (final_output - self.baseline):
                        self.dead_time = i * dt
                        break
                if self.dead_time is None:
                    self.dead_time = 0

                # Estimate rise time (τ): time from end of dead time to reaching 63.2% of the total change.
                target = self.baseline + 0.632 * (final_output - self.baseline)
                self.rise_time = None
                for i, y in enumerate(self.output_data):
                    if y >= target:
                        self.rise_time = i * dt - self.dead_time
                        break
                if self.rise_time is None or self.rise_time < 0:
                    self.rise_time = dt  # fallback if estimation fails

                self.cooldown_start_temp = process_variable
                self.final_cooldown = True
                return 0

            return self.current_output
