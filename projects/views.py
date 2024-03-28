# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Profile  

@csrf_exempt
def file_upload(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        user_id = request.POST.get('userId')  
        print(request.FILES)
        print(request.POST)
        if file and user_id:
            try:
                user_profile = Profile.objects.get(user_id=user_id)
                user_profile.image.save(file.name, file, save=True)
                return JsonResponse({'success': True, 'url': user_profile.image.url})
            except Profile.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Пользователь не найден'}, status=404)
        else:
            return JsonResponse({'success': False, 'error': 'Файл не предоставлен'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Неверный метод запроса'}, status=405)
