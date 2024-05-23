from .base import Vehicle
from .engine import Engine


class Car(Vehicle):
    def __init__(self, weight, fuel, fuel_consumption):
        super().__init__(weight, fuel, fuel_consumption)
        self.engine = None

    def set_engine(self, engine: Engine):
        self.engine = engine
