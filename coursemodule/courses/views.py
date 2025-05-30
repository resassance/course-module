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
    CourseRequestSerializer,
)

def is_teacher_or_admin(user):
    return user.role == 'teacher' or user.is_staff

@api_view(['GET'])
def course_list_view(request):
    courses = Course.objects.all()
    if not courses.exists():
        return Response({'status': 'error', 'message': 'Courses not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CourseSerializer(courses, many=True)
    return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def last_courses(request):
    latest = Course.objects.order_by('-creation_date')[:3]
    if not latest.exists():
        return Response({'status': 'error', 'message': 'No recent courses'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CourseLastSerializer(latest, many=True)
    return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({'status': 'error', 'message': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_materials(request, pk):
    materials = CourseMaterial.objects.filter(course=pk)
    serializer = CourseMaterialSerializer(materials, many=True)
    return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_enrollments(request, pk):
    if request.method == 'GET':
        if request.user.role in ['teacher'] or request.user.is_superuser:
            enrollments = CourseEnrollment.objects.filter(course=pk)
        else:
            enrollments = CourseEnrollment.objects.filter(course=pk, student_id=request.user.id)

        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        student_id = request.data.get('student_id', request.user.id)
        data = {'course': pk, 'student_id': student_id}

        serializer = CourseEnrollmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_requests(request, pk):
    if request.method == 'GET':
        if is_teacher_or_admin(request.user):
            requests = CourseRequest.objects.filter(course=pk)
        else:
            requests = CourseRequest.objects.filter(course=pk, auditor_id=request.user.id)

        serializer = CourseRequestSerializer(requests, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=200)

    if request.method == 'POST':
        if request.user.role != 'auditor':
            return Response(
                {'status': 'error', 'message': 'Only auditors can request access'},
                status=403
            )

        data = {'course': pk, 'auditor_id': request.user.id}
        serializer = CourseRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'data': serializer.data}, status=201)
        return Response({'status': 'error', 'message': serializer.errors}, status=400)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def handle_request(request, pk):
    if not is_teacher_or_admin(request.user):
        return Response(
            {'status': 'error', 'message': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        course_request = CourseRequest.objects.get(pk=pk)

        new_status = request.data.get('status')
        if new_status not in ['approved', 'rejected']:
            return Response(
                {'status': 'error', 'message': 'Invalid status value'},
                status=400
            )

        course_request.status = new_status
        course_request.save()

        if new_status == 'approved':
            CourseEnrollment.objects.get_or_create(
                course=course_request.course,
                student_id=course_request.auditor_id
            )

        return Response({'status': 'success', 'message': f'Request {new_status}'}, status=200)

    except CourseRequest.DoesNotExist:
        return Response({'status': 'error', 'message': 'Request not found'}, status=404)