import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pid_config
from pid_controllers.pid import PID
import datetime
import os
from uuid import UUID
import numpy as np
from matplotlib.collections import LineCollection
from tuners.tuner import Tuner

class Plotter:
    def __init__(self,
                chosen_tuner,
                dt: float,
                mass: float,
                specific_heat: float,
                simulated_delay: float,
                simulated_noise: float,
                experiment_set_id: UUID,
                experiment: int):
        self.temperature = []
        self.controller_output = []
        self.setpoint = []
        self.dt = []
        self.chosen_tuner = str.split(chosen_tuner.__module__, '.')[1]
        self.mass = mass
        self.specific_heat = specific_heat
        self.delta_time = dt
        self.simulated_delay = simulated_delay
        self.simulated_noise = simulated_noise
        self.experiment_set_id = experiment_set_id
        self.experiment = experiment
        self.evaluation_time = 0

    def add_temperature(self, temperature, dt, controller_output, setpoint):
        # If it's the first reading, just append dt
        if not self.dt:
            self.dt.append(dt)
        else:
            # Otherwise, add dt to the last recorded time
            self.dt.append(self.dt[-1] + dt)
        self.temperature.append(temperature)
        self.controller_output.append(controller_output)
        self.setpoint.append(setpoint)

    def plot(self, done_tuning_time: float):
        self.tuning_time = done_tuning_time
        if self.tuning_time == -1:
            self._plot_single()
        else:
            self._plot_tuning_and_evaluation()

    def _plot_single(self):
        # Use all data in one plot
        self.kp = pid_config.kp
        self.ki = pid_config.ki
        self.kd = pid_config.kd

        fig, ax1 = plt.subplots(figsize=(12, 8))

        # Primary y-axis for temperature
        ax1.plot(self.dt, self.temperature, linestyle='-', color='blue', label="Temperature (°C)")
        ax1.plot(self.dt, self.setpoint, color='blue', linestyle='-', alpha=0.3, linewidth=1.8, label="Setpoint")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Temperature (°C)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.minorticks_on()
        ax1.grid(True, which='major', linestyle='-', linewidth=0.8, alpha=1.0)
        ax1.grid(True, which='minor', linestyle='-', linewidth=0.5, alpha=1.0)
        ax1.xaxis.set_major_locator(ticker.LinearLocator())
        ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))

        # Secondary y-axis for controller output
        ax2 = ax1.twinx()
        ax2.plot(self.dt, self.controller_output, linestyle='--', color='orange', linewidth=1.1, label="Controller Output (%)")
        ax2.set_ylabel("Controller Output (%)", color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

        plt.title(f"Evaluation Phase Data\nPID Tuner: {self.chosen_tuner}",
                  fontsize=14, fontweight='bold', pad=20)

        # Legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', bbox_to_anchor=(1.05, 1.15))
        
        self._add_info_texts(fig)  # Call the new method
        plt.subplots_adjust(top=0.8, left=0.1, right=0.9, bottom=0.1)

    def _plot_tuning_and_evaluation(self):
        # Split the data into two parts
        tuning_indices = [i for i, t in enumerate(self.dt) if t <= self.tuning_time]
        evaluation_indices = [i for i, t in enumerate(self.dt) if t > self.tuning_time]

        # Create new time arrays relative to the start of each section
        dt_tuning = [self.dt[i] for i in tuning_indices]
        dt_evaluation = [self.dt[i] - self.dt[evaluation_indices[0]] if evaluation_indices else 0 for i in evaluation_indices]

        if evaluation_indices:
            self.evaluation_time = self.dt[-1] - self.tuning_time
        else:
            self.evaluation_time = 0  # Or None, if you initialized it that way

        temp_tuning = [self.temperature[i] for i in tuning_indices]
        temp_evaluation = [self.temperature[i] for i in evaluation_indices]

        setpoint_tuning = [self.setpoint[i] for i in tuning_indices]
        setpoint_evaluation = [self.setpoint[i] for i in evaluation_indices]

        ctrl_tuning = [self.controller_output[i] for i in tuning_indices]
        ctrl_evaluation = [self.controller_output[i] for i in evaluation_indices]

        # First plot: Tuning data
        self._plot_section(dt_tuning, temp_tuning, setpoint_tuning, ctrl_tuning,
                           title="Tuning Phase Data")

        # Second plot: Evaluation data
        self._plot_section(dt_evaluation, temp_evaluation, setpoint_evaluation, ctrl_evaluation,
                           title="Evaluation Phase Data")

    def _plot_section(self, dt_section, temp_section, setpoint_section, ctrl_section, title=""):
        # Retrieve PID parameters
        self.kp = pid_config.kp
        self.ki = pid_config.ki
        self.kd = pid_config.kd

        fig, ax1 = plt.subplots(figsize=(12, 8))
        ax1.plot(dt_section, temp_section, linestyle='-', color='blue', label="Temperature (°C)")
        ax1.plot(dt_section, setpoint_section, color='blue', linestyle='-', alpha=0.3, linewidth=1.8, label="Setpoint")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Temperature (°C)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.minorticks_on()
        ax1.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.7)
        ax1.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)

        ax2 = ax1.twinx()
        ax2.plot(dt_section, ctrl_section, linestyle='dashed', alpha=0.85, color='orange', linewidth=1.5, label="Controller Output (%)")
        ax2.set_ylabel("Controller Output (%)", color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')

        plt.title(f"{title}\nPID Tuner: {self.chosen_tuner}",
                  fontsize=14, fontweight='bold', pad=20)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', bbox_to_anchor=(1.05, 1.15))

        self._add_info_texts(fig)  # Call the new method
        plt.subplots_adjust(top=0.8, left=0.1, right=0.9, bottom=0.1)
        
        if self.experiment != -1 and self.experiment_set_id != -1:
            base_path = "experiments"
            experiment_set_folder = None

            # Look for an existing folder that contains the experiment_set_id
            for root, dirs, files in os.walk(base_path):
                for dir_name in dirs:
                    if str(self.experiment_set_id) in dir_name:
                        experiment_set_folder = os.path.join(root, dir_name)
                        break
                if experiment_set_folder:
                    break

            # If not found, create a new folder using current date and experiment_set_id
            if experiment_set_folder is None:
                current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M")
                combined_folder = f"{current_date}_{self.experiment_set_id}"
                experiment_set_folder = os.path.join(base_path, combined_folder)
                os.makedirs(experiment_set_folder, exist_ok=True)

            # Save the file in the chosen folder
            file_name = f"experiment_{self.experiment}_{title.split(' ')[0]}({ self.chosen_tuner }).png"
            full_path = os.path.join(experiment_set_folder, file_name)
            plt.savefig(full_path, dpi=200)
        else:
            print("(Set of) experiments had no id, not saving the plots")

    def _add_info_texts(self, fig):
        """Adds multiple info text boxes to the figure."""
        info_text1 = self._generate_info_text()
        plt.figtext(0.01, 0.82, info_text1, fontsize=8,
                    bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.4',
                              edgecolor='gray', linewidth=1))

        info_text2 = self._generate_second_info_text()  # Create this method
        plt.figtext(0.23, 0.82, info_text2, fontsize=8,  # Lower y-coordinate
                    bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.4',
                              edgecolor='gray', linewidth=1))

    def _generate_info_text(self):
        info_text = (
            f"Tuning Time: {round(self.tuning_time, 1)}s\n"
            f"Evaluation Time: {round(self.evaluation_time, 1)}s\n\n"
            f"Simulated Object:\n"
            f"Mass: {self.mass}kg, Heat Capacity: {self.specific_heat}J/(kg·K)\n\n"
            f"Simulation Parameters:\n"
            f"Delta Time: {self.delta_time}s, Delay: {self.simulated_delay}s, Noise: {self.simulated_noise}"
        )
        return info_text
    
    def _generate_second_info_text(self):
        system_dynamics=Tuner.to_string(self.chosen_tuner)
        return (
            f"Found System Dynamics:\n{system_dynamics}\n\n"
            f"Calculated PID variables: \nKp = {self.kp:.4f} \nKi = {self.ki:.4f} \nKd = {self.kd:.4f}"
        )

    def show(self):
        plt.show()