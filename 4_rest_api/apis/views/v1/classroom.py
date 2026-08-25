from rest_framework import viewsets

from apis.filters import ClassroomFilter
from apis.models import Classroom
from apis.serializers import ClassroomDetailSerializer, ClassroomSerializer
from apis.views.v1.mixins import ProtectedDeleteMixin


class ClassroomViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    filterset_class = ClassroomFilter
    protected_error_detail = "Cannot delete a classroom that still has students."

    def get_queryset(self):
        #select_related ดึงโรงเรียนมาพร้อมกันใน query เดียว กัน N+1 ตอน serializer อ่าน school.name
        queryset = Classroom.objects.select_related("school")
        if self.action == "retrieve":
            #teachers และ students เป็นความสัมพันธ์แบบหลายตัว ต้องใช้ prefetch_related ไม่ใช่ select_related
            queryset = queryset.prefetch_related("teachers", "students")
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ClassroomDetailSerializer
        return ClassroomSerializer
