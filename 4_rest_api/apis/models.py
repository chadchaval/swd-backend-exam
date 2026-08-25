from django.db import models
from django.core.validators import MinValueValidator


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True #ไม่สร้างตาราง TimeStampedModel ให้สืบทอด field เฉยๆ


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"


class School(TimeStampedModel):
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=20, unique=True)
    address = models.TextField()

    class Meta:
        ordering = ["name"] 

    def __str__(self):
        return self.name


class Classroom(TimeStampedModel):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="classrooms"
    )
    grade = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    room = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["school", "grade", "room"]
        constraints = [ #6/2 ซ้ำในโรงเรียนเดียวกันไม่ได้
            models.UniqueConstraint(
                fields=["school", "grade", "room"],
                name="uniq_classroom_per_school",
            )
        ]

    def __str__(self):
        return f"{self.school.abbreviation} {self.grade}/{self.room}"


class Teacher(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    classrooms = models.ManyToManyField( #school เข้าถึงผ่าน classroom เพื่อให้มีข้อมูลจริงที่เดียว
        Classroom, related_name="teachers", blank=True 
    )

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Student(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    classroom = models.ForeignKey( #school เข้าถึงผ่าน classroom เพื่อให้มีข้อมูลจริงที่เดียว
        Classroom, on_delete=models.PROTECT, related_name="students" #ถ้ามีนักเรียนแล้ว ไม่ควรลบห้องเรียนหรือโรงเรียนได้
    )

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
