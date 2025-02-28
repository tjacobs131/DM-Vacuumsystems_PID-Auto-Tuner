import HeatSim.heat_sim as hs
from PID.parallel_pid import Parallel_PID
from Plotter.plotter import Plotter
from time import sleep

import sys

class Main:
    dt = 0.05

    def __init__(self):
        pass

    def main(self):
        sim = hs.HeatSim(self.dt)
        pid = Parallel_PID(100, self.dt)
        plot = Plotter()

        heater_power = 100 # (%)
        
        stable_buffer = []
        stable_threshold = 0.5  # allowed variation in °C
        stable_samples_required = int(5 / self.dt)  # number of samples in 5 seconds
        setpoint_changed = False

        try:
            while True:
                # Update stability buffer
                stable_buffer.append(sim.read_temperature())
                if len(stable_buffer) > stable_samples_required:
                    stable_buffer.pop(0)
                
                # Check if temperature has been stable for 5 seconds
                if (len(stable_buffer) == stable_samples_required and 
                    (max(stable_buffer) - min(stable_buffer) < stable_threshold) and 
                    not setpoint_changed):
                    # We can now step up the heater power
                    pass
                
                # Get heater power
                process_variable = sim.read_temperature()
                heater_power = pid.get_output(process_variable)

                # Clamp heater power
                if heater_power < 0:
                    heater_power = 0
                elif heater_power > 100:
                    heater_power = 100

                sim.update(heater_power)

                # Wait for delta time
                sleep(self.dt)

                print('Current Temp: ' + str(round(sim.read_temperature(), 1)) + '°C | Heater Power: ' + str(round(heater_power, 1)) + '%')
                plot.add_temperature(sim.read_temperature())
        except KeyboardInterrupt:
            plot.plot()
            plot.show()
            sys.exit(0)

if __name__ == "__main__":
    Main.main(Main())