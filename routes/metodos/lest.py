from flask import Blueprint, jsonify

bp_lest = Blueprint('lest', __name__, url_prefix='/lest')

@bp_lest.route('/nueva', methods=['GET', 'POST'])
def nueva():
    return jsonify({'método': 'LEST', 'estado': 'en desarrollo'})
