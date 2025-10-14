from flask import Flask, request, jsonify #Aquí importamos la clase de Flask. Esta case es usada para crear la app.
app = Flask(__name__) #aquí creamos la instancia the FLask app.
from models.Test import Test #importamos modelo test
from services.TestService import TestService #imrpotamos el servicio test

@app.get("/api")
#lo de aqui arriba es un decorardor de flask en el cual definimos la ruta de GET
def api_test():
    #aquí retornamos lo que se vé al llamar a /api en postman
    return "This api works :)"

#Creamos la ruta para crear test
@app.post('/api/test')
def test_post():
    text = request.json['text']  # Obtiene el campo 'text' del cuerpo JSON de la petición

    _test = Test(0, text, None)  # Crea una instancia de Test con valores iniciales
    created_test = TestService.testInsert(_test)  # Inserta el test en la base de datos usando el servicio

    if(created_test != None):  # Si se creó correctamente el test
        return jsonify({'mensaje': 'Test creado!', 'test': created_test.to_dict()})  # Retorna mensaje y el test creado en formato JSON
    else:
        return jsonify({'mensaje': 'Error al crear Test.'}), 401  # Si hubo error, retorna mensaje de error y código 401

# Este bloque asegura que la aplicación Flask solo se ejecute si este archivo es el programa principal
if __name__ == '__name__':
    app.run(debug=True)  # Inicia el servidor Flask en modo debug para desarrollo