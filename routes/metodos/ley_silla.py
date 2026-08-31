from flask import Blueprint, jsonify

bp_ley_silla = Blueprint('ley_silla', __name__, url_prefix='/ley-silla')

@bp_ley_silla.route('/nueva', methods=['GET', 'POST'])
def nueva():
    return jsonify({'método': 'Ley SILLA', 'estado': 'en desarrollo'})
