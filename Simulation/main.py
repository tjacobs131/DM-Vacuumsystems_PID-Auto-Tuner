import sys
import heat_simulation.heat_sim as hs
from plotters.temp_controller_output_plot import Plotter
from time import sleep
from pid_controllers.parallel_pid import Parallel_PID
from pid_controllers.evaluate_parallel_pid import EvaluateParallelPID
import pid_config
from tuners.astrom_hagglund import AstromHagglund
from tuners.skogestad import Skogestad

class Main:
    dt = 0.04
    last_p = pid_config.kp
    last_i = pid_config.ki
    last_d = pid_config.kd
    
    selected_tuner = Skogestad
    selected_pid = EvaluateParallelPID

    heater_power = 0 # (%)
    setpoint = 100
    max_output = 100
    min_output = 0

    delay = 8.0
    noise = 0.02

    def __init__(self):
        self.plot = Plotter(
            chosen_tuner=self.selected_tuner,
            max_output=self.max_output,
            min_output=self.min_output,
            simulated_delay=self.delay,
            simulated_noise=self.noise
        )

        pid_config.setpoint = 100

    def main(self):
        sim = hs.HeatSim(self.dt, delay=self.delay, noise=self.noise)
        
        if self.selected_tuner == None:
            pid = self.selected_pid(self.max_output, self.min_output, kp, ki, kd)
        else:
            pid = self.selected_tuner()

        try:
            while True:
                kp = pid_config.kp
                ki = pid_config.ki
                kd = pid_config.kd

                if (self.last_p != kp or self.last_i != ki or self.last_d != kd):
                    # The settings changed during execution
                    # Reset the selected (potentially different) pid controller with new settings
                    pid = self.selected_pid(self.max_output, self.min_output, kp, ki, kd)
                    self.last_p = kp
                    self.last_i = ki
                    self.last_d = kd
                    print('PID config changed - Kp: ' + str(pid_config.kp) + ' | Ki: ' + str(pid_config.ki) + ' | Kd: ' + str(pid_config.kd))

                # Get heater power
                process_variable = sim.read_temperature()
                pid_output = pid.calculate_output(process_variable, pid_config.setpoint, self.dt)

                sim.update(pid_output)

                # Wait for delta time
                # sleep(self.dt)

                print('Current Temp: ' + str(round(process_variable, 2)) + '°C | PID Output: ' + str(round(pid_output, 1)) + '%')
                self.plot.add_temperature(process_variable, self.dt, pid_output, pid_config.setpoint)
        except KeyboardInterrupt:
            self.plot.plot()
            self.plot.show()
            sys.exit(0)

if __name__ == "__main__":

    Main.main(Main())