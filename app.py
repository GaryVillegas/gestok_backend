from flask import Flask, request, jsonify #Aquí importamos la clase de Flask. Esta case es usada para crear la app.
# Importamos los Blueprints de las nuevas rutas
from routes.TestRoutes import test_bp

app = Flask(__name__) #aquí creamos la instancia the FLask app.

app.register_blueprint(test_bp)

@app.get("/api")
#lo de aqui arriba es un decorardor de flask en el cual definimos la ruta de GET
def api_test():
    #aquí retornamos lo que se vé al llamar a /api en postman
    return "This api works :)"

# Este bloque asegura que la aplicación Flask solo se ejecute si este archivo es el programa principal
if __name__ == '__name__':
    app.run(debug=True)  # Inicia el servidor Flask en modo debug para desarrollo