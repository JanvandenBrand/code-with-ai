import numpy as np

def calculate_circle_area(radius):
    if not isinstance(radius, (int, float)):
        raise TypeError("Radius must be a numeric value.")
    if radius <= 0:
        raise ValueError("Radius must be greater than zero.")
    area = np.pi * np.power(radius, 2)
    return area

# Example usage:
try:
    radius = 5
    area = calculate_circle_area(radius)
    print(f"The area of the circle with radius {radius} is {area}")
except (ValueError, TypeError) as e:
    print(e)