from rest_framework import serializers
from .models import Course, CourseMaterial, CourseRequest, CourseEnrollment

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('creation_date',)

class CourseLastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'title', 'creation_date', 'is_active']

class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = '__all__'

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student_id.get_full_name', read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = ['id', 'student_id', 'student_name', 'enrollment_date']
        read_only_fields = ('enrollment_date',)

class CourseRequestSerializer(serializers.ModelSerializer):
    auditor_name = serializers.CharField(source='auditor_id.get_full_name', read_only=True)
    
    class Meta:
        model = CourseRequest
        fields = ['id', 'course', 'auditor_id', 'auditor_name', 'status']
        read_only_fields = ('course', 'auditor_id')