class Category:

    def __init__(self, id, description, user_id):
        self.id = id
        self.description = description
        self.user_id = user_id

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'user_id': self.user_id
        }