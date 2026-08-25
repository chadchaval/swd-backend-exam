from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apis.models import Classroom, School, Student, Teacher


class BaseAPITestCase(APITestCase):
    #สร้างข้อมูลชุดเดียวใช้ร่วมกันทุก test
    #โรงเรียน 2 แห่ง ครู 1 คนสอน 2 ห้องในโรงเรียนเดียวกัน นักเรียน 3 คน
    def setUp(self):
        self.user = User.objects.create_user("tester", password="test1234")
        self.client.force_authenticate(user=self.user)

        self.school_a = School.objects.create(
            name="Assumption College", abbreviation="ACC", address="Bangkok"
        )
        self.school_b = School.objects.create(
            name="Bangkok Christian", abbreviation="BCC", address="Bangkok"
        )

        self.room_a1 = Classroom.objects.create(school=self.school_a, grade=6, room=1)
        self.room_a2 = Classroom.objects.create(school=self.school_a, grade=6, room=2)
        self.room_b1 = Classroom.objects.create(school=self.school_b, grade=5, room=1)

        self.teacher = Teacher.objects.create(
            first_name="Somchai", last_name="Jaidee", gender="M"
        )
        self.teacher.classrooms.set([self.room_a1, self.room_a2])

        self.student_1 = Student.objects.create(
            first_name="Anan", last_name="Suksa", gender="M", classroom=self.room_a1
        )
        self.student_2 = Student.objects.create(
            first_name="Benja", last_name="Suksa", gender="F", classroom=self.room_a2
        )
        self.student_3 = Student.objects.create(
            first_name="Chai", last_name="Rakdee", gender="M", classroom=self.room_b1
        )


