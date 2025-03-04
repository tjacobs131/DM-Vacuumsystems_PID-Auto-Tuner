import subprocess
import uuid
import sys  # Import sys for getting python executable path

if __name__ == "__main__":
    experiment_set_id = uuid.uuid4()  # Generate a unique ID for this set of experiments

    parameter_sets = [
        {
            'tuner': 'astromhagglund',
            'dt': 0.02,
            'sim_mass': 40.0,
            'sim_specific_heat': 400.0,
            'setpoint': 100.0,
            'delay': 1.0,
            'noise': 0.01,
        },
        {
            'tuner': 'skogestad',
            'dt': 0.02,
            'sim_mass': 40.0,
            'sim_specific_heat': 400.0,
            'setpoint': 100.0,
            'delay': 1.0,
            'noise': 0.01,
        },
    ]

    python_executable = sys.executable  # Get the path to the current Python interpreter

    for experiment_count, params in enumerate(parameter_sets):
        print(f"Running Experiment {experiment_count + 1} with parameters: {params}")

        command = [python_executable, "main.py"] # Start with python executable and main script

        # Add parameters as command line arguments
        if params['tuner'] is not None:
            command.extend(['--tuner', params['tuner']])
        command.extend(['--dt', str(params['dt'])])
        command.extend(['--sim_mass', str(params['sim_mass'])])
        command.extend(['--sim_specific_heat', str(params['sim_specific_heat'])])
        command.extend(['--setpoint', str(params['setpoint'])])
        command.extend(['--delay', str(params['delay'])])
        command.extend(['--noise', str(params['noise'])])
        command.extend(['--experiment', str(experiment_count + 1)]) # Experiment number
        command.extend(['--experiment_set_id', str(experiment_set_id)]) # Experiment set ID

        print(f"Executing command: {' '.join(command)}") # Print the command for debugging

        try:
            process = subprocess.Popen(command) # Execute main.py as subprocess
            process.wait() # Wait for the subprocess to finish
            if process.returncode != 0:
                print(f"Experiment {experiment_count + 1} failed with return code: {process.returncode}")
            else:
                print(f"Experiment {experiment_count + 1} finished successfully.\n")

        except FileNotFoundError:
            print(f"Error: Python executable not found at: {python_executable}")
            print("Please ensure Python is installed and in your system's PATH.")
            print(f"Experiment {experiment_count + 1} aborted.\n")
        except Exception as e:
            print(f"An error occurred during Experiment {experiment_count + 1}: {e}")
            import traceback
            traceback.print_exc()
            print(f"Experiment {experiment_count + 1} aborted.\n")

    print("All experiments completed.")