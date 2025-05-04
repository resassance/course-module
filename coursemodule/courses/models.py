from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser


"""эти три таблицы (user, group, year) были не по моей части, поэтому я добавил их как заглушку, без них не работало"""
class User(AbstractUser):
    ROLES = [
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
        ('auditor', 'Вольнослушатель'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default='student')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Group(models.Model):
    """Учебная группа"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Year(models.Model):
    """Учебный год"""
    name = models.CharField(max_length=9, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Course(models.Model):
    """Основная модель курса"""
    course_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    year_id = models.ForeignKey(
        'Year', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Связанный учебный год'
    )
    teacher_id = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='taught_courses',
        verbose_name='Преподаватель'
    )
    group_id = models.ForeignKey(
        'Group', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='Группа'
    )
    is_active = models.BooleanField(
    default=True,
    verbose_name='Активен'
    )


    def __str__(self):
        return f"{self.title} (ID: {self.course_id})"

class CourseRequest(models.Model):
    """Заявки вольнослушателей на курс"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name='Курс'
    )
    auditor_id = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='course_requests',
        verbose_name='Вольнослушатель'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На рассмотрении'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено')
        ],
        default='pending'
    )

    class Meta:
        unique_together = ('course', 'auditor_id')
        verbose_name = 'Заявка на курс'
        verbose_name_plural = 'Заявки на курсы'

class CourseEnrollment(models.Model):
    """Записи студентов на курс"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Курс'
    )
    student_id = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Студент'
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student_id')
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'

class CourseMaterial(models.Model):
    """Материалы курса"""
    MATERIAL_TYPES = [
        ('video', 'Видео'),
        ('text', 'Текст'),
        ('pdf', 'PDF-документ'),
        ('quiz', 'Тест')
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='Курс'
    )
    material_type = models.CharField(
        max_length=20,
        choices=MATERIAL_TYPES,
        verbose_name='Тип материала'
    )
    content = models.TextField(verbose_name='Содержание')
    creation_date = models.DateTimeField(auto_now_add=True)
    material_file = models.FileField(
        upload_to='course_materials/',
        blank=True,
        null=True,
        verbose_name='Файл материала'
    )

    class Meta:
        verbose_name = 'Материал курса'
        verbose_name_plural = 'Материалы курса'

class CourseModule(models.Model):
    """Модули курса"""
    module_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Курс'
    )
    title = models.CharField(max_length=255, verbose_name='Название модуля')
    description = models.TextField(blank=True, verbose_name='Описание')
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Порядковый номер'
    )

    class Meta:
        unique_together = ('course', 'order')
        ordering = ['order']
        verbose_name = 'Модуль курса'
        verbose_name_plural = 'Модули курса'

class CourseArchive(models.Model):
    """Архивация курсов"""
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='archive',
        verbose_name='Курс'
    )
    year = models.ForeignKey(
        'Year',
        on_delete=models.CASCADE,
        verbose_name='Учебный год'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('archived', 'В архиве'),
            ('deleted', 'Удален')
        ],
        default='archived'
    )

    class Meta:
        verbose_name = 'Архив курса'
        verbose_name_plural = 'Архивы курсов'

class CourseSettings(models.Model):
    """Настройки видимости курса"""
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='settings',
        verbose_name='Курс'
    )
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Публичный'),
            ('private', 'Приватный'),
            ('hidden', 'Скрытый')
        ],
        default='private'
    )

    class Meta:
        verbose_name = 'Настройка курса'
        verbose_name_plural = 'Настройки курсов'