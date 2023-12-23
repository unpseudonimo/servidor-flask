from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['MONGO_URI'] = 'mongodb://localhost:27017/PedidosExpres'
mongo = PyMongo(app)    
bcrypt = Bcrypt(app)
@app.route('/')
def hello():
        # Verificar la conexión a MongoDB
    if mongo.db.client is not None and mongo.db.client.server_info() is not None:
        return '¡Conexión exitosa a MongoDB!'
    else:
        return 'No se pudo establecer la conexión a MongoDB.'
    
@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        data = request.get_json()
        print("Datos recibidos:", data)

        nombre = data.get('username')
        password = data.get('password')
        email = data.get('email')
        rol = data.get('rol')

        if not nombre or not password or not email:
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'})

        # Hasheamos la contraseña antes de almacenarla en la base de datos
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_exists = mongo.db.usuarios.find_one({'nombre': nombre})
        if user_exists:
            return jsonify({'success': False, 'message': 'El usuario ya existe'})

        new_user = {'nombre': nombre, 'password': hashed_password, 'email': email, 'rol':rol}
        mongo.db.usuarios.insert_one(new_user)

        return jsonify({'success': True, 'message': 'Registro exitoso'})

    except Exception as e:
        print("Error en la solicitud:", str(e))
        return jsonify({'success': False, 'message': 'Error en la solicitud'})
    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Obtener los datos enviados desde la aplicación Android
    username = data.get('username')
    password = data.get('password')

    # Validar campos
    if not username or not password:
        return jsonify({'success': False, 'message': 'Faltan campos requeridos'})

    # Obtener el usuario de la base de datos
    user = mongo.db.usuarios.find_one({'nombre': username})

    # Verificar si el usuario existe
    if user:
        # Verificar la contraseña usando bcrypt
        if bcrypt.check_password_hash(user['password'], password):
            # Login exitoso
            return jsonify({'success': True, 'message': 'Login exitoso', 'user_id': str(user['_id']),'rol':str(user['rol'])})
        else:
            # Contraseña incorrecta
            return jsonify({'success': False, 'message': 'Contraseña incorrecta'})
    else:
        # El usuario no existe
        return jsonify({'success': False, 'message': 'Usuario no encontrado'})

    
if __name__ == '__main__':
    app.run(host='0.0.0.0',use_reloader=True, debug=True)