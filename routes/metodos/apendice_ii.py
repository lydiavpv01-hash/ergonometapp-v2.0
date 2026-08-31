from flask import Blueprint, jsonify

bp_apendice_ii = Blueprint('apendice_ii', __name__, url_prefix='/apendice-ii')

@bp_apendice_ii.route('/nueva', methods=['GET', 'POST'])
def nueva():
    return jsonify({'método': 'Apéndice II', 'estado': 'en desarrollo'})
