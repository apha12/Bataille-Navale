from Model.battlefield import Battlefield

class Player:
    def __init__(self, name: str, battle_field: Battlefield):
        self.name = name
        self.battlefield = Battlefield

    def get_name(self):
        return self.name

    def get_battlefield(self):
        return self.battlefield