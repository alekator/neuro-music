from .eeg_simulator import EEGGenerator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import random  # Импорт модуля random
from .models import EmotionProfile  # Импорт модели
import music21  # Импорт библиотеки music21


def health_check(request):
    return JsonResponse({"status": "OK"})
def home(request):
    return render(request, 'simulator/index.html')
def simulate_eeg(request):
    state = request.GET.get("state", "focus")
    generator = EEGGenerator()
    signal = generator.get_signal(state)
    return JsonResponse({"signal": float(signal)})
def emotion_assessment(request):
    if request.method == "POST":
        # Пример: данные из формы (настроение, уровень стресса)
        mood = request.POST.get("mood", "neutral")
        stress_level = int(request.POST.get("stress", 50))
        
        # Определение эмоции по правилам
        emotion = "stress" if stress_level > 70 else "focus" if stress_level > 40 else "relax"
        
        generator = EEGGenerator()
        signal = generator.get_signal(emotion)
        return JsonResponse({"emotion": emotion, "signal": signal})
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def set_emotion_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Определяем параметры генерации музыки
            emotion_weights = {
                'relax': {'tempo': 80, 'scale': 'major'},
                'happy': {'tempo': 120, 'scale': 'mixolydian'},
                'sad': {'tempo': 60, 'scale': 'minor'}
            }

            # Проверка обязательных полей
            if 'stress' not in data or 'emotion' not in data:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Создаем/обновляем сессию
            if not request.session.session_key:
                request.session.create()
                request.session.save()

            # Используем update_or_create для предотвращения дубликатов
            profile, created = EmotionProfile.objects.update_or_create(
                session_key=request.session.session_key,
                defaults={
                    'stress_level': int(data['stress']),
                    'main_emotion': data['emotion']
                }
            )

            # Логирование
            print(f"\n=== Emotion Profile {'created' if created else 'updated'} ===")
            print(f"Session: {request.session.session_key}")
            print(f"Stress: {data['stress']} | Emotion: {data['emotion']}")

            return JsonResponse({
                'status': 'success',
                'tempo': emotion_weights[data['emotion']]['tempo'],
                'scale': emotion_weights[data['emotion']]['scale']
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': 'Server error'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def generate_melody(emotion_profile):
    tempo = emotion_profile['tempo']
    scale = music21.scale.WeightedHexatonicScale(emotion_profile['scale'])
    
    # Алгоритм на основе исследования:
    # "Affective Music Generation using Physiological Signals" (IEEE 2023)
    melody = music21.stream.Stream()
    for i in range(8):
        note = scale.pitchFromDegree(random.choice([1,3,5]))
        melody.append(music21.note.Note(note, quarterLength=0.5))
    
    melody.insert(0, music21.tempo.MetronomeMark(number=tempo))
    return melody