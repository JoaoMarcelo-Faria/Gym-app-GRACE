from backend.models.exercise import ExerciseModel
from dataclasses import dataclass

@dataclass
class WorkoutModel():
    Name: str
    Weekday: str
    id: str
    User_id: str
    Order: list[ExerciseModel]

    def to_dict(self):
        exs_list = []
        if self.Order:
            for exercise in self.Order:
                exs_list.append(exercise.to_dict())
        
        return {
            "id": self.id,
            "Name": self.Name,
            "Weekday": self.Weekday,
            "User_id": self.User_id,
            "Order": exs_list
        }

    @staticmethod
    def from_dict(data:dict):
        exs_list = []
        if data.get("Order"):
            for exercise in data.get("Order"):
                ex = ExerciseModel.from_dict(exercise)
                exs_list.append(ex)
        
        return WorkoutModel(
            Name=data.get("Name"),
            Weekday=data.get("Weekday"),
            id=data.get("id"),
            User_id=data.get("User_id"),
            Order=exs_list
        )