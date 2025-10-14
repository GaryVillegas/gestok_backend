class User():

    def __init__(self, id, name, lastname, rut, authid):
        # Constructor que inicializa los atributos del User
        self.id = id
        self.name = name
        self.lastname = lastname
        self.rut = rut
        self.authid = authid
    
    def to_dict(self):
        #Método que convierte la insancia del test en un diccionario
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'rut': self.rut,
            'authid': self.authid
        }