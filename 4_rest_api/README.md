# School REST API

API สำหรับจัดการข้อมูลโรงเรียนและบุคลากรในโรงเรียน (ครูและนักเรียน) พัฒนาด้วย Django REST Framework
โจทย์: [api_exam.md](api_exam.md)

## หมายเหตุเรื่องการใช้ AI

พัฒนาโปรเจกต์นี้โดยใช้ AI ช่วยในลักษณะ pair programming ทั้งการร่างโค้ดและอธิบายแนวคิด
โดยเฉพาะ `apis/tests.py` และ `README.md` ซึ่งเป็นงานที่ใช้เวลามาก

การตัดสินใจเชิงออกแบบทุกข้อในหัวข้อด้านล่างเป็นการเลือกของผมเอง
และได้ตรวจสอบกับผลรันจริงทุกส่วนก่อนส่ง

## เทคโนโลยีที่ใช้

|                       |                                 |
| :-------------------- | :------------------------------ |
| Python                | 3.10                            |
| Django                | 5.0.4                           |
| Django REST Framework | 3.15.1                          |
| django-filter         | 24.2                            |
| ฐานข้อมูล             | SQLite (ค่าเริ่มต้นของโปรเจกต์) |

## วิธีติดตั้งและรัน

```bash
cd 4_rest_api
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

ทุก endpoint ต้อง authenticate ก่อน เนื่องจากโปรเจกต์ตั้ง `IsAuthenticated` ไว้เป็นค่าเริ่มต้น
วิธีที่สะดวกที่สุดคือ login ที่ `http://127.0.0.1:8000/admin/` ก่อน เพราะ session เดียวกันใช้กับ API ได้
จากนั้นเปิด browsable API ที่ `http://127.0.0.1:8000/api/v1/` ได้ทันที

ทุก model ถูกลงทะเบียนใน Django admin ไว้แล้ว จึงใช้หน้า admin ใส่ข้อมูลทดสอบได้เลย

## วิธีรันเทส

```bash
python manage.py test apis
```

มีเทสทั้งหมด 30 ข้อ ครอบคลุม CRUD, filter ทุกตัวที่โจทย์ระบุ, ข้อมูลใน detail
และกรณีข้อผิดพลาด (ห้องเรียนซ้ำ, ชั้นปีไม่ถูกต้อง, ลบข้อมูลที่ถูกอ้างอิงอยู่, id ที่ไม่มีในระบบ, เข้าถึงโดยไม่ login)

## รายการ Endpoint

Base path: `/api/v1/`

| Resource      | filter ที่ list รองรับ                                     | ข้อมูลเพิ่มเติมใน detail                            |
| :------------ | :--------------------------------------------------------- | :-------------------------------------------------- |
| `schools/`    | `name` (ค้นบางส่วน ไม่สนตัวพิมพ์เล็กใหญ่)                  | `classroom_count`, `teacher_count`, `student_count` |
| `classrooms/` | `school`                                                   | `teachers[]`, `students[]`, `school_name`           |
| `teachers/`   | `school`, `classroom`, `first_name`, `last_name`, `gender` | `classrooms[]` (แสดงเป็น object)                    |
| `students/`   | `school`, `classroom`, `first_name`, `last_name`, `gender` | `classroom` (แสดงเป็น object)                       |

ทุก resource รองรับ CRUD ครบ: `GET` list, `POST` create, `GET` detail, `PUT`/`PATCH` update, `DELETE`

ตัวอย่างการเรียกใช้:

```bash
curl -u admin:<password> "http://127.0.0.1:8000/api/v1/schools/?name=assum" -H "Accept: application/json"
curl -u admin:<password> "http://127.0.0.1:8000/api/v1/teachers/?school=1&gender=M" -H "Accept: application/json"
curl -u admin:<password> "http://127.0.0.1:8000/api/v1/students/?last_name=suk" -H "Accept: application/json"
```

## โครงสร้างไฟล์

```
apis/
├── models.py              # School, Classroom, Teacher, Student
├── serializers.py         # serializer แยกเป็น brief / base / detail ของแต่ละ resource
├── filters.py             # FilterSet หนึ่งตัวต่อหนึ่ง resource
├── admin.py               # ลงทะเบียน model เพื่อใส่ข้อมูลและตรวจสอบ
├── tests.py               # เทส API 30 ข้อ
└── views/v1/
    ├── mixins.py          # ProtectedDeleteMixin (ตอบ 409 แทน 500)
    ├── school.py
    ├── classroom.py
    ├── teacher.py
    └── student.py
```

แยก view เป็นไฟล์ละ resource และอยู่ภายใต้ `v1/` ตามโครงที่ scaffold วางไว้ให้
เพื่อให้เพิ่ม `v2` ในอนาคตได้โดยไม่ต้องแก้ของเดิม

---

# การตัดสินใจในการออกแบบ

โจทย์ไม่ได้ระบุบางเรื่องไว้ ส่วนนี้สรุปเฉพาะสิ่งที่เลือกและเหตุผลโดยย่อ
รายละเอียดดูได้จากโค้ดและ comment ในไฟล์ที่อ้างถึง

### 1. ความสัมพันธ์กับโรงเรียน

ไฟล์: `models.py`

- **เลือก:** Teacher และ Student ไม่มี FK ตรงไป School แต่เข้าถึงผ่าน classroom
- **เหตุผล:** ให้มีแหล่งข้อมูลจริงที่เดียว กันกรณีนักเรียนสังกัดคนละโรงเรียนกับห้องเรียนของตัวเอง
- **แลกกับ:** ครูที่ยังไม่ได้รับห้องจะไม่ปรากฏใน `?school=` และไม่ถูกนับใน `teacher_count`

### 2. พฤติกรรมการลบ

ไฟล์: `models.py`, `views/v1/mixins.py`

- **เลือก:** `Classroom.school` ใช้ CASCADE ส่วน `Student.classroom` ใช้ PROTECT
- **เหตุผล:** ห้องเรียนไม่มีความหมายถ้าไม่มีโรงเรียน แต่การยุบห้องต้องไม่ลบประวัตินักเรียน
- **ผลที่ตามมา:** ดัก `ProtectedError` แล้วตอบ 409 แทนที่จะปล่อยเป็น 500

### 3. การนับข้อมูลใน school detail

ไฟล์: `views/v1/school.py`

- **เลือก:** ใช้ `annotate` พร้อม `distinct=True` และทำเฉพาะตอน retrieve
- **เหตุผล:** ถ้านับใน serializer จะเกิด N+1 และถ้าไม่ใส่ `distinct` ตัวเลขจะเบิ้ลจากการ JOIN หลายความสัมพันธ์พร้อมกัน

### 4. ประสิทธิภาพ query

ไฟล์: `views/v1/`

- **เลือก:** `select_related` กับ FK และ `prefetch_related` กับความสัมพันธ์ฝั่งที่มีได้หลายตัว
- **เหตุผล:** ทำให้จำนวน query คงที่ ไม่เพิ่มตามจำนวนแถว (list ใช้ 1 ถึง 3 query)

## สิ่งที่ยังไม่ได้ทำ

- **Pagination** ยังไม่ได้เปิดใช้งาน list endpoint จึงคืนข้อมูลทั้งหมด หากใช้งานจริงควรเปิด `PageNumberPagination` ก่อนที่ข้อมูลจะมีจำนวนมาก
- **การแยกสิทธิ์ตาม role** ยังไม่มี ผู้ใช้ที่ login แล้วทุกคนทำได้ทุก action ระบบจริงควรจำกัดการเขียนข้อมูลไว้เฉพาะบัญชีเจ้าหน้าที่
