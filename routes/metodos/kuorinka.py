from flask import Blueprint, jsonify

bp_kuorinka = Blueprint('kuorinka', __name__, url_prefix='/cuestionario-nordico')

@bp_kuorinka.route('/nueva', methods=['GET', 'POST'])
def nueva():
    return jsonify({'método': 'Kuorinka', 'estado': 'en desarrollo'})
