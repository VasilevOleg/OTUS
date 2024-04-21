"""
Домашнее задание №1
Функции и структуры данных
"""


def power_numbers(*nums):
    sq = [num ** 2 for num in nums]
    print(sq)


power_numbers(3, 5, 6, 7)

# filter types
ODD = "odd"
EVEN = "even"
PRIME = "prime"


def filter_numbers(nums, filter_numbers):
    if filter_numbers == ODD:
        result = [num for num in nums if num % 2 != 0]
        print(result)
    elif filter_numbers == EVEN:
        result = [num for num in nums if num % 2 == 0]
        print(result)
    elif filter_numbers == PRIME:
        def is_prime(n):
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True

        result = [num for num in nums if is_prime(num)]
        print(result)
    else:
        print("Invalid filter type")


filter_numbers([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], EVEN)
