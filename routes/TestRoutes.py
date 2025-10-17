from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.Test import Test #importamos modelo test
from services.TestService import TestService #imrpotamos el servicio test

#Crear un Blueprint para las rutas de test
test_bp = Blueprint('test_routes', __name__, url_prefix='/api/test')

# Ruta pública - no requiere autenticación
@test_bp.route('/public', methods=['GET'])
def public_tests():
    tests = TestService.testSelect()
    if tests is not None:
        return jsonify({
            'message': 'Datos públicos de test',
            'tests': [test.to_dict() for test in tests]
        })
    else:
        return jsonify({'error': 'Error al obtener tests'}), 500

#Creamos la ruta para crear test
@test_bp.route('/', methods=['POST'])
@jwt_required() # ¡Esta ruta ahora requiere autenticación!
def test_post():
    current_user=get_jwt_identity()
    text = request.json['text']  # Obtiene el campo 'text' del cuerpo JSON de la petición

    _test = Test(0, text, None)  # Crea una instancia de Test con valores iniciales
    created_test = TestService.testInsert(_test)  # Inserta el test en la base de datos usando el servicio

    if(created_test != None):  # Si se creó correctamente el test
        return jsonify({'user_id': current_user,'mensaje': 'Test creado!', 'test': created_test.to_dict()})  # Retorna mensaje y el test creado en formato JSON
    else:
        return jsonify({'mensaje': 'Error al crear Test.'}), 401  # Si hubo error, retorna mensaje de error y código 401
    
# Nota: También puedes agregar la ruta que tenías en app.py aquí:
@test_bp.route('/', methods=['GET'])
@jwt_required() # ¡Esta ruta ahora requiere autenticación!
def api_test():
    current_user_id = get_jwt_identity()
    tests = TestService.testSelect()
    if(tests != None):
        return jsonify({'user_id': current_user_id, 'tets': [test.to_dict() for test in tests]}) #Retorna los tests creados
    else:
        return jsonify({'mensaje': 'Error al crear Test.'}), 401  # Si hubo error, retorna mensaje de error y código 401