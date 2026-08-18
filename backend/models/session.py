from dataclasses import dataclass, field

@dataclass
class ExerciseSessionModel():
    Exercise_id: str
    Reps: int
    Weight: float
    Effort: float = field(init=False)       # O effort não precisa ser passado obrigatoriamente
    id: str
    User_id: str
    Occurency_date: str

    def __post_init__(self):
        # Garantindo a regra de negócio do cálculo de Esforço
        self.effort = self.weight * self.reps
    
    def to_dict(self):
        return {
            "Occurency_date": self.Occurency_date,
            "Exercise_id": self.Exercise_id,
            "Reps": self.Reps,
            "Weight": self.Weight,
            "Effort": self.Effort,
            "id": self.id,
            "User_id": self.User_id
        }

    @staticmethod
    def from_dict(data: dict):
        return ExerciseSessionModel(
            Occurency_date=data.get("Occurency_date"),
            Exercise_id=data.get("Exercise_id"),
            Reps=data.get("Reps"),
            Weight=data.get("Weight"),
            Effort=data.get("Effort"),
            id=data.get("id"),
            User_id=data.get("User_id")
        )

@dataclass
class SessionModel():
    Occurency_date: str
    Workout_id: str
    User_id: str
    id: str
    Data_session: list[ExerciseSessionModel]
    
    def to_dict(self):
        exs_list = []
        if self.Data_session:
            for exercise in self.Data_session:
                exs_list.append(exercise.to_dict())

        return {
            "Occurency_date": self.Occurency_date,
            "Workout_id": self.Workout_id,
            "User_id": self.User_id,
            "id": self.id,
            "Data_session": exs_list
        }

    @staticmethod
    def from_dict(data: dict):
        exs_list = []
        if data.get("Data_session"):
            for exercise in data.get("Data_session"):
                ex = ExerciseSessionModel.from_dict(exercise)
                exs_list.append(ex)

        return SessionModel(
            Occurency_date=data.get("Occurency_date"),
            Workout_id=data.get("Workout_id"),
            User_id=data.get("User_id"),
            id=data.get("id"),
            Data_session=exs_list
        )