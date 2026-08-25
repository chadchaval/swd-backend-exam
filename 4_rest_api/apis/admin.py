from django.contrib import admin

from apis.models import Classroom, School, Student, Teacher


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation", "address"]
    search_fields = ["name", "abbreviation"]


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ["school", "grade", "room"]
    list_filter = ["school", "grade", "room"]
    list_select_related = ["school"] 


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "gender"]
    list_filter = ["gender"]
    search_fields = ["first_name", "last_name"]
    filter_horizontal = ["classrooms"] #สำหรับ M2M


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "gender", "classroom"]
    list_filter = ["gender", "classroom__school"]
    search_fields = ["first_name", "last_name"]
    list_select_related = ["classroom"] 
