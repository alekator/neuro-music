import numpy as np
from scipy import signal
from typing import Dict, Any

class EEGGenerator:
    def __init__(self, sampling_rate: int = 250):
        self.sampling_rate = sampling_rate
        self.time = 0
        self.base_frequencies = {
            'relax': {'main': 10, 'secondary': 2},
            'focus': {'main': 20, 'secondary': 40},
            'stress': {'main': 25, 'secondary': 60},
            'happy': {'main': 15, 'secondary': 30},
            'sad': {'main': 8, 'secondary': 4}
        }

    def _generate_wave(self, freq: float, amplitude: float, wave_type: str = "sin") -> float:
        """Генерация волны заданного типа"""
        phase = 2 * np.pi * freq * self.time
        if wave_type == "sin":
            return amplitude * np.sin(phase)
        elif wave_type == "saw":
            return amplitude * signal.sawtooth(phase)
        elif wave_type == "gamma":
            return amplitude * (np.sin(phase) + 0.5 * np.sin(2 * phase))
        return 0.0

    def get_signal(self, emotion: str) -> Dict[str, Any]:
        """Генерация сигнала на основе эмоции"""
        self.time += 1 / self.sampling_rate
        noise = 0.05 * np.random.normal()
        
        # Получаем базовые частоты для эмоции
        freqs = self.base_frequencies.get(emotion, self.base_frequencies['relax'])
        
        # Генерируем компоненты сигнала
        components = [
            self._generate_wave(freqs['main'], 1.2, "sin"),
            self._generate_wave(freqs['secondary'], 0.5, "saw")
        ]
        
        # Вычисляем доминирующую частоту
        dominant_freq = float(freqs['main'])
        
        # Вычисляем амплитуду
        amplitude = float(np.sum(components) + noise)
        
        # Определяем тип волны
        wave_type = "gamma" if emotion == "stress" else "saw" if emotion == "focus" else "sin"
        
        return {
            'dominant_freq': dominant_freq,
            'wave_type': wave_type,
            'amplitude': amplitude,
            'emotion': emotion,
            'raw_components': [float(x) for x in components]
        }