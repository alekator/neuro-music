from django.http import JsonResponse
from django.http import HttpResponse

def health_check(request):
    return JsonResponse({"status": "OK"})
def home(request):
    return HttpResponse("Добро пожаловать в Neuro-Music!")