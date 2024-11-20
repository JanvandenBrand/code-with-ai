import time
import timeit
import cProfile
import math


def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def sum_of_primes_naive(numbers):
    total = 0
    for number in numbers:
        if is_prime(number):
            total += number
    return total

# Example usage
numbers = list(range(100000))
sum_of_primes_naive(numbers)

# Measure time using timeit
execution_time = timeit.timeit('sum_of_primes_naive(numbers)', globals=globals(), number=1)
print(f'Time taken: {execution_time}')

cProfile.run('sum_of_primes_naive(numbers)')


def is_prime_optimized(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def sum_of_primes_optimized(numbers):
    total = 0
    for number in numbers:
        if is_prime_optimized(number):
            total += number
    return total

# Measure the time taken by the optimized implementation
start_time = time.time()
total_optimized = sum_of_primes_optimized(numbers)
print(f"Optimized Implementation: Sum of primes = {total_optimized}, Time taken = {time.time() - start_time} seconds")

cProfile.run('sum_of_primes_optimized(numbers)')