class AuthenticationTests(BaseAPITestCase):
    #ทุก endpoint ต้อง login ก่อน เพราะ settings ตั้ง IsAuthenticated ไว้ระดับโปรเจกต์
    def test_anonymous_user_is_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/schools/")
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class SchoolAPITests(BaseAPITestCase):
    #ครบ CRUD ตาม requirement ของ school api
    def test_create_school(self):
        response = self.client.post(
            "/api/v1/schools/",
            {"name": "Debsirin", "abbreviation": "DS", "address": "Bangkok"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(School.objects.count(), 3)

    def test_update_school(self):
        response = self.client.patch(
            f"/api/v1/schools/{self.school_a.id}/",
            {"address": "Sathorn"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.school_a.refresh_from_db()
        self.assertEqual(self.school_a.address, "Sathorn")

    def test_delete_school_without_student(self):
        empty_school = School.objects.create(
            name="Empty", abbreviation="EMP", address="x"
        )
        response = self.client.delete(f"/api/v1/schools/{empty_school.id}/")
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK],
        )

    #โจทย์ระบุว่า school list ต้อง filter ด้วย name ได้
    #ใช้ icontains จึงต้องค้นด้วยคำบางส่วนและตัวพิมพ์เล็กได้
    def test_filter_school_by_partial_name(self):
        response = self.client.get("/api/v1/schools/?name=assum")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Assumption College")

    #โจทย์ระบุว่า school detail ต้องบอกจำนวน classroom teacher student
    #ข้อนี้สำคัญที่สุดของไฟล์ ถ้า annotate ไม่ได้ใส่ distinct=True ตัวเลขจะเบิ้ลจากการ JOIN ซ้อนกัน
    #โรงเรียน A มี 2 ห้อง ครู 1 คน (สอน 2 ห้อง) นักเรียน 2 คน
    def test_school_detail_returns_correct_counts(self):
        response = self.client.get(f"/api/v1/schools/{self.school_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["classroom_count"], 2)
        self.assertEqual(response.data["teacher_count"], 1)
        self.assertEqual(response.data["student_count"], 2)

    #ลบโรงเรียนที่ยังมีนักเรียนไม่ได้ เพราะ Student.classroom ใช้ on_delete=PROTECT
    #ต้องได้ 409 ไม่ใช่ 500 เพราะ ProtectedDeleteMixin ดักไว้แล้ว
    def test_delete_school_with_student_returns_409(self):
        response = self.client.delete(f"/api/v1/schools/{self.school_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(School.objects.filter(id=self.school_a.id).exists())


class ClassroomAPITests(BaseAPITestCase):
    def test_create_classroom(self):
        response = self.client.post(
            "/api/v1/classrooms/",
            {"school": self.school_a.id, "grade": 4, "room": 3},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #โจทย์ระบุว่า classroom list ต้อง filter ด้วย school ได้
    def test_filter_classroom_by_school(self):
        response = self.client.get(f"/api/v1/classrooms/?school={self.school_a.id}")
        self.assertEqual(len(response.data), 2)

    #โจทย์ระบุว่า classroom detail ต้องมี list ของครูและนักเรียน
    def test_classroom_detail_contains_teacher_and_student_list(self):
        response = self.client.get(f"/api/v1/classrooms/{self.room_a1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["teachers"]), 1)
        self.assertEqual(len(response.data["students"]), 1)
        self.assertEqual(response.data["teachers"][0]["first_name"], "Somchai")

    #UniqueConstraint ในโมเดลกันห้องซ้ำในโรงเรียนเดียวกัน
    #DRF แปลงเป็น UniqueTogetherValidator ให้เอง จึงได้ 400 ไม่ใช่ 500 จาก IntegrityError
    def test_duplicate_classroom_in_same_school_returns_400(self):
        response = self.client.post(
            "/api/v1/classrooms/",
            {"school": self.school_a.id, "grade": 6, "room": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #ห้องเลขเดียวกันแต่คนละโรงเรียนต้องสร้างได้ เพราะ constraint ผูกกับ school ด้วย
    def test_same_room_number_in_another_school_is_allowed(self):
        response = self.client.post(
            "/api/v1/classrooms/",
            {"school": self.school_b.id, "grade": 6, "room": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #MinValueValidator(1) กันชั้นปีหรือห้องที่เป็น 0 ซึ่งไม่มีอยู่จริง
    def test_grade_zero_is_rejected(self):
        response = self.client.post(
            "/api/v1/classrooms/",
            {"school": self.school_a.id, "grade": 0, "room": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #ลบห้องที่ยังมีนักเรียนไม่ได้ ต้องย้ายนักเรียนออกก่อน
    def test_delete_classroom_with_student_returns_409(self):
        response = self.client.delete(f"/api/v1/classrooms/{self.room_a1.id}/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    #ห้องที่ไม่มีนักเรียนลบได้ตามปกติ
    def test_delete_empty_classroom(self):
        empty_room = Classroom.objects.create(school=self.school_a, grade=1, room=9)
        response = self.client.delete(f"/api/v1/classrooms/{empty_room.id}/")
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK],
        )


class TeacherAPITests(BaseAPITestCase):
    def test_create_teacher_with_classrooms(self):
        response = self.client.post(
            "/api/v1/teachers/",
            {
                "first_name": "Malee",
                "last_name": "Sudjai",
                "gender": "F",
                "classrooms": [self.room_b1.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Teacher ไม่มี field school จึง filter ผ่าน classrooms__school
    #ครู 1 คนสอน 2 ห้องในโรงเรียนเดียวกัน ถ้าไม่ใส่ distinct=True จะถูก JOIN ออกมาซ้ำเป็น 2 แถว
    def test_filter_teacher_by_school_has_no_duplicate(self):
        response = self.client.get(f"/api/v1/teachers/?school={self.school_a.id}")
        self.assertEqual(len(response.data), 1)

    def test_filter_teacher_by_classroom(self):
        response = self.client.get(f"/api/v1/teachers/?classroom={self.room_a1.id}")
        self.assertEqual(len(response.data), 1)

    #ชื่อและนามสกุลใช้ icontains ค้นบางส่วนได้และไม่สนตัวพิมพ์เล็กใหญ่
    def test_filter_teacher_by_partial_first_name(self):
        response = self.client.get("/api/v1/teachers/?first_name=som")
        self.assertEqual(len(response.data), 1)

    #gender เป็น TextChoices django-filter จึงสร้าง ChoiceFilter ให้อัตโนมัติ
    def test_filter_teacher_by_gender(self):
        response = self.client.get("/api/v1/teachers/?gender=F")
        self.assertEqual(len(response.data), 0)

    #โจทย์ระบุว่า teacher detail ต้องมี list ของห้องเรียน
    #detail แสดงเป็น object ส่วน list แสดงเป็น id เพราะต้องใช้ส่งตอน create หรือ update
    def test_teacher_detail_contains_classroom_list(self):
        response = self.client.get(f"/api/v1/teachers/{self.teacher.id}/")
        self.assertEqual(len(response.data["classrooms"]), 2)
        self.assertIn("grade", response.data["classrooms"][0])

    def test_teacher_list_returns_classroom_ids(self):
        response = self.client.get("/api/v1/teachers/")
        self.assertEqual(response.data[0]["classrooms"], [self.room_a1.id, self.room_a2.id])


class StudentAPITests(BaseAPITestCase):
    def test_create_student(self):
        response = self.client.post(
            "/api/v1/students/",
            {
                "first_name": "Dara",
                "last_name": "Mekmai",
                "gender": "F",
                "classroom": self.room_b1.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #Student ไม่มี field school เช่นกัน filter ผ่าน classroom__school
    #ไม่ต้องใช้ distinct เพราะนักเรียนอยู่ได้ห้องเดียว การ JOIN จึงไม่ทำให้เกิดแถวซ้ำ
    def test_filter_student_by_school(self):
        response = self.client.get(f"/api/v1/students/?school={self.school_a.id}")
        self.assertEqual(len(response.data), 2)

    def test_filter_student_by_classroom(self):
        response = self.client.get(f"/api/v1/students/?classroom={self.room_a1.id}")
        self.assertEqual(len(response.data), 1)

    #นามสกุลซ้ำกัน 2 คน ใช้ทดสอบว่า icontains คืนได้มากกว่า 1 แถว
    def test_filter_student_by_partial_last_name(self):
        response = self.client.get("/api/v1/students/?last_name=suk")
        self.assertEqual(len(response.data), 2)

    #ผสมหลาย filter พร้อมกันต้องทำงานร่วมกันแบบ AND
    def test_filter_student_by_school_and_gender(self):
        response = self.client.get(
            f"/api/v1/students/?school={self.school_a.id}&gender=M"
        )
        self.assertEqual(len(response.data), 1)

    #โจทย์ระบุว่า student detail ต้องบอกห้องเรียน โดยแสดงเป็น object พร้อมชื่อโรงเรียน
    def test_student_detail_contains_classroom_object(self):
        response = self.client.get(f"/api/v1/students/{self.student_1.id}/")
        self.assertEqual(response.data["classroom"]["id"], self.room_a1.id)
        self.assertEqual(response.data["classroom"]["school_name"], "Assumption College")

    #ลบนักเรียนได้ตามปกติ PROTECT กันแค่การลบห้องเรียนที่ยังมีนักเรียนอยู่
    def test_delete_student(self):
        response = self.client.delete(f"/api/v1/students/{self.student_1.id}/")
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK],
        )
        self.assertFalse(Student.objects.filter(id=self.student_1.id).exists())

    #id ที่ไม่มีในระบบต้องได้ 404 ไม่ใช่ 500
    def test_retrieve_unknown_student_returns_404(self):
        response = self.client.get("/api/v1/students/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
