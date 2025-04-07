from .eeg_simulator import EEGGenerator
from django.http import JsonResponse, HttpResponse, FileResponse
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
from midi2audio import FluidSynth

logger = logging.getLogger(__name__)

def health_check(request):
    return JsonResponse({"status": "OK"})

def home(request):
    return render(request, 'simulator/index.html')

def partial_view(request, page_name):
    """Обработчик для загрузки частичных представлений"""
    templates = {
        'info': 'simulator/partials/info.html',
        'generator': 'simulator/partials/generator.html',
        'analytics': 'simulator/partials/analytics.html',
        'settings': 'simulator/partials/settings.html',
    }
    return render(request, templates.get(page_name, 'simulator/partials/info.html'))

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
            
            if 'stress' not in data or 'emotion' not in data:
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            if not request.session.session_key:
                request.session.create()
                request.session.save()

            stress = max(1, min(5, int(data['stress'])))
            emotion = data['emotion'] if data['emotion'] in ['relax', 'happy', 'sad'] else 'relax'

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
        logger.info("Starting music generation")
        
        # Проверка soundfont
        soundfont_path = os.path.join(settings.MEDIA_ROOT, 'soundfonts/GeneralUser.sf2')
        logger.info(f"Soundfont path: {soundfont_path}")
        
        if not os.path.exists(soundfont_path):
            logger.error("Soundfont file not found")
            raise Exception(f"Soundfont file not found at {soundfont_path}")

        # Проверка медиа-папки
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        if not os.access(settings.MEDIA_ROOT, os.W_OK):
            raise Exception(f"Media directory is not writable: {settings.MEDIA_ROOT}")
        
        # Получение параметров
        emotion = request.GET.get('emotion', 'relax')
        stress = int(request.GET.get('stress', 3))
        
        # Генерация EEG
        eeg_generator = EEGGenerator()
        eeg_raw = eeg_generator.get_signal(emotion)
        
        # Создание генератора музыки
        generator = AmbientGenerator(eeg_data={
            'emotion': emotion,
            'stress_level': stress,
            'dominant_freq': float(eeg_raw['dominant_freq']) if isinstance(eeg_raw, dict) else 10.0,
            'wave_type': eeg_raw['wave_type'] if isinstance(eeg_raw, dict) else 'sin',
            'amplitude': float(eeg_raw['amplitude']) if isinstance(eeg_raw, dict) else 1.0
        })
        
        # Генерация композиции
        composition = generator.generate(duration=32)
        
        # Сохранение файлов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"neuro_{emotion}_{stress}_{timestamp}"
        
        midi_path = os.path.join(settings.MEDIA_ROOT, f"{filename}.mid")
        composition.write('midi', fp=midi_path)
        
        # Конвертация в MP3
        mp3_path = os.path.join(settings.MEDIA_ROOT, f"{filename}.mp3")
        fs = FluidSynth(sound_font=soundfont_path)
        fs.midi_to_audio(midi_path, mp3_path)
        
        # Проверка файлов
        if not all(os.path.exists(p) for p in [midi_path, mp3_path]):
            raise Exception("Failed to create audio files")
        
        return JsonResponse({
            'status': 'success',
            'midi_url': f'/media/{filename}.mid',
            'mp3_url': f'/media/{filename}.mp3',
            'metadata': {
                'tempo': generator.tempo,
                'duration': 32,
                'emotion': emotion,
                'stress': stress,
                'file_size': os.path.getsize(mp3_path)
            }
        })
        
    except Exception as e:
        logger.error(f"Music generation failed: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'debug': {
                'media_root': settings.MEDIA_ROOT,
                'cwd': os.getcwd(),
                'soundfont_exists': os.path.exists(soundfont_path) if 'soundfont_path' in locals() else False
            }
        }, status=500)

def test_write(request):
    """Тест записи в медиа-папку"""
    test_file = os.path.join(settings.MEDIA_ROOT, 'test.txt')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        return JsonResponse({
            'success': os.path.exists(test_file),
            'path': test_file,
            'media_root': settings.MEDIA_ROOT
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def test_media(request):
    """Тест доступа к медиафайлам"""
    test_file = os.path.join(settings.MEDIA_ROOT, 'test.txt')
    try:
        return FileResponse(open(test_file, 'rb'))
    except FileNotFoundError:
        return HttpResponse("Test file not found", status=404)
def partial_view(request, page):
    print(f"Requested page: {page}")  # Добавьте эту строку
    templates = {
        'info': 'simulator/partials/info.html',
        'generator': 'simulator/partials/generator.html',
        'analytics': 'simulator/partials/analytics.html',
        'settings': 'simulator/partials/settings.html',
    }
    return render(request, templates.get(page, 'simulator/partials/info.html'))