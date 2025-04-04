import numpy as np
from scipy import signal

class EEGGenerator:
    def __init__(self, sampling_rate=250):
        self.sampling_rate = sampling_rate
        self.time = 0

    def _generate_wave(self, freq, amplitude, wave_type="sin"):
        """Генерация волны заданного типа"""
        phase = 2 * np.pi * freq * self.time
        if wave_type == "sin":
            return amplitude * np.sin(phase)
        elif wave_type == "saw":
            return amplitude * signal.sawtooth(phase)
        elif wave_type == "gamma":
            return amplitude * (np.sin(phase) + 0.5 * np.sin(2 * phase))
        return 0

    def get_signal(self, emotion):
        """Генерация сигнала на основе эмоции"""
        self.time += 1 / self.sampling_rate
        noise = 0.05 * np.random.normal()
        
        components = []
        if emotion == "relax":
            components.append(self._generate_wave(10, 1.2))
            components.append(self._generate_wave(2, 0.3, "saw"))  # Тета-ритмы
        elif emotion == "focus":
            components.append(self._generate_wave(20, 1.0, "saw"))
            components.append(self._generate_wave(40, 0.5))
        elif emotion == "stress":
            components.append(self._generate_wave(25, 1.5, "saw"))
            components.append(self._generate_wave(60, 0.8, "gamma"))
        
        return np.sum(components) + noise if components else noise