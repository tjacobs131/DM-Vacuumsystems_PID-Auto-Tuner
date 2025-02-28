import numpy as np
from collections import deque

class HeatSim:
    # Physical constants (adjust values to match your system)
    MASS = 10.0                # kg (mass of the heater)
    SPECIFIC_HEAT = 420.0      # J/(kg·K) (e.g., water: ~4200, metal: ~500)
    HEAT_TRANSFER_COEFF = 300.0 # W/K (heat loss to environment)
    ROOM_TEMP = 20.0           # °C

    SPEEDUP = 400

    def __init__(self, dt, delay=0.5, noise=0.0):
        self.dt = dt
        self.current_temp = self.ROOM_TEMP
        self.thermal_mass = self.MASS * self.SPECIFIC_HEAT  # J/K
        self.noise = noise

        self.delay_steps = int(delay / dt)
        self.delay_buffer = deque([self.current_temp] * self.delay_steps, maxlen=self.delay_steps)

    def update(self, heater_power):
        # Heat loss to environment (W)
        heat_loss = self.HEAT_TRANSFER_COEFF * (self.current_temp - self.ROOM_TEMP)
        
        # Net power (W): heater input - heat loss
        net_power = heater_power * 400 - heat_loss
        
        # Temperature change (dT = (Power * dt) / (mass * specific_heat))
        delta_temp = (net_power * self.dt) / self.thermal_mass
        
        # Update temperature
        self.current_temp += delta_temp

        # Simulate delay 
        self.delay_buffer.append(self.current_temp)

        # Add noise
        self.current_temp += np.random.normal(0, self.noise)

    def read_temperature(self):
        return self.delay_buffer[0]