## Question

![](/assets/q_data_format.png)

## Response Section

ความแตกต่างหลัก
JSON = ข้อความ(text) ที่อธิบายตัวเองได้ เข้าใจง่าย แต่ใหญ่
Protobuf = ไบนารีที่ต้องมี schema ถึงจะอ่านออก แต่เล็ก ปลอดภัยเรื่องชนิดข้อมูล

Protobuf เล็กกว่า JSON เพราะ
JSON ส่งแบบ (ชื่อ field ติดไปด้วยทุกครั้ง ทุก record):
{"firstname":"somchai","age":30} = 32 bytes

Protobuf ส่งแค่ "เลขประจำ field + ค่า":
0A 07 somchai 10 1E = 11 bytes

---

JSON
ข้อดี
คนอ่านออก: debug ง่ายมาก เปิด curl/Postman/browser ดูได้เลย
ไม่ต้อง compile: แก้แล้วใช้ได้ทันที ไม่มีขั้นตอน generate code
รองรับทุกที่: native ใน JavaScript/browser, ทุกภาษามี library ในตัว
ยืดหยุ่น: เพิ่ม/ลด field ได้อิสระ เหมาะกับตอนที่ API ยังเปลี่ยนบ่อย
คนคุ้นเคย: คนใหม่เข้าทีมได้เร็ว เครื่องมือเยอะ

ข้อเสีย
ขนาดใหญ่: ส่งชื่อ field ซ้ำไปทุก record
parse ช้ากว่า: ต้องอ่านตัวอักษรทีละตัวแล้วแปลง
ชนิดข้อมูลอ่อน: ไม่มี int64 แท้ (เลขใหญ่เพี้ยนใน JS) วันที่ต้องส่งเป็น string, ไม่มี binary type
ไม่มี schema บังคับ: พังตอน runtime ไม่ใช่ตอน compile ถ้าฝั่งใดฝั่งหนึ่งเปลี่ยนโครงแล้วไม่บอก

---

Protocol Buffer
ข้อดี
เล็กกว่ามาก: ประหยัด bandwidth ชัดเจนเมื่อ traffic สูงหรือเน็ตช้า
เร็วกว่า: ทั้ง encode และ decode
มี schema: ชัดเจน เป็นเอกสารในตัว ทีมสองฝั่งเถียงกันไม่ได้
type-safe: ผิด type รู้ตั้งแต่ตอน generate/compile ไม่ใช่ตอน production
จัดการ schema evolution ได้เป็นระบบ: เพิ่ม field ใหม่โดยไม่พังของเก่า เพราะยึด field number ไม่ใช่ชื่อ

ข้อเสีย
คนอ่านไม่ออก: debug ยาก ต้องมีเครื่องมือถอดรหัส
มีขั้นตอนเพิ่ม: ต้อง compile / generate code ทุกครั้งที่แก้ schema
ต้อง sync: .proto ระหว่างทีม/service ถ้าคนละเวอร์ชันก็พัง
browser ไม่รองรับตรงๆ: ต้องใช้ grpc-web หรือมี proxy คั่น
overkill: สำหรับ API เล็กๆ ที่ traffic ไม่เยอะ

---

สถานการณ์จริงเลือกยังไง
Public API / frontend เป็น web = JSON debug ง่าย คนอื่นเอาไปใช้ต่อง่าย
API ที่ยังเปลี่ยนบ่อย ทีมเล็ก = JSON ไม่ต้องมีขั้นตอน codegen
Service ภายในคุยกันเอง traffic สูง = Protobuf
Mobile ที่ bandwidth จำกัด = Protobuf
