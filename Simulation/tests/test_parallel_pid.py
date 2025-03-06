import unittest
from pid_controllers.parallel_pid import Parallel_PID

class TestParallelPID(unittest.TestCase):
    def test_proportional_control(self):
        pid = Parallel_PID(max_output=100, min_output=-100, kp=2, ki=0, kd=0)
        output = pid.calculate_output(process_variable=5, setpoint=10, dt=1)
        self.assertEqual(output, 10)  # 2 * (10-5) = 10
        self.assertEqual(pid.integral, 5)  # Integral still accumulates

    def test_integral_anti_windup_max(self):
        pid = Parallel_PID(max_output=5, min_output=-5, kp=0, ki=1, kd=0)
        # First call: integral=5, output=5 (max)
        output1 = pid.calculate_output(5, 10, dt=1)
        self.assertEqual(output1, 5)
        self.assertEqual(pid.integral, 5)
        
        # Second call: integral would be 10, but output clamped to 5
        output2 = pid.calculate_output(5, 10, dt=1)
        self.assertEqual(output2, 5)
        self.assertEqual(pid.integral, 5)  # Integral rolled back

    def test_derivative_term(self):
        pid = Parallel_PID(max_output=100, min_output=-100, kp=0, ki=0, kd=2)
        # Initial call to set prev_error
        pid.calculate_output(process_variable=0, setpoint=0, dt=1)
        # Next call: error=5-0=5, derivative=(5-0)/1=5
        output = pid.calculate_output(process_variable=0, setpoint=5, dt=1)
        self.assertEqual(output, 10)  # 2 * 5 = 10

    def test_dt_zero_handling(self):
        pid = Parallel_PID(max_output=100, min_output=-100, kp=0, ki=0, kd=1)
        output = pid.calculate_output(process_variable=5, setpoint=10, dt=0)
        self.assertEqual(output, 0)  # Derivative term forced to 0

    def test_min_output_clamping(self):
        pid = Parallel_PID(max_output=0, min_output=-5, kp=0, ki=1, kd=0)
        # First call: integral=-5, output=-5 (min)
        output1 = pid.calculate_output(5, 0, dt=1)
        self.assertEqual(output1, -5)
        self.assertEqual(pid.integral, -5)
        
        # Second call: integral would be -10, output clamped to -5
        output2 = pid.calculate_output(5, 0, dt=1)
        self.assertEqual(output2, -5)
        self.assertEqual(pid.integral, -5)  # Integral rolled back

    def test_integral_accumulation_within_limits(self):
        pid = Parallel_PID(max_output=100, min_output=-100, kp=0, ki=1, kd=0)
        output1 = pid.calculate_output(8, 10, dt=1)
        self.assertEqual(output1, 2)  # Integral=2
        output2 = pid.calculate_output(8, 10, dt=1)
        self.assertEqual(output2, 4)  # Integral=4

if __name__ == '__main__':
    unittest.main()