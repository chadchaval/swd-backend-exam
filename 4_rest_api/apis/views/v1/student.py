from rest_framework import viewsets

from apis.filters import StudentFilter
from apis.models import Student
from apis.serializers import StudentDetailSerializer, StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filterset_class = StudentFilter

    def get_queryset(self):
        #ต่อ __school ได้เพราะเป็น FK ทั้งสองชั้น detail จึงอ่านชื่อโรงเรียนได้โดยไม่ยิง query เพิ่ม
        return Student.objects.select_related("classroom__school")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentSerializer
