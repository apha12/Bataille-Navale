
class Game:
    def __init__(self, id=None):
        self.id = id

    def get_id(self):
        return self._id

    def get_players(self):
        return self.players 