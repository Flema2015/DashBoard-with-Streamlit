"""
Script de administración de usuarios para Mesa de Ayuda IT.
Permite crear nuevos usuarios con rol y cambiar contraseñas.
"""
from database import crear_usuario, cambiar_password, listar_usuarios, inicializar_db


def main():
    inicializar_db()
    print("=== Usuarios Registrados en el Sistema ===")
    usuarios = listar_usuarios()
    for u in usuarios:
        print(f"ID: {u['id']} | Usuario: {u['username']} | Rol: {u['rol']}")

    # Ejemplos de uso:
    # crear_usuario("nuevo_tecnico", "claveSegura123", rol="tecnico")
    # crear_usuario("nuevo_admin", "adminSeguro123", rol="administrador")
    # cambiar_password("admin", "nuevaClave123")


if __name__ == "__main__":
    main()
