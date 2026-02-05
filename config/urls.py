from django.contrib import admin
from django.urls import path
# Импортируем нашу функцию из приложения gallery
from gallery.views import home
from gallery.views import about
urlpatterns = [
path('admin/', admin.site.urls),
# Пустая строка '' означает главную страницу сайта (http://localhost:8000/)
path('about/', about, name="about"),
path('', home, name='home'),
]

