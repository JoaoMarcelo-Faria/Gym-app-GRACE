from backend.models.exercise import ExerciseModel
from backend.models.workout import WorkoutModel
from google.cloud import firestore

class ExerciseController():
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection("Exercise")

    def create_exercise(self, data: ExerciseModel):
        ## Verificar a existência de um exercício igual
        exist_exercise = self.collection.where("Name", "==", data.name).where("User_id", "==", data.user_id).limit(1).get()
        if len(exist_exercise) != 0:
            raise ValueError("Já existe um exercício cadastradado com esse nome")

        new_doc_ref = self.collection.document()
        data.id = new_doc_ref.id
        new_doc_ref.set(data.to_dict())

        return data

    def get_exercises(self, user_id: str):
        ## Checar se existe o id de usuário no banco
        exist_user = self.db.collection("User").document(user_id).get()
        if not exist_user.exists:
            raise IndexError("Não existe usuário com esse id")

        exercises = self.collection.where("User_id", "==", user_id).stream()
        response = []       # Lista de dicionarios de exercícios
        for ex in exercises:
            response.append(ex.to_dict())

        return response



class WorkoutController():
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection("Workout")
        self.exercise_controller = ExerciseController(db_client)

    def create_workout(self, data: WorkoutModel):
        exercise_names = [ex.name for ex in data.Order]     # pega todos os nomes dos exercícios a serem criados
        existing_names = {}
        if exercise_names:
            # Faz uma chamada a API do google para complexidade O(1)
            existing_docs = self.db.collection("Exercise").where("User_id", "==", data.User_id).where("Name", "in", exercise_names).stream()
            existing_names = {doc.to_dict().get("Name"): doc.id for doc in existing_docs}       # Permite a busca em O(1)
        exs_list = []
        seen_exercises = set()

        for exercise in data.Order:
            if exercise.name in seen_exercises:
                raise ValueError(f"Não é possível adicionar exercícios duplicados em um treino.")
            seen_exercises.add(exercise.name)
            
            if exercise.name in existing_names:
                exercise.id = existing_names[exercise.name]     # coloca o id do exercicio "antigo" no "novo" exercicio
            else:
                self.exercise_controller.create_exercise(exercise)

            exs_list.append(exercise)
        data.Order = exs_list

        ## Checar se já tem um treino nesse dia da semana
        used_weekday = self.collection.where("Weekday", "==", data.Weekday).where("User_id", "==", data.User_id).limit(1).get()
        if len(used_weekday) != 0:
            ## Checar se é um dia de descanso
            if used_weekday[0].to_dict().get("Name") == "Descanso":
                rest_day_id = used_weekday[0].to_dict().get("id")
                self.delete_workout(rest_day_id, data.User_id)

            ## Se for um treino normal bloqueia
            else:
                raise ValueError("Já existe um treino cadastrado nesse dia")

        ## Checar se já tem um treino com o mesmo nome e não é um dia de decanso
        used_name = self.collection.where("Name", "==", data.Name).where("User_id", "==", data.User_id).limit(1).get()
        if len(used_name) != 0:
            raise ValueError("Já existe um treino cadastrado com esse nome")

        
        new_doc_ref = self.collection.document()
        data.id = new_doc_ref.id
        new_doc_ref.set(data.to_dict())

        return data

    def create_rest_day(self, weekday: str, user_id: str):
        ## Validações 
        # Se tem um treino cadastrado nesse dia
        used_weekday = self.collection.where("Weekday", "==", weekday).where("User_id", "==", user_id).limit(1).get()
        if len(used_weekday) != 0:
            raise ValueError("Já existe um treino cadastrado nesse dia")

        ## Definir o nome e os exercícios
        new_doc_ref = self.collection.document()
        new_id = new_doc_ref.id
        rest_day = WorkoutModel(
            Name="Descanso",
            id=new_id,
            Order=[],
            User_id=user_id,
            Weekday=weekday
        )
        new_doc_ref.set(rest_day.to_dict())

        return rest_day
        

    def get_used_weekdays(self, user_id: str):
        ## Checar se existe o id de usuário no banco
        exist_user = self.db.collection("User").document(user_id).get()
        if not exist_user.exists:
            return None

        workouts = self.collection.where("User_id", "==", user_id).stream()
        used_weekdays = []
        for wrks in workouts:
            data = wrks.to_dict()
            day = data.get("Weekday")
            if day:
                used_weekdays.append(day)

        return used_weekdays

    def get_workouts_by_user(self, user_id: str):
        ## Checar se existe o id de usuário no banco
        exist_user = self.db.collection("User").document(user_id).get()
        if not exist_user.exists:
            raise IndexError("Não existe usuário com esse id")

        workouts = self.collection.where("User_id", "==", user_id).stream()
        response = []
        for data in workouts:
            response.append(data.to_dict())

        if len(response) == 0:
            raise ValueError("O usuário não possui treinos cadastrados")

        return response

    def get_workouts_by_date(self, day: str, user_id: str):
        exist_user = self.db.collection("User").document(user_id).get()
        if not exist_user.exists:
            raise IndexError("Não existe usuário com esse id")

        workout = self.collection.where("User_id", "==", user_id).where("Weekday", "==", day).limit(1).get()

        if len(workout) == 0:
            return None
        
        response = workout[0].to_dict()

        return response

    def delete_workout(self, workout_id: str, user_id: str):
        ## Checar se o id existe no banco
        exist_workout = self.collection.document(workout_id).get()
        if not exist_workout.exists:
            raise IndexError("Não existe treino com esse id")

        ## Checagem do id do usuário para não permitir a remoção de treinos que não sejam dele
        workout_data = exist_workout.to_dict()
        if workout_data.get("User_id") != user_id:
            raise PermissionError("Usuário não coincide com o id permitido")

        self.collection.document(workout_id).delete()
        return True

    def update_workout(self, workout_id: str, new_workout: WorkoutModel, user_id: str):
        ## Checar se o id existe no banco
        exist_workout = self.collection.document(workout_id).get()
        if not exist_workout.exists:
            raise IndexError("Não existe treino com esse id")

        ## Checagem do id do usuário para não permitir a alteração de treinos que não sejam dele
        workout_data = exist_workout.to_dict()
        if workout_data.get("User_id") != user_id:
            raise PermissionError("Usuário não coincide com o id permitido")

        ## Validar as novas entradas
        # weekday
        used_weekday = self.collection.where("Weekday", "==", new_workout.Weekday).where("User_id", "==", new_workout.User_id).limit(1).get()
        if len(used_weekday) != 0 and used_weekday[0].id != workout_id:
            raise ValueError("Já existe um treino cadastrado nesse dia")
        
        # nome
        used_name = self.collection.where("Name", "==", new_workout.Name).where("User_id", "==", new_workout.User_id).limit(1).get()
        if len(used_name) != 0 and used_name[0].id != workout_id:
            raise ValueError("Já existe um treino cadastrado com esse nome")

        ## Tudo está validado
        # Atualização de exercícios novos e antigos
        exercise_names = [ex.name for ex in new_workout.Order]
        existing_names = {}
        if exercise_names:      ## Protege a query do parametro IN
            existing_docs = self.db.collection("Exercise").where("User_id", "==", new_workout.User_id).where("Name", "in", exercise_names).stream()
            existing_names = {doc.to_dict().get("Name"): doc.id for doc in existing_docs}       # Permite a busca em O(1)
        exs_list = []
        seen_exercises = set()

        for exercise in new_workout.Order:
            if exercise.name in seen_exercises:     # Valida a duplicidade de exercícios no mesmo treino
                raise ValueError(f"O exercício {exercise.Name} já está neste treino.")
            seen_exercises.add(exercise.Name)

            if exercise.name in existing_names:
                exercise.id = existing_names[exercise.Name]     # coloca o id do exercicio "antigo" no "novo" exercicio
            else:
                self.exercise_controller.create_exercise(exercise)

            exs_list.append(exercise)
        new_workout.Order = exs_list

        ## Se chegou aqui, está tudo validado e pode ser alterado no banco
        data = new_workout.to_dict()
        self.collection.document(workout_id).update(data)

        return new_workout