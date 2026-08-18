class ExerciseModel():
    def __init__(self, id: str, name: str, user_id:str):
        self.name = name.strip().capitalize() if name else name
        self.id = id
        self.user_id = user_id

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

## TODO: Refatorar esse model para usar dataclass