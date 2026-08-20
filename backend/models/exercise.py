from dataclasses import dataclass



@dataclass
class ExerciseModel():
    name: str
    id: str
    user_id: str

    def to_dict(self):
        return {
            "id": self.id,
            "Name": self.name,
            "User_id": self.user_id
        }

    @staticmethod
    def from_dict(data: dict):
        return ExerciseModel(
            id=data.get("id"),
            name=data.get("Name"),
            user_id=data.get("User_id")
        )