"""
Servicio de autenticación.
- Todas las consultas a la DB se realizan mediante Stored Procedures (SP).
- Cada SP se separa y documenta con un comentario.
- Se usa database.db_mysql.get_connection() para obtener la conexión.
- Se intenta devolver una instancia del modelo Users si el modelo provee un constructor compatible,
  si no, se devuelve el diccionario directo.
"""
from database.db_mysql import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Intento de usar tu modelo Users si existe.
try:
    from models.Users import Users
except Exception:
    Users = None  # si no encaja el modelo, retornamos dicts

class AuthService:
    # -----------------------------
    # SP: Obtener usuario por email
    # SP name assumed: sp_get_user_by_email
    # Devuelve columnas: id, email, password_hash, (opcional) otros campos
    # -----------------------------
    @staticmethod
    def find_user_by_email_sp(email: str):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # CALL al SP que busca usuario por email
                cur.execute('call sp_get_user_by_email(%s)', (email,))
                row = cur.fetchone()
                # Si existe un modelo Users aprovechamos su constructor o from_dict
                if row and Users:
                    try:
                        # Intentamos construir la instancia del modelo (si soporta dict unpack)
                        return Users(**row)
                    except Exception:
                        # Si no es posible, devolvemos el dict
                        return row
                return row
        finally:
            if conn:
                conn.close()

    # -----------------------------
    # SP: Crear usuario (registro)
    # SP name assumed: sp_create_user
    # Parámetros: p_email, p_password_hash
    # Debe devolver id (SELECT LAST_INSERT_ID() AS id) o un indicador de error
    # -----------------------------
    @staticmethod
    def create_user_sp(email: str, plain_password: str):
        password_hash = generate_password_hash(plain_password)
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # CALL al SP para crear usuario
                cur.execute('call sp_create_user(%s, %s)', (email, password_hash))
                # Intentamos leer el resultado que el SP puede retornar (p. ej. SELECT LAST_INSERT_ID() AS id)
                row = cur.fetchone()
                conn.commit()
                if row :
                    return row[0]
                # si no hay fila devuelta, intentar obtener lastrowid
                return cur.lastrowid or None
        finally:
            if conn:
                conn.close()

    # -----------------------------
    # SP: Guardar refresh token
    # SP name assumed: sp_save_refresh_token
    # Parámetros: p_user_id, p_jti, p_token, p_expires, p_last_activity
    # -----------------------------
    @staticmethod
    def save_refresh_token_sp(user_id: int, token_jti: str, token_str: str, expires_at: datetime, last_activity: datetime):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                # CALL al SP que inserta el refresh token en la tabla correspondiente
                cur.execute('call sp_save_refresh_token(%s, %s, %s, %s, %s)', (
                    user_id,
                    token_jti,
                    token_str,
                    expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                    last_activity.strftime('%Y-%m-%d %H:%M:%S')
                ))
                conn.commit()
                return True
        finally:
            if conn:
                conn.close()

    # -----------------------------
    # SP: Obtener refresh token por jti
    # SP name assumed: sp_get_refresh_token_by_jti
    # Debe devolver: user_id, token_str, expires_at, last_activity, revoked, email (opcional)
    # -----------------------------
    @staticmethod
    def get_refresh_token_by_jti_sp(token_jti: str):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute('call sp_get_refresh_token_by_jti(%s)', (token_jti,))
                row = cur.fetchone()
                return row
        finally:
            if conn:
                conn.close()

    # -----------------------------
    # SP: Actualizar last_activity del refresh token
    # SP name assumed: sp_update_refresh_token_activity
    # Parámetros: p_jti, p_last_activity
    # -----------------------------
    @staticmethod
    def update_refresh_token_activity_sp(token_jti: str, last_activity: datetime):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute('call sp_update_refresh_token_activity(%s, %s)', (token_jti, last_activity.strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                return True
        finally:
            if conn:
                conn.close()

    # -----------------------------
    # SP: Revocar refresh token (marcar revoked = 1)
    # SP name assumed: sp_revoke_refresh_token
    # Parámetros: p_jti
    # -----------------------------
    @staticmethod
    def revoke_refresh_token_sp(token_jti: str):
        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute('call sp_revoke_refresh_token(%s)', (token_jti,))
                conn.commit()
                return True
        finally:
            if conn:
                conn.close()

    # -----------------------------
    # Util: verificar contraseña (hash almacenado con werkzeug)
    # -----------------------------
    @staticmethod
    def verify_password(plain_password: str, stored_hash: str) -> bool:
        if not stored_hash:
            return False
        return check_password_hash(stored_hash, plain_password)