from jobsdb.base import main_func
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.test
col = db.jobs_dba


def jobsdb_jobs():
    for page in range(1,2):
        resp = main_func(page_no=page)
        for d in resp["data"]:
            col.update({"title": d["title"]},
                       d,
                       upsert=True)