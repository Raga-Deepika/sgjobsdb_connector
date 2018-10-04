from jobsdb.base import main_func
from rq import Queue
from redis import Redis
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.test
col = db.jobs_dbdata

redis_conn = Redis()
q = Queue('jobsdb',connection=redis_conn)


def jobsdb_jobs():
    page = ''
    while page < str(50):
        resp = main_func(page_no=page)
        if 'data' in resp:
            for d in resp["data"]:
                col.update({"details_url": d["details_url"]},
                           d,
                           upsert=True)
        else:
            pass
        page = page+str(1)


def jobsdb_queue():
    job = q.enqueue(jobsdb_jobs)
    print(job)