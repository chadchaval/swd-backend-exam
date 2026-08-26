## Question

![](/assets/q_idempotency.png)

## Response Section

### Idempotency

การยิงเรียก request เดิมซ้ำกี่ครั้งก็ตาม สถานะของระบบ (state) จะเหมือนกันตลอด แต่ไม่ได้แปลว่า response ต้องเหมือนกันทุกครั้ง

**ตัวอย่าง** `DELETE /users/1`

| ครั้งที่ | เกิดอะไรขึ้น        | ผลลัพธ์ |
| :------- | :------------------ | :------ |
| 1        | ลบ User 1 สำเร็จ    | `204`   |
| 2        | User 1 ไม่มีแล้ว    | `404`   |

ยังถือว่า Idempotent เพราะระบบทำงานเหมือนเดิม

### สำคัญกับ RESTful API เพราะ client เป็นเรื่องปกติ ที่เราควบคุมไม่ได้

- เน็ตหลุด / timeout แล้ว client ยิงซ้ำ
- user กดปุ่มรัวๆ / double-click
- webhook จากระบบอื่น

ถ้า API ไม่ idempotent จะเกิดข้อผิดพลาดของข้อมูลได้หลายอย่าง

---

## ตัวอย่างการ implement ด้วย Python (Django REST Framework)

ถ้า POST ปกติไม่ idempotent เพราะยิงซ้ำจะสร้างข้อมูลใหม่ทุกครั้ง

แก้ได้ด้วยการให้ client ส่ง `Idempotency-Key` มาหนึ่งค่าต่อหนึ่งการกระทำ ถ้า key เดิมถูกส่งเข้ามาอีก server จะคืนผลลัพธ์เดิมโดยไม่ทำงานซ้ำ

### models.py

```python
from django.db import models


class IdempotencyKey(models.Model):
    key = models.CharField(max_length=64, unique=True) #key จาก client
    response_body = models.JSONField(null=True) #สำหรับ คำตอบที่เคยตอบไปแล้ว
    created_at = models.DateTimeField(auto_now_add=True) #เก็บวันที่สำหรับไว้ลบในอนาคต
```

### views.py

```python
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import IdempotencyKey
from .serializers import PaymentSerializer


class CreatePaymentView(APIView):
    def post(self, request):
        key = request.headers.get("Idempotency-Key")
        if not key:
            return Response(
                {"detail": "Idempotency-Key header is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            idempotency_record = IdempotencyKey.objects.create(key=key) #ให้ DB เช็คด้วย unique constraint
        except IntegrityError:
            idempotency_record = IdempotencyKey.objects.get(key=key)
            return Response(
                idempotency_record.response_body, status=status.HTTP_200_OK
            )

        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) #ตรวจข้อมูล ถ้าข้อมูลผิดให้ error 400 ออกไป

        with transaction.atomic(): #ทำงานจริง
            payment = serializer.save()
            idempotency_record.response_body = PaymentSerializer(payment).data
            idempotency_record.save(update_fields=["response_body"])

        return Response(
            idempotency_record.response_body, status=status.HTTP_201_CREATED
        )
```

### อธิบายการทำงาน

1. ถ้า client ไม่ส่ง Idempotency-Key มาจะได้ 400
2. server พยายามสร้าง record ของ key นี้ทันที ถ้าสร้างได้แปลว่าเป็นการเรียกครั้งแรก
3. ถ้าสร้างไม่ได้เพราะติด unique constraint แปลว่า key นี้เคยถูกใช้ไปแล้ว จึงคืนผลลัพธ์ที่บันทึกไว้เดิมโดยไม่สร้างข้อมูลใหม่
4. การเรียกครั้งแรกจะทำงานจริงแล้วเก็บผลลัพธ์ไว้ในตารางเดียวกัน เพื่อให้การเรียกซ้ำครั้งถัดไปมีคำตอบคืนกลับได้

### จุดสำคัญของวิธีนี้

ที่ไม่ใช้วิธีเช็คก่อนว่ามี key นี้แล้วหรือยัง เพราะการเช็คแล้วค่อยสร้างยังมีช่องว่างให้ request สองตัวที่เข้ามาพร้อมกันผ่านด่านไปได้ทั้งคู่ แล้วทำงานซ้ำทั้งคู่ ตัวที่ป้องกันได้จริงคือ unique constraint ที่ระดับฐานข้อมูล เพราะฐานข้อมูลเป็นคนตัดสินว่าใครมาก่อน

การสร้างข้อมูลจริงกับการบันทึกผลลัพธ์ถูกครอบด้วย transaction เดียวกัน ถ้าขั้นตอนใดล้มเหลวจะ rollback ทั้งคู่ ไม่เกิดกรณีที่สร้างข้อมูลไปแล้วแต่ไม่มีผลลัพธ์เก็บไว้

### ข้อควรพิจารณาเมื่อใช้งานจริง

- ควรลบ key ที่เก่าเกินระยะเวลาที่กำหนด เช่น 24 ชั่วโมง เพื่อไม่ให้ตารางโตขึ้นเรื่อย ๆ
- ขอบเขตของ key ควรผูกกับผู้ใช้หรือ API client เพื่อไม่ให้ key ของแต่ละคนชนกัน
- GET, PUT, DELETE ไม่ต้องใช้กลไกนี้ เพราะ idempotent อยู่แล้วโดยธรรมชาติของ method
