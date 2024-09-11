from flask import Blueprint
from utils.entity import r
from utils.sql import supabase

cron_users:Blueprint = Blueprint('chat', __name__ ,url_prefix='/cron_users')
@cron_users.route('/', methods=['GET'])
def index():
    response = sql = supabase.table('users').select('*').execute()
    return r(code=200,data=response.data)