import numpy as np
from collections import deque

class HeatSim:
    # Physical constants
    MASS = 0.0                # kg (mass of the heater)
    SPECIFIC_HEAT = 0.0      # J/(kg·K)
    HEAT_TRANSFER_COEFF = 180.0 # W/K (heat loss to environment)
    ROOM_TEMP = 20.0           # °C

    def __init__(self, dt, mass = 40, specific_heat = 420, delay=0.5, noise=0.04):
        self.dt = dt
        self.current_temp = self.ROOM_TEMP
        self.sensor_temp = self.ROOM_TEMP
        self.MASS = mass
        self.SPECIFIC_HEAT = specific_heat
        self.thermal_mass = self.MASS * self.SPECIFIC_HEAT  # J/K
        self.noise = noise

        self.delay_steps = max(1,int(delay / dt))
        self.delay_buffer = deque([self.current_temp] * self.delay_steps, maxlen=self.delay_steps)
        self.delay_buffer.append(self.current_temp)

    def update(self, heater_power):
        # Heat loss to environment (W)
        heat_loss = self.HEAT_TRANSFER_COEFF * (self.current_temp - self.ROOM_TEMP)
        
        # Net power (W): heater input - heat loss
        net_power = heater_power * 200 - heat_loss
        
        # Temperature change (dT = (Power * dt) / (mass * specific_heat))
        delta_temp = (net_power * self.dt) / self.thermal_mass
        
        # Update temperature
        self.current_temp += delta_temp

        # Simulate delay 
        self.delay_buffer.append(self.current_temp)

    def read_temperature(self):
        return self.delay_buffer[0] + np.random.normal(0, self.noise)