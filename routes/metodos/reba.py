from flask import Blueprint, jsonify

bp_reba = Blueprint('reba', __name__, url_prefix='/reba')

@bp_reba.route('/nueva', methods=['GET', 'POST'])
def nueva():
    return jsonify({'método': 'REBA', 'estado': 'en desarrollo'})
