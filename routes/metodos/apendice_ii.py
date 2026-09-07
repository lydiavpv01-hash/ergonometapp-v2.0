from flask import Blueprint, render_template

bp_apendice_ii = Blueprint('apendice_ii', __name__, url_prefix='/apendice-ii')

@bp_apendice_ii.route('/nueva', methods=['GET'])
def nueva():
    return render_template('apendice_ii_workspace.html')
