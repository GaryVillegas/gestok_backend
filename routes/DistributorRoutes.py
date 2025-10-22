from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.DistributorService import DistributorService

distributor_bp = Blueprint('distributor_routes', __name__)

@distributor_bp.route('/creatre', methods=['POST'])
@jwt_required()
def create_distributor():
    #TODO: finish route
    """"""