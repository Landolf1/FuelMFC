import bcrypt
import supabase

# Configuración del cliente de Supabase
url = "https://qrodavmgttwjtnpvzxrt.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFyb2Rhdm1ndHR3anRucHZ6eHJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYxMjE3ODgsImV4cCI6MjA0MTY5Nzc4OH0.4jGeaXbKGmCwA3LcgURy_W5OQgjrcg74vKrm6Jf0jzU"
supabase_client = supabase.create_client(url, key)

def create_user(username, password, role):
    # Generar un hash para la contraseña
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insertar el nuevo usuario en la base de datos
    data = {
        'usuario': username,
        'contrasena': hashed_password,
        'rol': role
    }
    
    try:
        response = supabase_client.table('usuarios').insert(data).execute()
        print(f"Usuario '{username}' creado exitosamente.")
        print(response)
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("Bienvenido al gestor de usuarios.")
    
    # Solicitar opción al usuario
    print("Elija el tipo de usuario:")
    print("1.Usuario normal")
    print("2.Usuario con rol")
    choice = input("Ingrese el número de la opción deseada (1 o 2): ")
    
    if choice == '1':
        role = 'usuario'  # Asignar rol por defecto a usuarios normales
    elif choice == '2':
        role = input("Ingrese el rol del usuario (por ejemplo, 'admin' o 'usuario'): ")
    else:
        print("Opción no válida. Saliendo.")
        return
    
    # Solicitar datos del usuario
    username = input("Ingrese el nombre de usuario: ")
    password = input("Ingrese la contraseña: ")
    
    # Crear el usuario
    create_user(username, password, role)

if __name__ == "__main__":
    main()
