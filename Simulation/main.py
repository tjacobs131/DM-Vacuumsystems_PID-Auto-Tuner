import HeatSim.heat_sim as hs
from PID.pid import PID
from Plotter.plotter import Plotter
from time import sleep

import sys

class Main:
    dt = 0.05

    def __init__(self):
        pass

    def main(self):
        sim = hs.HeatSim(self.dt)
        pid = PID(100.0, 0.05, 0.2, 100, self.dt)
        plot = Plotter()
        heater_power = 100 # (%)

        try:
            while True:
                # Get heater power
                process_variable = sim.read_temperature()
                heater_power = pid.update_parallel(process_variable)

                if heater_power < 0:
                    heater_power = 0
                elif heater_power > 100:
                    heater_power = 100

                sim.update(heater_power)

                # Wait for delta time
                sleep(self.dt)

                print('Current Temp: ' + str(round(sim.read_temperature(), 1)) + ' | Heater Power: ' + str(heater_power))

                plot.add_temperature(sim.read_temperature())
        except KeyboardInterrupt:
            plot.plot()
            plot.show()
            sys.exit(0)

if __name__ == "__main__":
    Main.main(Main())