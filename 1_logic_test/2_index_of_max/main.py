"""
เขียบนโปรแกรมหา index ของตัวเลขที่มีค่ามากที่สุดใน list

[Input]
numbers: list of numbers

[Output]
index: index of maximum number in list

[Example 1]
input = [1,2,1,3,5,6,4]
output = 5

[Example 2]
input = []
output = list can not blank
"""


class Solution:

    def find_max_index(self, numbers: list) -> int | str:
        if not numbers:
            return "list can not blank"

        max_index = 0
        for index in range(1, len(numbers)):
            if numbers[index] > numbers[max_index]: #หาเลขที่มากที่สุดใน list โดยเปรียบเทียบค่าของตัวเลขใน list กับค่าที่มากที่สุดที่เจอมาแล้ว
                max_index = index
        return max_index
