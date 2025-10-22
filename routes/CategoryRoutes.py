from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.CategoryService import CategoryServie

category_bp = Blueprint('category_routes', __name__)

@category_bp.route('/create', methods=['POST'])
@jwt_required()
def create_category():
    """
    Ruta para crear categorias
    """
    try:
        category = {
            'description': request.json.get('description', None)
        }
        current_user_id = int(get_jwt_identity())

        if not current_user_id or not category['description']:
            return jsonify({'error': 'Los datos son requeridos.'}), 400
        
        category_id, message = CategoryServie.create_category(category, current_user_id)
        if category_id:
            return jsonify({'message': message, 'category_id': category_id}), 200
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        print(f"Error en creacion: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500

@category_bp.route('/categories', methods=['GET'])
@jwt_required()
def categories():
    """
    Ruta para traer categorias de usuario
    """
    try:
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            return jsonify({'error': 'usuario no encontrado'}), 400
        
        categories, message = CategoryServie.get_categories(current_user_id)
        if categories:
            categories_dict = [category.to_dict() for category in categories]
            return jsonify({
                'message': message,
                'categories': categories_dict
            }), 200

        return jsonify({'message': message}), 404
    except Exception as ex:
        print(f"Error al obtener categorías: {str(ex)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    
@category_bp.route('/delete/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id: int):
    """
    Ruta para poder elimiar categoria
    """
    try:
        if not category_id:
            return jsonify({'error': 'categoria no encontrada'}), 404
        
        row_affected, message = CategoryServie.delete_category(category_id)
        if row_affected is not None and row_affected > 0:
            return jsonify({'message': message, 'row_affected': row_affected}), 200
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        print(f"Error al eliminar categoria. Type {str(type)}: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500