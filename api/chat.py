from flask import Blueprint,request
from utils.entity import r
from flask_socketio import SocketIO, send, emit
from utils.sql import supabase

chat_bp:Blueprint = Blueprint('chat', __name__ ,url_prefix='/chat')

socketio = SocketIO()

@socketio.on('connect', namespace='/chat')
def connect():
    print("Connected")

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    print('Client disconnected')

@socketio.on('message', namespace='/chat')
def message(message):
    emit('message update', message,broadcast=True,namespace='/chat')
    supabase.table('chatRecodes').insert(message).execute()

@chat_bp.route('/recodes',methods=['POST'])
def recodes():
    return r(200,'暂未开放',[])