from flask import Blueprint, render_template

bp_kuorinka = Blueprint('kuorinka', __name__, url_prefix='/cuestionario-nordico')

@bp_kuorinka.route('/nueva', methods=['GET'])
def nueva():
    return render_template('kuorinka_workspace.html')
