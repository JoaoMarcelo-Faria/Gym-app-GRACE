from backend.models.exercise import ExerciseModel


class WorkoutModel():
    def __init__(
            self, 
            Name: str, 
            Weekday: str, 
            id: str,
            user_id: str,
            exs_order: list[ExerciseModel]
        ):
        self.id = id
        self.name = Name.strip().capitalize() if Name else Name
        self.weekday = Weekday
        self.user_id = user_id
        self.order = exs_order

    def to_dict(self):
        exs_list = []
        if self.order:
            for exercise in self.order:
                exs_list.append(exercise.to_dict())
        
        return {
            "id": self.id,
            "Name": self.name,
            "Weekday": self.weekday,
            "User_id": self.user_id,
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
            user_id=data.get("User_id"),
            exs_order=exs_list
        )

## TODO: Refatorar esse model para usar dataclass