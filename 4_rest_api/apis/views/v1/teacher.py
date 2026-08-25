from rest_framework import viewsets

from apis.filters import TeacherFilter
from apis.models import Teacher
from apis.serializers import TeacherDetailSerializer, TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filterset_class = TeacherFilter

    def get_queryset(self):
        #prefetch และต่อ __school ทั้ง list และ detail เพราะทั้งสองแบบ ต้องอ่าน classrooms ของครูแต่ละคน
        return Teacher.objects.prefetch_related("classrooms__school")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeacherDetailSerializer
        return TeacherSerializer
