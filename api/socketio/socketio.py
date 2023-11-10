from flask_socketio import SocketIO, send, emit

socketio = SocketIO()

@socketio.on('connect', namespace='/chat')
def connect():
    print("Connected")


@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('Client disconnected')

@socketio.on('message event',namespace='/chat')
def message(message):
    print(message)
    emit('message event', {'data': 'hallodsalfkjaslkjfdsa'})

@socketio.on('message',namespace='/chat')
def message(message):
    emit('message event',{'data':'hallo'})
