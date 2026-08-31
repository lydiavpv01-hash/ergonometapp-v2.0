from flask import Blueprint, jsonify

bp_apendice_i = Blueprint('apendice_i', __name__, url_prefix='/apendice-i')

@bp_apendice_i.route('/nueva', methods=['GET', 'POST'])
def nueva():
    return jsonify({'método': 'Apéndice I', 'estado': 'en desarrollo'})
