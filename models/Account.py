class Account:

    def __init__(self, id, name, lastname, rut, user_id):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.rut = rut
        self.user_id = user_id
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'rut': self.rut,
            'user_id': self.user_id
        }