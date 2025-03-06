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
import argparse
import uuid

class Main:
    dt = 0.8                   # Delta time (s)
    sim_mass = 40.0             # Mass of simulated object (kg)
    sim_specific_heat = 500.0   # Specific heat capacity (J/(kg*K))

    selected_tuner = Skogestad  # Tuning method (None is no tuning)
    # Each tuning method stores the measured system dynamics
    # Only the PID variables will be recalculated based on the stored dynamics
    load_from_config = False    # Use stored dynamics when True

    selected_pid = EvaluateParallelPID # Selected PID controller

    setpoint = 100              # Target temperature
    max_output = 100            # Max heater output
    min_output = 0              # Min heater output

    delay = 4.0                # Simulated delay / dead-time (s)
    noise = 0.0                # Simulated temperature sensor noise
    
    experiment = -1
    experiment_set_id = -1

    def __init__(self):
        parser = argparse.ArgumentParser(description='Heat Simulation with PID Control')
        parser.add_argument('--tuner', type=str, default=None, help="Which tuner to use", choices=['astrom_hagglund', 'skogestad'])
        parser.add_argument('--dt', type=float, default=self.dt, help='Delta time (s)')
        parser.add_argument('--sim_mass', type=float, default=self.sim_mass, help='Mass of simulated object (kg)')
        parser.add_argument('--sim_specific_heat', type=float, default=self.sim_specific_heat, help='Specific heat capacity (J/(kg*K))')
        parser.add_argument('--setpoint', type=float, default=self.setpoint, help='Target temperature (°C)')
        parser.add_argument('--delay', type=float, default=self.delay, help='Simulated delay / dead-time (s)')
        parser.add_argument('--noise', type=float, default=self.noise, help='Simulated temperature sensor noise')
        parser.add_argument('--experiment', type=int, default=-1, help='Number to identify different experiments')
        parser.add_argument('--experiment_set_id', type=uuid.UUID, default=-1, help='Unique id to identify sets of experiments')

        args = parser.parse_args()
        
        if args.tuner == 'astrom_hagglund':
            self.selected_tuner = AstromHagglund
        elif args.tuner == 'skogestad':
            self.selected_tuner = Skogestad

        self.dt = args.dt
        self.sim_mass = args.sim_mass
        self.sim_specific_heat = args.sim_specific_heat
        self.setpoint = args.setpoint
        self.delay = args.delay
        self.noise = args.noise
        self.experiment = args.experiment
        self.experiment_set_id = args.experiment_set_id

        self.plot = Plotter(
            chosen_tuner=self.selected_tuner,
            dt=self.dt,
            mass=self.sim_mass,
            specific_heat=self.sim_specific_heat,
            simulated_delay=self.delay,
            simulated_noise=self.noise,
            experiment_set_id=self.experiment_set_id,
            experiment=self.experiment
        )

        pid_config.setpoint = self.setpoint # Used to update the setpoint from different modules for plotting

    def main(self):
        sim = hs.HeatSim(self.dt, mass=self.sim_mass, specific_heat=self.sim_specific_heat, delay=self.delay, noise=self.noise)
        sim_time = 0                # Cumulative delta time (s)
        tuning_done_time = -1.0     # Time it took to tune the system (-1 if no tuning occured)

        # PID variables from config file
        # The config file lets modules sync their PID settings between each other
        last_p = pid_config.kp
        last_i = pid_config.ki
        last_d = pid_config.kd
        
        cycle_count = 0
        print_interval = int(1 / self.dt)

        # Selected tuner is None when we don't want to tune the system
        if self.selected_tuner == None:
            pid = self.selected_pid(self.max_output, self.min_output, kp, ki, kd)
        else:
            pid = self.selected_tuner(load_from_config=self.load_from_config)

        try:
            while True:
                # Potentially update PID variables with newly tuned variables
                kp = pid_config.kp
                ki = pid_config.ki
                kd = pid_config.kd

                # If PID variables were updated
                if (last_p != kp or last_i != ki or last_d != kd):
                    # The settings changed during execution
                    # Reset the selected (potentially different) pid controller with new settings
                    pid = self.selected_pid(self.max_output, self.min_output, kp, ki, kd) # Switch to selected PID control
                    last_p = kp
                    last_i = ki
                    last_d = kd
                    print('PID config changed - Kp: ' + str(pid_config.kp) + ' | Ki: ' + str(pid_config.ki) + ' | Kd: ' + str(pid_config.kd))

                    if not self.load_from_config:               # Only if we are measuring the system dynamics
                        tuning_done_time = sim_time - self.dt   # Remove one dt otherwise we get one datapoint from the eval phase in the tune plot

                process_variable = sim.read_temperature() # Get new measured temperature
                pid_output = pid.calculate_output(process_variable, pid_config.setpoint, self.dt) # Calculate new actuation strength based on new temperature
                sim.update(pid_output) # Update sim with new actuation

                # sleep(self.dt) # Wait for delta time
                if cycle_count == print_interval:
                    print('Current Temp: ' + str(round(process_variable, 2)) + '°C | PID Output: ' + str(round(pid_output, 1)) + '%')
                    cycle_count = 0
                
                self.plot.add_temperature(process_variable, self.dt, pid_output, pid_config.setpoint) # Add data point to plot
                
                cycle_count+=1
                sim_time += self.dt # Add delta time to total time
        except KeyboardInterrupt:
            # Excepts when evaluation is done, or when user presses Ctrl+C
            self.plot.plot(tuning_done_time)
            if self.experiment == -1: 
                self.plot.show()
                
            sys.exit(0)

if __name__ == "__main__":
    main_instance = Main()
    main_instance.main()