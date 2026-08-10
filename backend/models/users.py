## Entidade User
class UserModel():
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def to_dict(self):
        ## Transforma o objeto UserModel em um dicionário para o Firestore salvar no banco
        return {
            "id": self.id,
            "name": self.name
        }

    def from_dict(src_dict: dict):
        ## Transforma um dicionário do Firestore em um objeto UserModel
        return UserModel(
            id=src_dict.get("id"),
            name=src_dict.get("name")
        )
    