from flask import Flask
from flasgger import Swagger
from jobsdb.controllers import jobsdb_blueprint
from apscheduler.schedulers.background import BackgroundScheduler
from jobsdb.jobs import jobsdb_queue


app = Flask(__name__)
swagger = Swagger(app)
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(jobsdb_queue,'interval',minutes=5,max_instances=3)
scheduler.start()


app.register_blueprint(jobsdb_blueprint, url_prefix='/api/v1/jobsdb')

if __name__ == '__main__':
    app.run(debug=True)