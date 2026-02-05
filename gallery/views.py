
from django.http import HttpResponse

from django.shortcuts import render
from .models import Asset # Импортируем модель, чтобы спрашивать данные

# HttpResponse нам больше не нужен, render делает это за нас
# def home(request):
#     # Имитация данных из базы (список словарей)
#     fake_database = [
#         {'id': 1, 'name': 'Sci-Fi Helmet', 'file_size': '15 MB'},
#         {'id': 2, 'name': 'Old Chair', 'file_size': '2 MB'},
#         {'id': 3, 'name': 'Cyber Truck', 'file_size': '10 MB'},
#         {'id': 4, 'name': 'Table', 'file_size': '7 MB'},
#     ]
#     context_data = {
#         'page_title': 'Главная Галерея',
#         'assets': fake_database, # Передаем весь список
#     }
#     return render(request, 'gallery/index.html', context_data)
def home(request):
    # all() возвращает хаос.
    # order_by('-created_at') сортирует по полю created_at.
    # Минус (-) означает "по убыванию" (DESC).
    assets = Asset.objects.all().order_by('-created_at')
    context_data = {
    'page_title': 'Главная Галерея',
    'assets': assets,
    }
    return render(request, 'gallery/index.html', context_data)

def about(request):
# Мы пока не используем HTML-шаблоны, просто вернем строку.
    #return HttpResponse("<h1>Курс Web Структуры.</p>")
    return render(request, 'gallery/about.html')

def upload(request):
# Мы пока не используем HTML-шаблоны, просто вернем строку.
    #return HttpResponse("<h1>Курс Web Структуры.</p>")
    return render(request, 'gallery/upload.html')