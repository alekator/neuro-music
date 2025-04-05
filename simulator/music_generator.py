from music21 import stream, chord, instrument, tempo, note, scale
import numpy as np
from enum import Enum
import os
class EmotionType(Enum):
    RELAX = 'relax'
    FOCUS = 'focus'
    STRESS = 'stress'
    HAPPY = 'happy'
    SAD = 'sad'

class AmbientGenerator:
    def __init__(self, eeg_data=None, tempo=None, scale_name=None, octave=4):
        self.eeg_data = eeg_data
        self.octave = octave
        self.tempo = self._map_eeg_to_tempo() if eeg_data else (tempo or 80)
        self.scale_name = self._map_eeg_to_scale() if eeg_data else (scale_name or 'major')
        self.instruments = self._select_instruments()
        self.scale = self._create_scale()
        self.dynamic = self._map_amplitude_to_dynamic()

    def _map_eeg_to_tempo(self):
        """Темп музыки зависит от доминирующей частоты EEG"""
        base_freq = self.eeg_data.get('dominant_freq', 10)
        emotion = self.eeg_data.get('emotion', EmotionType.RELAX.value)
        
        ranges = {
            EmotionType.RELAX.value: (40, 70),
            EmotionType.FOCUS.value: (70, 100),
            EmotionType.STRESS.value: (100, 140),
            EmotionType.HAPPY.value: (90, 120),
            EmotionType.SAD.value: (50, 80)
        }
        
        min_bpm, max_bpm = ranges.get(emotion, (60, 120))
        return int(np.interp(base_freq, [2, 40], [min_bpm, max_bpm]))

    def _map_eeg_to_scale(self):
        """Выбор только поддерживаемых гамм"""
        scale_map = {
            EmotionType.RELAX.value: {'sin': 'major', 'saw': 'dorian', 'gamma': 'lydian'},
            EmotionType.FOCUS.value: {'sin': 'minor', 'saw': 'phrygian', 'gamma': 'locrian'},
            EmotionType.STRESS.value: {'sin': 'harmonic minor', 'saw': 'octatonic', 'gamma': 'whole tone'},
            EmotionType.HAPPY.value: {'sin': 'major', 'saw': 'mixolydian', 'gamma': 'ionian'},
            EmotionType.SAD.value: {'sin': 'minor', 'saw': 'aeolian', 'gamma': 'dorian'}
        }
        
        wave_type = self.eeg_data.get('wave_type', 'sin') if self.eeg_data else 'sin'
        emotion = self.eeg_data.get('emotion', EmotionType.RELAX.value) if self.eeg_data else EmotionType.RELAX.value
        
        supported_scales = [
            'major', 'minor', 'harmonic minor', 'melodic minor',
            'dorian', 'phrygian', 'lydian', 'mixolydian', 
            'aeolian', 'locrian', 'whole tone', 'octatonic'
        ]
        
        selected = scale_map.get(emotion, {}).get(wave_type, 'major')
        return selected if selected in supported_scales else 'major'
        

    def _select_instruments(self):
        """Выбор инструментов из доступных в music21"""
        [
        'Piano', 'Harpsichord', 'Clavichord', 'Celesta', 'Glockenspiel',
        'Vibraphone', 'Marimba', 'Xylophone', 'TubularBells', 'Dulcimer',
        'Harp', 'Guitar', 'ElectricGuitar', 'Bass', 'Violin', 'Viola',
        'Cello', 'Contrabass', 'Piccolo', 'Flute', 'Recorder', 'Oboe',
        'Clarinet', 'Bassoon', 'Saxophone', 'Trumpet', 'Trombone', 'Tuba',
        'FrenchHorn', 'ElectricPiano', 'Organ', 'AcousticGuitar'
        ]


        emotion = self.eeg_data.get('emotion', EmotionType.RELAX.value) if self.eeg_data else EmotionType.RELAX.value
        
        # Получаем все доступные инструменты
        available_instruments = [
            inst for inst in dir(instrument) 
            if not inst.startswith('__') and inst[0].isupper()
        ]
        
        # Сопоставление эмоций с существующими инструментами
        instrument_map = {
            EmotionType.RELAX.value: [
                'Piano', 
                'Harp',
                'AcousticGuitar'
            ],
            EmotionType.FOCUS.value: [
                'ElectricPiano',
                'Marimba',
                'Violin'  # Заменили Cello на Violin
            ],
            EmotionType.STRESS.value: [
                'ElectricGuitar',
                'Bass',
                'Trumpet'
            ],
            EmotionType.HAPPY.value: [
                'Glockenspiel',
                'Clarinet',
                'Vibraphone'
            ],
            EmotionType.SAD.value: [
                'Flute',
                'Oboe',
                'Violin'
            ]
        }
        
        # Выбираем только существующие инструменты
        selected = []
        for inst_name in instrument_map.get(emotion, ['Piano', 'Guitar', 'Violin']):
            if inst_name in available_instruments:
                selected.append(getattr(instrument, inst_name)())
            else:
                # Fallback на Piano если инструмент не найден
                selected.append(instrument.Piano())
        
        return selected[:3]  # Всегда возвращаем 3 инструмента

    def _map_amplitude_to_dynamic(self):
        """Громкость на основе амплитуды EEG"""
        amplitude = self.eeg_data.get('amplitude', 1.0) if self.eeg_data else 1.0
        dynamics = ['pp', 'p', 'mp', 'mf', 'f', 'ff']
        index = min(int(amplitude * 2), len(dynamics)-1)
        return dynamics[index]

    def _create_scale(self):
        """Создает гамму с корректными параметрами для music21"""
        scale_name = self.scale_name.lower()
        
        # Базовый объект Pitch для создания шкалы
        from music21 import pitch
        base_pitch = pitch.Pitch(f'C{self.octave}')
        
        try:
            if scale_name == 'major':
                s = scale.MajorScale(base_pitch)
            elif scale_name == 'minor':
                s = scale.MinorScale(base_pitch)
            elif scale_name == 'harmonic minor':
                s = scale.MinorScale(base_pitch)
                s.type = 'harmonic'
            elif scale_name == 'melodic minor':
                s = scale.MinorScale(base_pitch)
                s.type = 'melodic'
            elif scale_name == 'dorian':
                s = scale.DorianScale(base_pitch)
            elif scale_name == 'phrygian':
                s = scale.PhrygianScale(base_pitch)
            elif scale_name == 'lydian':
                s = scale.LydianScale(base_pitch)
            elif scale_name == 'mixolydian':
                s = scale.MixolydianScale(base_pitch)
            elif scale_name == 'locrian':
                s = scale.LocrianScale(base_pitch)
            elif scale_name == 'whole tone':
                s = scale.WholeToneScale(base_pitch)
            elif scale_name == 'octatonic':
                s = scale.OctatonicScale(base_pitch)
            else:
                s = scale.MajorScale(base_pitch)  # fallback
                
            # Получаем ноты шкалы в нужном диапазоне
            pitches = s.getPitches(
                f'C{self.octave}',
                f'C{self.octave+2}'
            )
            return pitches
            
        except Exception as e:
            # Крайний fallback - хроматическая гамма
            chromatic = scale.ChromaticScale(base_pitch)
            return chromatic.getPitches(
                f'C{self.octave}',
                f'C{self.octave+2}'
            )[:7]  # Берем первые 7 нот как мажорную гамму

    def _create_mode_scale(self, mode_index):
        """Создает церковный лад на основе мажорной гаммы"""
        major_pitches = scale.MajorScale().getPitches(self.octave*12, (self.octave+2)*12)
        return major_pitches[mode_index:] + [p.transpose(12) for p in major_pitches[:mode_index]]
    
    def _create_drone(self):
        """Создает фоновый дрон"""
        root = np.random.choice(self.scale)
        drone = chord.Chord([root, root.transpose(12)], type='whole').arpeggiate()
        drone.volume.velocity = self.dynamic
        return drone

    def _add_pad(self, part):
        """Добавляет атмосферные пады"""
        for _ in range(4):
            notes = np.random.choice(self.scale, 3, replace=False)
            pad_chord = chord.Chord(notes, type='half')
            pad_chord.volume.velocity = self.dynamic
            part.append(pad_chord)

    def _add_melody(self, part):
        """Генерирует мелодию"""
        emotion = self.eeg_data.get('emotion', EmotionType.RELAX.value) if self.eeg_data else None
        note_count = 16 if emotion == EmotionType.STRESS.value else 8
        
        melody_notes = []
        current_note = np.random.choice(self.scale)
        
        for _ in range(note_count):
            interval = np.random.choice([-2, -1, 1, 2])
            try:
                current_note = current_note.transpose(interval)
                melody_notes.append(current_note)
            except:
                current_note = np.random.choice(self.scale)
                melody_notes.append(current_note)
            
        for n in melody_notes:
            note_length = 'eighth' if emotion == EmotionType.STRESS.value else 'quarter'
            n = note.Note(n, type=note_length)
            n.volume.velocity = self.dynamic
            part.append(n)

    def generate(self, duration=16):

        try:
            if not hasattr(self, 'scale') or len(self.scale) < 5:
                self.scale = scale.MajorScale().getPitches(self.octave*12, (self.octave+2)*12)

            """Генерация композиции"""
            score = stream.Score()
            
            # Дрон-партия
            drone_part = stream.Part()
            drone_part.insert(self.instruments[0])
            drone_part.append(self._create_drone())
            
            # Партия падов
            pad_part = stream.Part()
            pad_part.insert(self.instruments[1])
            self._add_pad(pad_part)
            
            # Мелодическая партия
            melody_part = stream.Part()
            melody_part.insert(self.instruments[2])
            self._add_melody(melody_part)
            
            # Установка темпа
            score.insert(0, tempo.MetronomeMark(number=self.tempo))
            score.insert(0, drone_part)
            score.insert(0, pad_part)
            score.insert(0, melody_part)
            
            return score
        except Exception as e:
            # Fallback на простую генерацию при ошибке
            backup_score = stream.Score()
            backup_score.append(tempo.MetronomeMark(number=100))
            backup_part = stream.Part([note.Note('C4', type='whole')])
            backup_part.insert(instrument.Piano())
            backup_score.append(backup_part)
            return backup_score

    def save_to_midi(self, score, filename):
        """Сохранение в MIDI-файл с созданием папок"""
        try:
            # Создаем папку media если не существует
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Сохраняем файл
            score.write('midi', fp=filename)
            return True
        except Exception as e:
            print(f"Error saving MIDI: {str(e)}")
            return False