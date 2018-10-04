from jobsch.base import jobs_ch_jds
from jobsch import jobs_ch_urls
from rq import Queue
from redis import Redis
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.test
col = db.jobs_ch_data

redis_conn = Redis()
q = Queue('jobsch',connection=redis_conn)


def jobsch_jobs():
    page = ''
    while page < 100:
        for i in jobs_ch_urls:
            url = i['link]']
            resp = jobs_ch_jds(job_url=url,page=str(page))
            if 'data' in resp:
                for d in resp["data"]:
                    col.update({"detail_url": d["detail_url"]},
                               d,
                               upsert=True)
            else:
                pass
            page = page+str(1)


def jobsch_queue():
    job = q.enqueue(jobsch_jobs)
    print(job)