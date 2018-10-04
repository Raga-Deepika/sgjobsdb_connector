from flask import Blueprint, jsonify
from flask import request
from jobsch.base import jobs_ch_jds
from jobsch import jobs_ch_urls


jobsch_blueprint = Blueprint('jobsch', __name__)


@jobsch_blueprint.route('/get_jd')
def jobsch_controller():
    """
        This is the summary defined in yaml file
        First line is the summary
        All following lines until the hyphens is added to descriptions
        the format of the first lines until 3 hyphens will be not yaml compliant
        but everything below the 3 hyphens should be.
        ---
        tags:
         - jobsch
        description: gets one page of jobsch jd source
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
    for i in jobs_ch_urls:
        job_url = i['link']
        return jsonify(jobs_ch_jds(job_url = job_url, page=page))
