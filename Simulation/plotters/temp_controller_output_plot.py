import matplotlib.pyplot as plt
import pid_config
from pid_controllers.pid import PID
import numpy as np

class Plotter:
    def __init__(self,
                chosen_tuner: PID,
                max_output: float,
                min_output: float,
                simulated_delay: float,
                simulated_noise: float
                ):
        self.temperature = []
        self.controller_output = []
        self.setpoint = []
        self.dt = []
        self.chosen_tuner = chosen_tuner
        self.max_output = max_output
        self.min_output = min_output
       
        self.simulated_delay = simulated_delay
        self.simulated_noise = simulated_noise
        
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
        
    def plot(self):
        self.kp = pid_config.kp
        self.ki = pid_config.ki
        self.kd = pid_config.kd
        
        fig, ax1 = plt.subplots(figsize=(12, 8))
        
        # Primary y-axis for temperature
        ax1.plot(self.dt, self.temperature, linestyle='-', color='blue', label="Temperature (°C)")
        
        # Add setpoint line
        ax1.plot(self.dt, self.setpoint, color='blue', linestyle='-', alpha=0.2, label="Setpoint")
        
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Temperature (°C)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        
        # Enable minor ticks and set finer grid
        ax1.minorticks_on()
        ax1.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.7)
        ax1.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.4)
        
        # Secondary y-axis for controller output
        ax2 = ax1.twinx()
        ax2.plot(self.dt, self.controller_output, linestyle='--', color='orange', label="Controller Output (%)")
        ax2.set_ylabel("Controller Output (%)", color='orange')
        ax2.tick_params(axis='y', labelcolor='orange')
        
        # Add a title showing the chosen tuner
        plt.title(f"PID Performance with Tuning Method: {str.split(self.chosen_tuner.__module__, '.')[1]}", fontsize=14, fontweight='bold', pad=20)
        
        # Add a legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Add text box with configuration information
        info_text = (
            f"PID Parameters:\n"
            f"Kp = {self.kp:.4f}, Ki = {self.ki:.4f}, Kd = {self.kd:.4f}\n\n"
            f"Controller Settings:\n"
            f"Output Range: {self.min_output} to {self.max_output}\n\n"
            f"Simulation Parameters:\n"
            f"Delay: {self.simulated_delay}s, Noise: {self.simulated_noise}"
        )
        
        # Position the text box in the top left corner with more room
        # Create a more spaced-out and noticeable text box
        plt.figtext(0.02, 0.85, info_text, fontsize=10,
                bbox=dict(facecolor='white', alpha=0.9, boxstyle='round,pad=0.7',
                            edgecolor='gray', linewidth=1))
        
        # Adjust layout to make room for the text box and title
        plt.subplots_adjust(top=0.8, left=0.1, right=0.9, bottom=0.1)
    
    def show(self):
        plt.show()