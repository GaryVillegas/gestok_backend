from flask import Flask, request, jsonify #Aquí importamos la clase de Flask. Esta case es usada para crear la app.
import os
from datetime import timedelta
from flask_jwt_extended import JWTManager
# Importamos los Blueprints de las nuevas rutas
from routes.TestRoutes import test_bp
from routes.AuthRoutes import auth_bp

if os.environ.get('VERCEL') is None:
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__) #aquí creamos la instancia the FLask app.
#Configuracion JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
#Configuracion JWT: tiempos de expiracion
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
#Inicializa el manejador JWT
jwt = JWTManager(app)

app.register_blueprint(test_bp)
app.register_blueprint(auth_bp, url_prefix="/auth") # prefijo /auth para rutas de login

@app.get("/api")
#lo de aqui arriba es un decorardor de flask en el cual definimos la ruta de GET
def api_test():
    #aquí retornamos lo que se vé al llamar a /api en postman
    return "This api works :)"

# Este bloque asegura que la aplicación Flask solo se ejecute si este archivo es el programa principal
if __name__ == '__name__':
    app.run(debug=True)  # Inicia el servidor Flask en modo debug para desarrollo