from flask import Flask, request, jsonify
from flask_socketio import SocketIO, send
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Almacenamiento temporal de usuarios (nombre: contraseña encriptada)
users = {}
clients = {}

@app.route('/', methods=['GET'])
def hello():
    return 'hello'


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Nombre y contraseña requeridos"}), 400

    if username in users:
        return jsonify({"error": "Usuario ya registrado"}), 409

    users[username] = generate_password_hash(password)
    return jsonify({"message": "Usuario registrado exitosamente"}), 201

# Chat WebSocket
@socketio.on('connect')
def on_connect():
    print("🔌 Cliente conectado")

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    user = clients.pop(sid, 'Desconocido')
    print(f'❌ {user} se desconectó')

@socketio.on('login')
def on_login(data):
    username = data.get('username')
    password = data.get('password')

    if username not in users or not check_password_hash(users[username], password):
        send("❌ Login fallido. Usuario o contraseña incorrectos.", to=request.sid)
        return

    clients[request.sid] = username
    send(f"✅ {username} ha ingresado al chat.", broadcast=True)

@socketio.on('message')
def on_message(msg):
    username = clients.get(request.sid, "Anon")
    print(f"💬 {username}: {msg}")
    send(f"{username}: {msg}", broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)