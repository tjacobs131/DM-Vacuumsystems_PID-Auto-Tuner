import unittest
from pid_controllers.pid import PID

class ConcretePID(PID):
    """Concrete subclass to test abstract PID methods."""
    def calculate_output(self, process_variable, setpoint, dt):
        return 0.0  # Dummy implementation

class TestPID(unittest.TestCase):
    def test_check_stability_basic(self):
        pid = ConcretePID(max_output=100, min_output=0)
        for _ in range(100):  # Exactly stable_samples_required (100)
            is_stable = pid.check_stability(10.0, dt=0.05, threshold=1.0)
        self.assertTrue(is_stable)
        self.assertEqual(len(pid.stable_buffer), 100)

    def test_check_stability_initial_value_reset(self):
        pid = ConcretePID(max_output=100, min_output=0)
        # Initial call with current_value close to initial_value
        pid.check_stability(102.0, dt=0.05, threshold=1.0, initial_value=100.0)
        self.assertEqual(len(pid.stable_buffer), 0)  # Buffer cleared
        
        # Add values and check buffer growth
        for _ in range(50):
            pid.check_stability(10.0, dt=0.05, threshold=1.0)
        self.assertEqual(len(pid.stable_buffer), 50)
        
        # Add value near initial_value again
        pid.check_stability(104.0, dt=0.05, threshold=1.0, initial_value=100.0)
        self.assertEqual(len(pid.stable_buffer), 0)  # Buffer cleared again

    def test_check_stability_buffer_management(self):
        pid = ConcretePID(max_output=100, min_output=0)
        for _ in range(150):  # More than required samples
            pid.check_stability(10.0, dt=0.05, threshold=1.0)
        self.assertEqual(len(pid.stable_buffer), 100)  # Capped at 100

    def test_check_stability_threshold_exceeded(self):
        pid = ConcretePID(max_output=100, min_output=0)
        # Alternate values to create max-min=2.0 (threshold=1.0)
        for i in range(100):
            val = 10.0 if i % 2 == 0 else 12.0
            is_stable = pid.check_stability(val, dt=0.05, threshold=1.0)
        self.assertFalse(is_stable)  # Variation exceeds threshold

    def test_get_stabilized_output(self):
        pid = ConcretePID(max_output=100, min_output=0)
        # Fill buffer: 80 * 10.0, then 20 * 20.0
        for _ in range(80):
            pid.check_stability(10.0, dt=0.05, threshold=5.0)
        for _ in range(20):
            pid.check_stability(20.0, dt=0.05, threshold=5.0)
        self.assertAlmostEqual(pid.get_stabilized_output(), 20.0)  # Last 20% average

    def test_initial_value_change_resets_buffer(self):
        pid = ConcretePID(max_output=100, min_output=0)
        pid.check_stability(90.0, dt=0.05, threshold=10.0, initial_value=100.0)
        self.assertEqual(len(pid.stable_buffer), 1)
        
        # Add values and change initial_value
        for _ in range(50):
            pid.check_stability(90.0, dt=0.05, threshold=10.0)
        pid.check_stability(90.0, dt=0.05, threshold=10.0, initial_value=200.0)
        self.assertEqual(len(pid.stable_buffer), 1)

if __name__ == '__main__':
    unittest.main()