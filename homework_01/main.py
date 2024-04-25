def power_numbers(*nums):
    sq = [num ** 2 for num in nums]
    return sq

ODD = "odd"
EVEN = "even"
PRIME = "prime"

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def filter_numbers(nums, filter_numbers_):
    if filter_numbers_ == ODD:
        result = [num for num in nums if num % 2 != 0]
        return result
    elif filter_numbers_ == EVEN:
        result = [num for num in nums if num % 2 == 0]
        return result
    elif filter_numbers_ == PRIME:
        result = [num for num in nums if is_prime(num)]
        return result
