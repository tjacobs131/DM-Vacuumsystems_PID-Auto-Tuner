import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    temperature = []

    def __init__(self):
        pass

    def add_temperature(self, temperature):
        self.temperature.append(temperature)

    def plot(self):
        fig, ax = plt.subplots()
        ax.plot(np.arange(0, len(self.temperature), 1), self.temperature)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Temperature (C)')

    def show(self):
        plt.show()