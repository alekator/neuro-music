# analytics.py
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class NeuroAnalytics:
    @staticmethod
    def generate_eeg_wave(emotion='relax', duration=5, sample_rate=250):
        """Генерация искусственного EEG сигнала"""
        t = np.linspace(0, duration, int(duration * sample_rate), False)
        
        # Частоты для разных эмоций (в Гц)
        freq_ranges = {
            'relax': (8, 12),    # Альфа-ритм
            'focus': (12, 30),    # Бета-ритм
            'stress': (30, 50),   # Гамма-ритм
            'happy': (12, 25),
            'sad': (4, 8)         # Тета-ритм
        }
        
        base_freq = np.mean(freq_ranges.get(emotion, (10, 15)))
        signal = np.sin(2 * np.pi * base_freq * t)
        noise = 0.2 * np.random.normal(size=len(t))
        return t, signal + noise

    @staticmethod
    def generate_music_pattern(eeg_signal):
        """Преобразование EEG в музыкальные параметры"""
        amplitude = np.max(eeg_signal) - np.min(eeg_signal)
        notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        
        # Ноты на основе амплитуды
        note_index = int(np.interp(amplitude, [0.2, 2], [0, len(notes)-1]))
        note = notes[min(note_index, len(notes)-1)]
        
        # Длительность ноты на основе частоты
        zero_crossings = len(np.where(np.diff(np.sign(eeg_signal)))[0])
        duration = 'quarter' if zero_crossings > 20 else 'half'
        
        return {
            'note': note,
            'duration': duration,
            'amplitude': amplitude,
            'zero_crossings': zero_crossings
        }

    @staticmethod
    def create_plots(emotion='relax'):
        """Создание интерактивных графиков"""
        t, eeg_signal = NeuroAnalytics.generate_eeg_wave(emotion)
        music_data = NeuroAnalytics.generate_music_pattern(eeg_signal)
        
        # Создаем фигуру с двумя субплoтами
        fig = make_subplots(rows=2, cols=1, subplot_titles=(
            f'EEG Signal ({emotion.capitalize()} State)',
            'Music Generation Pattern'
        ))
        
        # EEG график
        fig.add_trace(
            go.Scatter(x=t, y=eeg_signal, name='EEG', line=dict(color='blue')),
            row=1, col=1
        )
        
        # Музыкальный график (упрощенный)
        fig.add_trace(
            go.Scatter(
                x=t, 
                y=np.sin(2 * np.pi * 5 * t) * music_data['amplitude'],
                name='Music Wave',
                line=dict(color='green')
            ),
            row=2, col=1
        )
        
        # Настройки layout
        fig.update_layout(
            height=600,
            showlegend=True,
            template='plotly_white'
        )
        
        explanation = f"""
        <h4>How EEG Translates to Music:</h4>
        <p><b>Detected Emotion:</b> {emotion.capitalize()}</p>
        <p><b>Dominant Frequency:</b> {np.mean(eeg_signal):.2f} Hz</p>
        <p><b>Generated Note:</b> {music_data['note']} ({music_data['duration']} note)</p>
        <p><b>Amplitude:</b> {music_data['amplitude']:.2f} → Volume</p>
        <p><b>Zero Crossings:</b> {music_data['zero_crossings']} → Rhythm</p>
        """
        
        return fig.to_html(full_html=False), explanation