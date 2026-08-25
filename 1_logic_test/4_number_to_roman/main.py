"""
เขียบนโปรแกรมแปลงตัวเลยเป็นตัวเลข roman

[Input]
number: list of numbers

[Output]
roman_text: roman number

[Example 1]
input = 101
output = CI

[Example 2]
input = -1
output = number can not less than 0
"""


class Solution:

    ROMAN_NUMERALS = ( #เรียงจากค่ามากไปน้อย เพื่อให้ไล่หักค่าจากแบบใหญ่สุดก่อน
        (1000, "M"),
        (900, "CM"), #รูปแบบลบ 900 = 1000 - 100 ถ้าไม่ใส่คู่นี้ 900 จะกลายเป็น DCCCC
        (500, "D"),
        (400, "CD"), #รูปแบบลบ 400 = 500 - 100
        (100, "C"),
        (90, "XC"), #รูปแบบลบ 90 = 100 - 10
        (50, "L"),
        (40, "XL"), #รูปแบบลบ 40 = 50 - 10
        (10, "X"),
        (9, "IX"), #รูปแบบลบ 9 = 10 - 1
        (5, "V"),
        (4, "IV"), #รูปแบบลบ 4 = 5 - 1 ถ้าไม่ใส่คู่นี้ 4 จะกลายเป็น IIII
        (1, "I"),
    )

    def number_to_roman(self, number: int) -> str:
        if number < 0:
            return "number can not less than 0"

        parts = [] 
        for value, symbol in self.ROMAN_NUMERALS: 
            count, number = divmod(number, value) # หารเอาเศษและตัวหารออกจากกัน เช่น 101 // 100 = 1 และ 101 % 100 = 1
            parts.append(symbol * count) #คูณ string เช่น "X" * 3 ได้ XXX / ถ้า count เป็น 0 จะได้ค่าว่าง
        return "".join(parts) #ต่อ array เข้าด้วยกันเป็นคำตอบเดียว
