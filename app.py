from flask import Flask, request, jsonify #Aquí importamos la clase de Flask. Esta case es usada para crear la app.
import os
from datetime import timedelta
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
# Importamos los Blueprints de las nuevas rutas
from routes.TestRoutes import test_bp
from routes.AuthRoutes import auth_bp
from routes.AccountRoutes import account_bp
from routes.StoreRoutes import store_bp
from routes.CategoryRoutes import category_bp

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
bcrypt = Bcrypt(app)

app.register_blueprint(test_bp)
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth") # prefijo /auth para rutas de login
app.register_blueprint(account_bp, url_prefix='/api/v1/account')
app.register_blueprint(store_bp, url_prefix='/api/v1/store')
app.register_blueprint(category_bp, url_prefix='/api/v1/category')

# Callback para verificar tokens en blacklist (opcional)
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    # Aquí podrías verificar si el token está en una blacklist
    # Por ahora retornamos False (no está revocado)
    return False

# Callback personalizado para errores de JWT
@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({
        'error': 'Token de acceso requerido'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'error': 'Token inválido'
    }), 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'error': 'Token expirado'
    }), 401

@app.get("/api")
#lo de aqui arriba es un decorardor de flask en el cual definimos la ruta de GET
def api_test():
    #aquí retornamos lo que se vé al llamar a /api en postman
    return "This api works :)"

# Ruta de información (pública)
@app.get("/api/info")
def api_info():
    return jsonify({
        "name": "Flask API con JWT",
        "version": "1.0",
        "protected_routes": [
            "/api/test/",
            "/auth/protected",
            "/auth/me",
            "/auth/logout",
            "/auth/refresh"
        ]
    })

# Este bloque asegura que la aplicación Flask solo se ejecute si este archivo es el programa principal
if __name__ == '__name__':
    app.run(debug=True)  # Inicia el servidor Flask en modo debug para desarrollo