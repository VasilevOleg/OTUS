from abc import ABC
from .exceptions import LowFuelError, NotEnoughFuel


class Vehicle(ABC):
    def __init__(self, weight, fuel, fuel_consumption):
        self.weight = weight
        self.started = False
        self.fuel = fuel
        self.fuel_consumption = fuel_consumption

    def start(self):
        if self.started:
            return
        if self.fuel <= 0:
            raise LowFuelError
        self.started = True

    def move(self, distance):
        required_fuel = distance * self.fuel_consumption
        if self.fuel < required_fuel:
            raise NotEnoughFuel
        self.fuel -= required_fuel
