from dataclasses import dataclass


@dataclass
class UserModel():
    id: str
    name: str
    username: str
    password_hash: str

    def to_dict(self):
        return {
            "id": self.id,
            "Name": self.name,
            "Username": self.username,
            "Password_hash": self.password_hash
        }

    def from_dict(src_dict: dict):
        return UserModel(
            id=src_dict.get("id", ""),
            name=src_dict.get("Name", ""),
            username=src_dict.get("Username", ""),
            password_hash=src_dict.get("Password_hash", "")
        )
    