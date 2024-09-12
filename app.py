from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from supabase import create_client, Client
import bcrypt
from datetime import datetime
import os

# Configuración del cliente de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qrodavmgttwjtnpvzxrt.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFyb2Rhdm1ndHR3anRucHZ6eHJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYxMjE3ODgsImV4cCI6MjA0MTY5Nzc4OH0.4jGeaXbKGmCwA3LcgURy_W5OQgjrcg74vKrm6Jf0jzU")
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user_data = supabase_client.table('usuarios').select('*').eq('id', user_id).execute()
    if user_data.data:
        user_info = user_data.data[0]
        return User(id=user_info['id'], username=user_info['usuario'], password=user_info['contrasena'], role=user_info['rol'])
    return None

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Obtener el usuario desde la base de datos
        user_data = supabase_client.table('usuarios').select('*').eq('usuario', username).execute()
        if user_data.data:
            user_info = user_data.data[0]
            # Verificar la contraseña
            if bcrypt.checkpw(password.encode('utf-8'), user_info['contrasena'].encode('utf-8')):
                user = User(id=user_info['id'], username=user_info['usuario'], password=user_info['contrasena'], role=user_info['rol'])
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Credenciales incorrectas', 'danger')
        else:
            flash('Usuario no encontrado', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/usuarios')
@login_required
def usuarios():
    if current_user.role != 'admin':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('home'))
    # Obtener usuarios de la base de datos
    usuarios = supabase_client.table('usuarios').select('*').execute().data
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/camiones', methods=['GET', 'POST'])
@login_required
def camiones():
    if request.method == 'POST':
        camion_id = request.form.get('id')
        numero_ficha = request.form.get('numero_ficha')
        marca = request.form.get('marca')
        placa = request.form.get('placa')

        if not numero_ficha:
            flash('El campo número de ficha es obligatorio', 'danger')
            return redirect(url_for('camiones'))

        if camion_id:
            # Actualizar el camión existente
            supabase_client.table('camiones').update({
                'numero_ficha': numero_ficha,
                'marca': marca,
                'placa': placa
            }).eq('id', camion_id).execute()
            flash('Camión actualizado exitosamente', 'success')
        else:
            # Insertar un nuevo camión
            supabase_client.table('camiones').insert({
                'numero_ficha': numero_ficha,
                'marca': marca,
                'placa': placa
            }).execute()
            flash('Camión agregado exitosamente', 'success')

        return redirect(url_for('camiones'))

    # Obtener solo las columnas necesarias
    camiones = supabase_client.table('camiones').select('id, numero_ficha, marca, placa').execute().data
    return render_template('camiones.html', camiones=camiones)

@app.route('/editar_camion/<string:numero_ficha>', methods=['GET', 'POST'])
@login_required
def editar_camion(numero_ficha):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('home'))

    camion = supabase_client.table('camiones').select('*').eq('numero_ficha', numero_ficha).execute().data
    if not camion:
        flash('Camión no encontrado', 'danger')
        return redirect(url_for('camiones'))

    camion = camion[0]  # Extrae el primer resultado

    if request.method == 'POST':
        nuevo_numero_ficha = request.form['numero_ficha']
        marca = request.form['marca']
        placa = request.form['placa']

        supabase_client.table('camiones').update({
            'numero_ficha': nuevo_numero_ficha,
            'marca': marca,
            'placa': placa
        }).eq('numero_ficha', numero_ficha).execute()

        flash('Camión actualizado exitosamente', 'success')
        return redirect(url_for('camiones'))

    return render_template('editar_camion.html', camion=camion)

@app.route('/eliminar_camion/<int:id>', methods=['POST'])
@login_required
def eliminar_camion(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('home'))

    supabase_client.table('camiones').delete().eq('id', id).execute()
    flash('Camión eliminado exitosamente', 'success')
    return redirect(url_for('camiones'))

@app.route('/registro_combustible', methods=['GET', 'POST'])
@login_required
def registro_combustible():
    if request.method == 'POST':
        camion_id = request.form['camion_id']
        km_inicial = request.form['kilometraje_inicial']
        km_final = request.form['kilometraje_final']
        
        # Calcular la cantidad de galones
        galones = (float(km_final) - float(km_inicial)) / 10  # Ejemplo de cálculo
        
        # Guardar en la base de datos
        data = {
            'placa': camion_id,
            'km_inicio': km_inicial,
            'km_final': km_final,
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'galones': galones
        }
        supabase_client.table('despachos').insert(data).execute()

        flash('Registro de combustible guardado exitosamente')
        return redirect(url_for('registro_combustible'))

    # Obtener todos los despachos y camiones para mostrar en la tabla
    despachos = supabase_client.table('despachos').select('*').execute().data
    camiones = supabase_client.table('camiones').select('*').execute().data
    placas = [camion['placa'] for camion in camiones]

    return render_template('registro_combustible.html', despachos=despachos, placas=placas)

@app.route('/editar_despacho/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_despacho(id):
    if request.method == 'POST':
        camion_id = request.form['camion_id']
        km_inicial = request.form['kilometraje_inicial']
        km_final = request.form['kilometraje_final']
        galones = (float(km_final) - float(km_inicial)) / 10  # Ejemplo de cálculo
        
        data = {
            'placa': camion_id,
            'km_inicio': km_inicial,
            'km_final': km_final,
            'galones': galones
        }
        supabase_client.table('despachos').update(data).eq('id', id).execute()
        flash('Despacho actualizado exitosamente')
        return redirect(url_for('registro_combustible'))

    despacho = supabase_client.table('despachos').select('*').eq('id', id).execute().data
    if not despacho:
        flash('Despacho no encontrado', 'danger')
        return redirect(url_for('registro_combustible'))

    despacho = despacho[0]  # Extrae el primer resultado
    camiones = supabase_client.table('camiones').select('*').execute().data
    placas = [camion['placa'] for camion in camiones]

    return render_template('editar_despacho.html', despacho=despacho, placas=placas)

@app.route('/eliminar_despacho/<int:id>', methods=['POST'])
@login_required
def eliminar_despacho(id):
    if current_user.role != 'admin':
        flash('Acceso denegado', 'danger')
        return redirect(url_for('home'))

    supabase_client.table('despachos').delete().eq('id', id).execute()
    flash('Despacho eliminado exitosamente', 'success')
    return redirect(url_for('registro_combustible'))


if __name__ == '__main__':
    app.run(debug=True)
