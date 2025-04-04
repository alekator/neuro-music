from django.test import TestCase
from .eeg_simulator import EEGGenerator

class EEGModelTest(TestCase):
    def test_stress_signal(self):
        generator = EEGGenerator()
        signal = [generator.get_signal("stress") for _ in range(1000)]
        self.assertTrue(max(signal) > 2.0)  # Проверка амплитуды