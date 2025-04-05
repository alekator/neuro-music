from .eeg_simulator import EEGGenerator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import random
from .models import EmotionProfile
import music21
from .music_generator import AmbientGenerator
import os
from django.conf import settings
from datetime import datetime
import logging
import numpy as np
from django.http import FileResponse

logger = logging.getLogger(__name__)

def health_check(request):
    return JsonResponse({"status": "OK"})

def home(request):
    return render(request, 'simulator/index.html')

def simulate_eeg(request):
    try:
        state = request.GET.get("state", "focus")
        generator = EEGGenerator()
        signal = generator.get_signal(state)
        
        if isinstance(signal, dict):
            return JsonResponse({"signal": float(signal.get('amplitude', 0))})
        return JsonResponse({"signal": float(signal)})
    
    except Exception as e:
        logger.error(f"EEG simulation error: {str(e)}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def set_emotion_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Валидация входных данных
            if 'stress' not in data or 'emotion' not in data:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            if not request.session.session_key:
                request.session.create()
                request.session.save()

            # Нормализация данных
            stress = max(1, min(5, int(data['stress'])))  # Ограничение 1-5
            emotion = data['emotion'] if data['emotion'] in ['relax', 'happy', 'sad'] else 'relax'

            # Создание/обновление профиля
            profile, created = EmotionProfile.objects.update_or_create(
                session_key=request.session.session_key,
                defaults={
                    'stress_level': stress,
                    'main_emotion': emotion
                }
            )

            return JsonResponse({
                'status': 'success',
                'session_key': request.session.session_key,
                'stress': profile.stress_level,
                'emotion': profile.main_emotion
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Emotion profile error: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Server error'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def generate_music(request):
    try:
        # Проверка доступности медиа-папки
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
            print(f"Created media dir: {settings.MEDIA_ROOT}")
        
        if not os.access(settings.MEDIA_ROOT, os.W_OK):
            raise Exception(f"Media directory is not writable: {settings.MEDIA_ROOT}")
        
        # 1. Получаем параметры из запроса
        emotion = request.GET.get('emotion', 'relax')
        stress = int(request.GET.get('stress', 3))
        
        # 2. Генерируем EEG данные
        eeg_generator = EEGGenerator()
        eeg_raw = eeg_generator.get_signal(emotion)
        
        # 3. Подготавливаем данные для генератора
        eeg_data = {
            'emotion': emotion,
            'stress_level': stress,
            'dominant_freq': float(eeg_raw['dominant_freq']) if isinstance(eeg_raw, dict) else 10.0,
            'wave_type': eeg_raw['wave_type'] if isinstance(eeg_raw, dict) else 'sin',
            'amplitude': float(eeg_raw['amplitude']) if isinstance(eeg_raw, dict) else 1.0
        }

        # 4. Создаем и настраиваем генератор
        generator = AmbientGenerator(eeg_data=eeg_data)
        composition = generator.generate(duration=32)
        
        # 5. Сохраняем результат
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"neuro_{emotion}_{stress}_{timestamp}.mid"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
        # Создаем папку media если не существует
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        # Сохраняем MIDI файл
        composition.write('midi', fp=filepath)
        
        # Проверяем что файл создан
        if not os.path.exists(filepath):
            raise Exception("MIDI file was not created successfully")
        
        # После сохранения файла, перед возвратом ответа:
        print(f"File exists: {os.path.exists(filepath)}")  # Должно быть True
        print(f"Full path: {filepath}")
        print(f"Media root: {settings.MEDIA_ROOT}")
        # 6. Возвращаем результат
        return JsonResponse({
            'status': 'success',
            'url': f'/media/{filename}', 
            'filepath': filepath,  # Для отладки
            'metadata': {
                'tempo': generator.tempo,
                'scale': generator.scale_name,
                'instruments': [str(i) for i in generator.instruments],
                'emotion': emotion,
                'stress': stress,
                'duration': 32
            }
        })
        
    except Exception as e:
        logger.error(f"Music generation failed: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'error': 'Music generation failed',
            'details': str(e),
            'debug': {
                'emotion': emotion if 'emotion' in locals() else None,
                'stress': stress if 'stress' in locals() else None,
                'eeg_raw': str(eeg_raw) if 'eeg_raw' in locals() else None
            }
        }, status=500)
    

def test_write(request):
    test_file = os.path.join(settings.MEDIA_ROOT, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    return JsonResponse({
        'success': os.path.exists(test_file),
        'path': test_file,
        'cwd': os.getcwd()
    })

def test_media(request):
    filepath = os.path.join(settings.MEDIA_ROOT, 'neuro_happy_1_20250405_184215.mid')
    return FileResponse(open(filepath, 'rb'))