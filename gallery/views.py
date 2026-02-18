
from datetime import timedelta
from django.http import HttpResponse
import base64
from django.core.files.base import ContentFile # Обертка для сохранения файлов
from .models import Asset # Импортируем модель, чтобы спрашивать данные
from django.shortcuts import render, redirect # Добавляем redirect
from .forms import AssetForm # Импортируем нашу новую форму
from django.db.models import Q # Импортируем Q-object для сложного поиска
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages

def home(request):
     # 1. Получаем параметры из URL (GET-запроса)
    # Если параметра нет, вернет None (или пустую строку, если мы так настроили)
    search_query = request.GET.get('q', '')
    ordering = request.GET.get('ordering', 'new') # По умолчанию 'new'
    # 2. Базовый запрос: Берем ВСЕ
    assets = Asset.objects.all()
    # 3. Применяем поиск (если пользователь что-то ввел)
    if search_query:
        # icontains = Case Insensitive Contains (содержит, без учета регистра)
        # Если бы у нас было поле 'description', мы бы использовали Q:
        # assets = assets.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        assets = assets.filter(title__icontains=search_query)
    # 4. Применяем сортировку
    if ordering == 'old':
        assets = assets.order_by('created_at') # От старых к новым
    elif ordering == 'name':
        assets = assets.order_by('title')      # По алфавиту
    elif ordering == 'day':
        assets = assets.filter(created_at__gte=timezone.now() - timedelta(days=1))
    else:
        # По умолчанию (new) - свежие сверху
        assets = assets.order_by('-created_at')

    # --- ПАГИНАЦИЯ (Новый код) --
    # Режем список по 8 штук на страницу (для теста, чтобы быстрее увидеть кнопки)
    paginator = Paginator(assets, 8) 
    # Получаем номер страницы из URL (например, ?page=2)
    page_number = request.GET.get('page')
    # Получаем конкретный кусочек данных (объект Page)
    page_obj = paginator.get_page(page_number)
    context_data = {
        'page_title': 'Главная Галерея',
        # 'assets': assets,  <-- ЭТУ СТРОКУ УДАЛИТЬ!
        'page_obj': page_obj, # <-- ВМЕСТО НЕЁ ЭТУ
    }
    return render(request, 'gallery/index.html', context_data)


def about(request):
    return render(request, 'gallery/about.html')

def upload(request):
    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Создаем объект, но пока НЕ сохраняем в базу (commit=False)
            new_asset = form.save(commit=False)
            
            # 2. Обрабатываем картинку из скрытого поля
            image_data = request.POST.get('image_data') # Получаем строку Base64
            
            if image_data:
                # Формат строки: "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
                # Нам нужно отрезать заголовок "data:image/jpeg;base64,"
                format, imgstr = image_data.split(';base64,') 
                ext = format.split('/')[-1] # получаем "jpeg"
                
                # Декодируем текст в байты
                data = base64.b64decode(imgstr)
                
                # Создаем имя файла (берем имя модели + .jpg)
                file_name = f"{new_asset.title}_thumb.{ext}"
                
                # Сохраняем байты в поле image
                # ContentFile превращает байты в объект, который понимает Django FileField
                new_asset.image.save(file_name, ContentFile(data), save=False)
            # 3. Финальное сохранение в БД
            new_asset.save()
            
            # ДОБАВЛЯЕМ СООБЩЕНИЕ
            messages.success(request, f'Модель "{new_asset.title}" успешно загружена!')

            return redirect('home')
    else:
        form = AssetForm()
    return render(request, 'gallery/upload.html', {'form': form})