from django.db.models import Count
from rest_framework import viewsets

from apis.filters import SchoolFilter
from apis.models import School
from apis.serializers import SchoolDetailSerializer, SchoolSerializer
from apis.views.v1.mixins import ProtectedDeleteMixin


class SchoolViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filterset_class = SchoolFilter
    protected_error_detail = "Cannot delete a school that still has students."

    def get_queryset(self):
        queryset = School.objects.all()
        if self.action == "retrieve":  
            #annotate เฉพาะตอน retrieve เพราะ list ไม่ได้ใช้ค่าพวกนี้ ไม่ต้องให้ DB ทำงานเปล่า
            queryset = queryset.annotate(
                classroom_count=Count("classrooms", distinct=True),
                teacher_count=Count("classrooms__teachers", distinct=True),#distinct=True เพราะการ annotate หลาย relation พร้อมกันจะ JOIN ซ้อนกัน
                student_count=Count("classrooms__students", distinct=True),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SchoolDetailSerializer
        return SchoolSerializer
