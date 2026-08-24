"""
เขียบนโปรแกรมแปลงตัวเลยเป็นคำอ่านภาษาไทย

[Input]
number: positive number rang from 0 to 10_000_000

[Output]
num_text: string of thai number call

[Example 1]
input = 101
output = หนึ่งร้อยเอ็ด

[Example 2]
input = -1
output = number can not less than 0
"""


class Solution:

    DIGITS = ("", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า") 
    PLACES = ("", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน") 

    def number_to_thai(self, number: int) -> str:
        if number < 0:
            return "number can not less than 0"
        if number == 0:
            return "ศูนย์"

        if number >= 1_000_000: #ตั้งแต่ 1 ล้านขึ้นไป ภาษาไทยอ่านเป็นกลุ่มละ 6 หลัก คั่นด้วยคำว่าล้าน จึงต้องแยกอ่าน
            millions, remainder = divmod(number, 1_000_000) #หั่นเป็น 2 กลุ่ม เช่น 1000021 จะได้ millions = 1 และ remainder = 21
            text = self._read_below_million(millions) + "ล้าน" #อ่านกลุ่มหน้าด้วยตัวอ่านตัวเดิม แล้วต่อคำว่าล้าน
            if remainder: #ถ้าเศษเป็น 0 ไม่ต้องทำต่อ
                text += self._read_below_million(remainder, has_higher_group=True) #ส่ง True บอกว่ามีกลุ่มล้านนำหน้าอยู่ เพื่อให้ 1000001 อ่านว่า หนึ่งล้านเอ็ด
            return text

        return self._read_below_million(number) #น้อยกว่า 1 ล้าน อ่านตัวเลขปกติ

    def _read_below_million(self, number: int, has_higher_group: bool = False) -> str: 
        digits = str(number)  #แปลงเป็น string เพื่อไล่อ่านทีละหลัก
        length = len(digits) #เพื่อใช้คำนวนหลักของตัวเลข เช่น 1234 มี length = 4
        text = ""

        for position, digit in enumerate(digits): # loop อ่านตัวเลขทีละหลักจากซ้ายไปขวา / enumerate() จะแถม เลขลำดับ มาให้ด้วย โดย position นับจาก 0
            value = int(digit) 
            if value == 0:
                continue  #หลักที่เป็น 0 ไม่ต้องอ่าน เช่น 20105 อ่านว่า สองหมื่นหนึ่งร้อยห้า

            place = length - position - 1  # place คือหลักของตัวเลข / 0 คือหน่วย, 1 คือสิบ, 2 คือร้อย / -1 เพราะ position เริ่มจาก 0 และ length เริ่มจาก 1

            if place == 1 and value == 1:
                text += self.PLACES[place] 
            elif place == 1 and value == 2:
                text += "ยี่" + self.PLACES[place]  
            elif place == 0 and value == 1 and (length > 1 or has_higher_group):
                text += "เอ็ด"  
            else:
                text += self.DIGITS[value] + self.PLACES[place]  #กรณีปกติ ต่อคำอ่านตัวเลขกับคำอ่านหลัก

        return text
