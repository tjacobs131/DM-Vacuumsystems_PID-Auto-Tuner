import sys
import HeatSim.heat_sim as hs
from Plotter.plotter import Plotter
from time import sleep
from PID.parallel_pid import Parallel_PID
import pid_config
from Tuners import astrom_hagglund, skogestad

class Main:
    dt = 0.04
    last_p = pid_config.kp
    last_i = pid_config.ki
    last_d = pid_config.kd
    
    selected_tuner = skogestad.Skogestad
    selected_pid = Parallel_PID

    heater_power = 0 # (%)

    def __init__(self):
        pass

    def main(self):
        sim = hs.HeatSim(self.dt, delay=0.2)
        plot = Plotter()
        
        if self.selected_tuner == None:
            pid = self.selected_pid(kp, ki, kd)
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
                    pid = self.selected_pid(kp, ki, kd)
                    self.last_p = kp
                    self.last_i = ki
                    self.last_d = kd
                    print('PID config changed - Kp: ' + str(pid_config.kp) + ' | Ki: ' + str(pid_config.ki) + ' | Kd: ' + str(pid_config.kd))

                # Get heater power
                process_variable = sim.read_temperature()
                pid_output = pid.calculate_output(process_variable, 100, self.dt)

                # Add a smoothing factor based on dt
                tau = 0.05  # Time constant for lag effect
                alpha = self.dt / (tau + self.dt)  # Exponential smoothing factor

                # Update heater power with lag
                self.heater_power = (1 - alpha) * self.heater_power + alpha * pid_output

                # Clamp heater power
                self.heater_power = max(0, min(100, self.heater_power))

                sim.update(self.heater_power)

                # Wait for delta time
                sleep(self.dt)

                print('Current Temp: ' + str(round(sim.read_temperature(), 1)) + '°C | Heater Power: ' + str(round(self.heater_power, 1)) + '%')
                plot.add_temperature(sim.read_temperature())
        except KeyboardInterrupt:
            plot.plot()
            plot.show()
            sys.exit(0)

if __name__ == "__main__":
    Main.main(Main())