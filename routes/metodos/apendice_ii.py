from flask import Blueprint, render_template

bp_apendice_ii = Blueprint('apendice_ii', __name__, url_prefix='/apendice-ii')

@bp_apendice_ii.route('/nueva', methods=['GET'])
def nueva():
    html = render_template('apendice_ii_workspace.html')
    refinements = render_template('apendice_ii_refinements_v1.html')
    return html.replace('</body>', refinements + '</body>')
