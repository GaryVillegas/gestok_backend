"""
Rutas de autenticación:
- /auth/register  -> crear usuario (SP)
- /auth/login     -> login por email (SP), guarda refresh token (SP)
- /auth/refresh   -> refrescar access token usando refresh token (valida SP, inactividad, renovación)
- /auth/logout    -> revocar refresh token (SP)
- /auth/protected -> ejemplo protegido con access token
Comentarios en español explicando cada paso.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    decode_token
)
from datetime import datetime, timedelta
import os

from services.AuthService import AuthService

auth_bp = Blueprint('auth', __name__)

# Tiempo máximo de inactividad en segundos antes de cerrar la sesión (env opcional)
INACTIVITY_TIMEOUT = int(os.getenv('INACTIVITY_TIMEOUT_SECONDS', 1800))
# Umbral para renovar refresh token si está por expirar (p. ej. 7 días)
REFRESH_RENEW_THRESHOLD = timedelta(days=7)

@auth_bp.post("/register")
def register():
    """
    1) Recibe JSON { email, password }
    2) Llama al SP que crea usuario y devuelve id.
    3) Devuelve 201 con user_id o 400 si falla.
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "email y password son requeridos"}), 400

    # Llamada al AuthService que ejecuta el SP correspondiente.
    new_id = AuthService.create_user_sp(email, password)
    if not new_id:
        return jsonify({"msg": "no se pudo crear el usuario (email puede existir)"}), 400

    return jsonify({"msg": "usuario creado", "user_id": new_id}), 201


@auth_bp.post("/login")
def login():
    """
    Flujo:
    1) Recibe { email, password }.
    2) Busca usuario por email mediante SP.
    3) Verifica password.
    4) Genera access_token y refresh_token.
    5) Extrae jti/exp del refresh token y lo guarda en BD vía SP.
    6) Devuelve ambos tokens al cliente.
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "email y password son requeridos"}), 400

    # Buscar usuario por email (SP)
    user_row = AuthService.find_user_by_email_sp(email)
    if not user_row:
        return jsonify({"msg": "email o password incorrectos"}), 401

    # Si el servicio devolvió un modelo Users, intentar extraer atributos.
    if hasattr(user_row, '__dict__'):
        # compatible con instancia de modelo
        user_id = getattr(user_row, 'id', None)
        user_email = getattr(user_row, 'email', None)
        pwd_hash = getattr(user_row, 'password_hash', None) or getattr(user_row, 'password', None)
    else:
        # diccionario
        user_id = user_row.get('id')
        user_email = user_row.get('email')
        pwd_hash = user_row.get('password_hash') or user_row.get('password')

    if not AuthService.verify_password(password, pwd_hash):
        return jsonify({"msg": "email o password incorrectos"}), 401

    # Generar tokens
    access_token = create_access_token(identity=user_id, additional_claims={"email": user_email})
    refresh_token = create_refresh_token(identity=user_id)

    # Decodificar refresh para obtener jti y exp (sin validar firma, local)
    decoded = decode_token(refresh_token)
    refresh_jti = decoded.get("jti")
    expires_timestamp = datetime.utcfromtimestamp(decoded.get("exp"))

    now = datetime.utcnow()
    # Guardar refresh token en BD (SP)
    saved = AuthService.save_refresh_token_sp(
        user_id=user_id,
        token_jti=refresh_jti,
        token_str=refresh_token,
        expires_at=expires_timestamp,
        last_activity=now
    )
    if not saved:
        return jsonify({"msg": "error al guardar refresh token en BD"}), 500

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {"id": user_id, "email": user_email}
    }), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """
    Flujo:
    1) Valida refresh token (decorador).
    2) Obtiene jti e identidad.
    3) Verifica que el refresh token exista y no esté revocado (SP).
    4) Comprueba inactividad -> si excede, revoca y fuerza logout.
    5) Actualiza last_activity (SP).
    6) Genera nuevo access token.
    7) Si el refresh token está cercano a expirar, genera uno nuevo y lo guarda (SP) y revoca el viejo.
    """
    jwt_data = get_jwt()
    jti = jwt_data.get("jti")
    identity = get_jwt_identity()

    # Obtener fila del refresh token desde la BD (SP)
    token_row = AuthService.get_refresh_token_by_jti_sp(jti)
    if not token_row:
        return jsonify({"msg": "refresh token inválido o revocado"}), 401

    if token_row.get("revoked"):
        return jsonify({"msg": "refresh token revocado"}), 401

    now = datetime.utcnow()
    last_activity = token_row.get("last_activity") or token_row.get("created_at") or now
    # Si DB devuelve string, intentar parsear ISO
    if isinstance(last_activity, str):
        try:
            last_activity = datetime.fromisoformat(last_activity)
        except Exception:
            try:
                last_activity = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')
            except Exception:
                last_activity = now

    inactivity_seconds = (now - last_activity).total_seconds()
    if inactivity_seconds > INACTIVITY_TIMEOUT:
        # Revocar refresh token por inactividad (SP)
        AuthService.revoke_refresh_token_sp(jti)
        return jsonify({"msg": "sesión cerrada por inactividad"}), 401

    # Actualizar last_activity en BD (SP)
    AuthService.update_refresh_token_activity_sp(jti, now)

    # Crear nuevo access token
    user_email = token_row.get("email") or ""
    new_access = create_access_token(identity=identity, additional_claims={"email": user_email})

    response = {"access_token": new_access}

    # Decidir si renovar refresh token: si expira dentro del umbral lo reemplazamos
    expires_at = token_row.get("expires_at")
    need_renew = False
    if expires_at:
        if isinstance(expires_at, str):
            try:
                expires_at = datetime.fromisoformat(expires_at)
            except Exception:
                try:
                    expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
                except Exception:
                    expires_at = None
        if isinstance(expires_at, datetime):
            if (expires_at - now) <= REFRESH_RENEW_THRESHOLD:
                need_renew = True

    if need_renew:
        # Generar nuevo refresh token y guardarlo (SP). Revocar el antiguo.
        new_refresh = create_refresh_token(identity=identity)
        decoded = decode_token(new_refresh)
        new_jti = decoded.get("jti")
        new_expires = datetime.utcfromtimestamp(decoded.get("exp"))

        # Revocar antiguo (SP)
        AuthService.revoke_refresh_token_sp(jti)
        # Guardar nuevo (SP)
        AuthService.save_refresh_token_sp(identity, new_jti, new_refresh, new_expires, now)
        response["refresh_token"] = new_refresh

    return jsonify(response), 200


@auth_bp.post("/logout")
@jwt_required(refresh=True)
def logout():
    """
    Revoca (marca) el refresh token actual en la BD (SP).
    """
    jwt_data = get_jwt()
    jti = jwt_data.get("jti")
    AuthService.revoke_refresh_token_sp(jti)
    return jsonify({"msg": "sesión cerrada"}), 200


@auth_bp.get("/protected")
@jwt_required()
def protected():
    """
    Ejemplo de ruta protegida con access token.
    """
    identity = get_jwt_identity()
    return jsonify({"msg": "acceso autorizado", "user_id": identity}), 200