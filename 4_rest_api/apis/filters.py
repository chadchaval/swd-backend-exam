from django_filters import FilterSet, filters

from apis.models import Classroom, School, Student, Teacher


class SchoolFilter(FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = School
        fields = ["name"]


class ClassroomFilter(FilterSet):
    school = filters.NumberFilter(field_name="school")

    class Meta:
        model = Classroom
        fields = ["school"]


class TeacherFilter(FilterSet):
    #distinct=True เพราะครู 1 คนที่สอนหลายห้อง จะถูก JOIN ออกมาซ้ำหลายแถว
    school = filters.NumberFilter(field_name="classrooms__school", distinct=True)
    classroom = filters.NumberFilter(field_name="classrooms", distinct=True)
    first_name = filters.CharFilter(lookup_expr="icontains")
    last_name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Teacher
        fields = ["school", "classroom", "first_name", "last_name", "gender"]


class StudentFilter(FilterSet):
    #Student อยู่ได้ห้องเดียว การ JOIN จึงไม่ทำให้เกิดแถวซ้ำ ไม่ต้องใช้ distinct
    school = filters.NumberFilter(field_name="classroom__school")
    classroom = filters.NumberFilter(field_name="classroom")
    first_name = filters.CharFilter(lookup_expr="icontains")
    last_name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Student
        fields = ["school", "classroom", "first_name", "last_name", "gender"]
