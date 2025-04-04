from flask import Flask, request
from flask_socketio import SocketIO, send, emit, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

#guardando los clientes
clients = {}

@app.route('/')
def hello():
    return 'welcome!'

@socketio.on('connect')
def handle_connect():
    print('✅ Un cliente se ha conectado.')

@socketio.on('disconnect')
def handle_disconnect():
    username = clients.get(request.sid, 'Desconocido')
    print(f'❌ {username} se desconectó.')
    clients.pop(request.sid, None)

@socketio.on('register')
def handle_register(username):
    clients[request.sid] = username
    print(f'👤 Cliente registrado como: {username}')
    send(f'{username} se ha unido al chat.', broadcast=True)

@socketio.on('message')
def handle_message(msg):
    username = clients.get(request.sid, 'Anonimo')
    print(f'📨 Mensaje de {username}: {msg}')
    send(f'{username}: {msg}', broadcast=True)

@socketio.on('message')
def handleMessage(msg):
    print('Message: '+msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)