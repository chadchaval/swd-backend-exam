"""
เขียนโปรแกรมหาจำนวนเลข 0 ที่อยู่ติดกับหลังสุดของค่า factorial โดยห้ามใช้ function from math

[Input]
number: as an integer

[Output]
count: count of tailing zero as an integer

[Example 1]
input = 7
output = 1

[Example 2]
input = -10
output = number can not be negative
"""


class Solution:

    def find_tailing_zeroes(self, number: int) -> int | str:
        if number < 0:
            return "number can not be negative"
        #ใช้สูตร ⌊n/5⌋ + ⌊n/25⌋ + ⌊n/125⌋ + ... 
        count = 0
        power_of_five = 5 
        while power_of_five <= number: # วนไปเรื่อยๆ ถ้า 5, 25, 125... ยังไม่เกินเลขที่รับมา
            count += number // power_of_five
            power_of_five *= 5  # เพื่อวนหารด้วย 5, 25, 125... ไปเรื่อยๆถ้ายังไม่เกินเลขที่รับมา   เพราะนับเลขที่หาร 5 ลงตัวก่อน แล้วนับเพิ่มอีกรอบสำหรับตัวที่หาร 25 ลงตัว แล้วอีกรอบสำหรับ 125 ไปเรื่อยๆ
        return count