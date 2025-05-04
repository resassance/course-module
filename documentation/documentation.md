# Документация модуля курсов (courses)

## `admin.py`
**Назначение**: Настройка административного интерфейса Django для управления пользователями и токенами.

```python
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Custom fields', {'fields': ('role',)}),
    )
```

**Ключевые особенности**:
- Кастомизированный интерфейс для модели User
- Добавлено отображение роли (role) пользователя
- Стандартная регистрация модели Token

## `models.py`
**Назначение**: Определение структуры базы данных.

### Основные модели:
1. `User` - расширенная модель пользователя с ролями
2. `Course` - основная единица системы обучения
3. `CourseMaterial` - учебные материалы разных типов
4. `CourseRequest` - система заявок на курсы

**Пример модели**:
```python
class Course(models.Model):
    title = models.CharField(max_length=255)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
```

## `serializers.py`
**Назначение**: Преобразование данных между Django-моделями и JSON.

**Основные сериализаторы**:
1. `CourseSerializer` - полное представление курса
2. `CourseEnrollmentSerializer` - с дополнительным полем `student_name`
3. `CourseRequestSerializer` - автоматическое поле `auditor_name`

**Пример**:
```python
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('creation_date',)
```

## `views.py`
**Назначение**: Обработка HTTP-запросов и бизнес-логика.

### Ключевые endpoint'ы:
GET - `/courses/` - список всех курсов
POST - `/courses/<id>/enrollments/` - запись на курс
PATCH - `/requests/<id>/` - обработка заявок

**Пример view-функции**:
```python
@api_view(['GET'])
def course_list_view(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response({'data': serializer.data})
```

## `urls.py`
**Назначение**: Маршрутизация API.

```python
urlpatterns = [
    path('courses/', views.course_list_view),
    path('courses/<int:pk>/enrollments/', views.course_enrollments),
    path('requests/<int:pk>/', views.handle_request),
]
```

## Системные требования
- Python 3.9+
- Django 4.2+
- DRF 3.14+

## Установка
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```