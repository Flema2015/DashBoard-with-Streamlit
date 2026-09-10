import sqlite3
import bcrypt

DB_PATH = "mesa_ayuda.db"


def crear_usuario(username, password, nombre_completo):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios_sistema (username, password_hash, nombre_completo) VALUES (?, ?, ?)",
        (username, password_hash, nombre_completo),
    )
    conn.commit()
    conn.close()
    print(f"Usuario '{username}' creado.")


def cambiar_password(username, password_nueva):
    password_hash = bcrypt.hashpw(password_nueva.encode(), bcrypt.gensalt()).decode()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios_sistema SET password_hash = ? WHERE username = ?",
        (password_hash, username),
    )
    conn.commit()
    filas_afectadas = cursor.rowcount
    conn.close()

    if filas_afectadas == 0:
        print(f"No existe el usuario '{username}'.")
    else:
        print(f"Contraseña de '{username}' actualizada.")


# ------------------------------------------------------
# Editá estas líneas según lo que quieras hacer, y corré el script
# ------------------------------------------------------
if __name__ == "__main__":
    # Ejemplo: cambiar la contraseña de admin
    crear_usuario("Mirko", "Mirko123", "Mirko Kovacevich")
    # cambiar_password("admin", "miNuevaClave123")
