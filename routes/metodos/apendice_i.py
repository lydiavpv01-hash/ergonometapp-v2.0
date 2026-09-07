from flask import Blueprint, render_template

bp_apendice_i = Blueprint('apendice_i', __name__, url_prefix='/apendice-i')

@bp_apendice_i.route('/nueva', methods=['GET'])
def nueva():
    return render_template('apendice_i_workspace.html')
