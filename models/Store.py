class Store:

    def __init__(self, id, description, address, user_id):
        self.id = id
        self.description = description
        self.address = address
        self.user_id = user_id

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'address': self.address,
            'user_id': self.user_id
        }