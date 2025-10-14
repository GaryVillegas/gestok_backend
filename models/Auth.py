class Auth(): #Define la clase Auth que representa un modelo Authentication

    def __inti__(self, id, email, password):
        #Constructor que inicializa los atributos de Authetication
        self.id = id
        self.email = email
        self.password = password

    def to_dict(self):
        #Método que convierte la instancia del test en un diccionario
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password
        }