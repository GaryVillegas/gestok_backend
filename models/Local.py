class Local:

    def __init__(self, id, name, address, user_id):
        self.id = id
        self.name = name
        self.address = address
        self.user_id = user_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address
        }