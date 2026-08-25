from rest_framework import serializers

from apis.models import Classroom, School, Student, Teacher


#Brief serializers ใช้เป็นรายการใน Detail กันข้อมูลบวม
class TeacherBriefSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Teacher
        fields = ["id", "first_name", "last_name", "gender"]


class StudentBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "first_name", "last_name", "gender"]


class ClassroomBriefSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Classroom
        fields = ["id", "school", "school_name", "grade", "room"]


#Base serializers CRUD ใช้เป็นการ List / Create / Update
#Detail serializers ใช้แสดงรายการที่มี Detail และ สืบทอดจาก Base และ Brief ไม่มี field ซ้ำ


#School 
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "abbreviation", "address", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SchoolDetailSerializer(SchoolSerializer):
    classroom_count = serializers.IntegerField(read_only=True)
    teacher_count = serializers.IntegerField(read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    #ปัญหา N+1
    #classroom_count = serializers.SerializerMethodField() และใช้ obj.classrooms.count() ได้ N+1 query
    #IntegerField + annotate ที่ viewset ได้ 1 query

    class Meta(SchoolSerializer.Meta): #Meta ของ Detail ไม่สืบทอด School ให้อัตโนมัติ / ต้องใส่เอง
        fields = SchoolSerializer.Meta.fields + [
            "classroom_count",
            "teacher_count",
            "student_count",
        ]


#Classroom 
class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ["id", "school", "grade", "room", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
class ClassroomDetailSerializer(ClassroomSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    teachers = TeacherBriefSerializer(many=True, read_only=True) #ถ้าใช้ TeacherSerializer ตัวเต็ม จะพ่วง classrooms มาด้วย
    students = StudentBriefSerializer(many=True, read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = ClassroomSerializer.Meta.fields + [
            "school_name",
            "teachers",
            "students",
        ]


#Teacher 
class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "classrooms",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
class TeacherDetailSerializer(TeacherSerializer):
    classrooms = ClassroomBriefSerializer(many=True, read_only=True)



#Student
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "classroom",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentDetailSerializer(StudentSerializer):
    classroom = ClassroomBriefSerializer(read_only=True)
