from flask import Blueprint, jsonify
from flask import request
from jobsdb.base import main_func

jobsdb_blueprint = Blueprint('jobsdb', __name__)


@jobsdb_blueprint.route('/get_jd')
def jobsdb_api():
    """
        This is the summary defined in yaml file
        First line is the summary
        All following lines until the hyphens is added to descriptions
        the format of the first lines until 3 hyphens will be not yaml compliant
        but everything below the 3 hyphens should be.
        ---
        tags:
         - jobsdb
        description: gets one page of jobsdb jd source
        parameters:
         - name: page
           in: query
           type: integer
           required: true
        responses:
         200:
          description: A list of jd sources
         404:
          description: Error page not found

    """
    page = request.args.get('page')
    return jsonify(main_func(page_no=page))
