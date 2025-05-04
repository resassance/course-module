from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Course, CourseMaterial, CourseEnrollment, CourseRequest
from .serializers import (
    CourseSerializer, 
    CourseLastSerializer,
    CourseMaterialSerializer,
    CourseEnrollmentSerializer,
    CourseRequestSerializer
)

@api_view(['GET'])
def course_list_view(request):
    try:
        if request.method == 'GET':
            courses = Course.objects.all()
            if not courses.exists():
                return Response(
                    {'status': 'error', 'message': 'Courses not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = CourseSerializer(courses, many=True)
            return Response(
                {'status': 'success', 'data': serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(
            {'status': 'error', 'message': 'HTTP method not allowed'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    except Exception as e:
        return Response(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def last_courses(request):
    try:
        if request.method == 'GET':
            latest = Course.objects.order_by('-creation_date')[:4]
            
            if not latest.exists():
                return Response(
                    {'status': 'error', 'message': 'No recent courses'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = CourseLastSerializer(latest, many=True, context={'request': request})
            return Response(
                {'status': 'success', 'data': serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(
            {'status': 'error', 'message': 'HTTP method not supported'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    except Exception as e:
        return Response(
            {'status': 'error', 'message': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response(
            {'status': 'error', 'message': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_materials(request, pk):
    materials = CourseMaterial.objects.filter(course=pk)
    serializer = CourseMaterialSerializer(materials, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_enrollments(request, pk):
    if request.method == 'GET':
        enrollments = CourseEnrollment.objects.filter(course=pk)
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        student_id = request.data.get('student_id', request.user.id)
        data = {'course': pk, 'student_id': student_id}
        
        serializer = CourseEnrollmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_requests(request, pk):
    if request.method == 'GET':
        requests = CourseRequest.objects.filter(course=pk)
        serializer = CourseRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'auditor':
            data = {'course': pk, 'auditor_id': request.user.id}
            serializer = CourseRequestSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def handle_request(request, pk):
    try:
        course_request = CourseRequest.objects.get(pk=pk)
        
        new_status = request.data.get('status')
        if new_status not in ['approved', 'rejected']:
            return Response(
                {'status': 'error', 'message': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course_request.status = new_status
        course_request.save()
        
        if new_status == 'approved':
            CourseEnrollment.objects.create(
                course=course_request.course,
                student_id=course_request.auditor_id
            )
        
        return Response(
            {'status': 'success', 'message': f'Request {new_status}'},
            status=status.HTTP_200_OK
        )
    
    except CourseRequest.DoesNotExist:
        return Response(
            {'status': 'error', 'message': 'Request not found'},
            status=status.HTTP_404_NOT_FOUND
        )