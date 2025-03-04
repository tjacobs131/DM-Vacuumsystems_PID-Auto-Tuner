import sys
import heat_simulation.heat_sim as hs
from plotters.plot_pid_sim import Plotter
from time import sleep
from pid_controllers.parallel_pid import Parallel_PID
from pid_controllers.evaluate_parallel_pid import EvaluateParallelPID
import pid_config
from tuners.astrom_hagglund import AstromHagglund
from tuners.skogestad import Skogestad
from tuners.tuner import Tuner

class Main:
    dt = 0.02
    sim_time = 0
    
    sim_mass = 40.0
    sim_specific_heat = 500.0
    
    last_p = pid_config.kp
    last_i = pid_config.ki
    last_d = pid_config.kd
    
    selected_tuner = Skogestad
    load_from_config = True
    selected_pid = EvaluateParallelPID

    heater_power = 0 # (%)
    setpoint = 100
    max_output = 100
    min_output = 0

    delay = 30.0
    noise = 0.02
    
    done_tuning_time = -1.0

    def __init__(self):
        self.plot = Plotter(
            chosen_tuner=self.selected_tuner,
            dt=self.dt,
            mass=self.sim_mass,
            specific_heat=self.sim_specific_heat,
            simulated_delay=self.delay,
            simulated_noise=self.noise,
        )

        pid_config.setpoint = 100

    def main(self):
        sim = hs.HeatSim(self.dt, mass=self.sim_mass, specific_heat=self.sim_specific_heat, delay=self.delay, noise=self.noise)
        
        if self.selected_tuner == None:
            pid = self.selected_pid(self.max_output, self.min_output, kp, ki, kd)
        else:
            pid = self.selected_tuner(load_from_config=self.load_from_config)

        try:
            while True:
                self.sim_time += self.dt
                
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
                    
                    if not self.load_from_config: # Only if we are measuring the system dynamics again
                        self.done_tuning_time = self.sim_time - self.dt # We remove one dt otherwise we get one datapoint from the eval phase

                # Get heater power
                process_variable = sim.read_temperature()
                pid_output = pid.calculate_output(process_variable, pid_config.setpoint, self.dt)

                sim.update(pid_output)

                # Wait for delta time
                # sleep(self.dt)

                print('Current Temp: ' + str(round(process_variable, 2)) + '°C | PID Output: ' + str(round(pid_output, 1)) + '%')
                self.plot.add_temperature(process_variable, self.dt, pid_output, pid_config.setpoint)
        except KeyboardInterrupt:
            self.plot.plot(self.done_tuning_time)
            self.plot.show()
            sys.exit(0)

if __name__ == "__main__":

    Main.main(Main())