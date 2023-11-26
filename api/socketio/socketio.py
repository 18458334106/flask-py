from flask import Blueprint,request
from utils.entity import r
from flask_socketio import SocketIO, send, emit
from utils.sql import supabase

socket_bp = Blueprint('socket', __name__ ,url_prefix='/chat')

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
    supabase.table('chat_recode').insert(message).execute()

@socket_bp.route('/recode',methods=['POST'])
def queryRecode():
    obj = request.get_json(silent=True)
    print(type(obj['userId']),obj['toUserId'])
    result1 = (supabase.table('chat_recode')
              .select('*').eq('userId',obj['toUserId'])
              .eq('toUserId',obj['userId']).execute().data)
    result2 = (supabase.table('chat_recode')
              .select('*').eq('userId',obj['userId'])
              .eq('toUserId',obj['toUserId']).execute().data)
    res = result1 + result2
    res.sort(key=lambda x:x['created_at'],reverse=False)
    return r(code=200,msg='操作成功',data=res)