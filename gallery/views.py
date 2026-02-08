
from django.http import HttpResponse

from .models import Asset # Импортируем модель, чтобы спрашивать данные
from django.shortcuts import render, redirect # Добавляем redirect
from .forms import AssetForm # Импортируем нашу новую форму


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
    return render(request, 'gallery/about.html')

def upload(request):
    if request.method == 'POST':
        # Сценарий: Пользователь нажал "Отправить"
        form = AssetForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Если все поля заполнены верно - сохраняем в БД
            form.save()
            # Показываем сообщение об успехе
            context = {
                'form': AssetForm(),  # Создаем новую пустую форму
                'success_message': 'Спасибо, файл загружен!'
            }
            return render(request, 'gallery/upload.html', context)
        else:
            # Форма невалидна, показываем ошибки
            context = {
                'form': form,  # Форма с ошибками
                'success_message': None  # Сообщение об успехе не показываем
            }
            return render(request, 'gallery/upload.html', context)
    else:
        # Сценарий: Пользователь просто зашел на страницу (GET)
        context = {
            'form': AssetForm(),
            'success_message': None
        }
        return render(request, 'gallery/upload.html', context)