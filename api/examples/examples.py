from utils.sql import supabase
from flask import Blueprint
from utils.entity import r
examples_bp = Blueprint('examples', __name__, url_prefix='/examples')

@examples_bp.route('/getList')
def getList():
    res = supabase.table('examples').select("*").execute()
    return r(code=200,data=res.get('data',[]))
