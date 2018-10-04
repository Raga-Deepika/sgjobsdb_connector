from bs4 import BeautifulSoup
import os,sys,re
from datetime import datetime
from dateparser import parse
import requests
import random
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.WARNING)
logger.setLevel(logging.ERROR)


logging.basicConfig(filename="jobsdb.logs",level=logging.DEBUG, format='%(asctime)s:%(name)s:%(message)s')

desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']

proxies = {
    'http': 'http://35.173.16.12:8888/?noconnect',
    'https':'http://35.173.16.12:8888/?noconnect'
}


def proxied_request(url, extra_headers={}, params={}):
    headers = {
        'User-Agent':random.choice(desktop_agents),
        # 'Accept': ('text/html,application/xhtml+xml,application/xml;'
        #            'q=0.9,*/*;q=0.8'),
        # 'Accept-Language': 'en-US,en;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    headers.update(extra_headers)

    # if url.startswith('http://'):
    #     p = proxies('http')
    # else:
    #     p = proxies('https')
    resp = requests.get(url, headers=headers, proxies=proxies, params=params)
    return resp

def details_func(detail_url):
    try:
        try:
            req = proxied_request(detail_url)
            logger.info('successful request to details page {0} of jobsdb connector'.format(detail_url))
        except Exception as e:
            details_data = None
            logger.warning('request to  details page {0} of jobsdb connector failed: {1}'.format(detail_url, str(e)))
            return details_data
        if req.status_code==200:
            soup = BeautifulSoup(req.content,'lxml')
            try:
                details_data= soup.find('div',class_='job_info').text.strip().replace('\xa0','').replace('\n','')
            except AttributeError:
                details_data = None
            return details_data
    except Exception as e:
        logger.error('Error in scraping the details page of jobsdb connector : {0}'.format(str(e)))
        return None


def jobstreet(detail_url):
    try:
        jobstreet_data ={}
        try:
            req = proxied_request(detail_url)
            logger.info('successful request to jobstreet details page of {0} jobsdb connector'.format(detail_url))
        except Exception as e:
            jobstreet_data = None
            logger.warning('request to  jobstreet details page of {0} jobsdb connector failed: {1}'.format(detail_url, str(e)))
            return jobstreet_data
        if req.status_code==200:
            soup = BeautifulSoup(req.content,'lxml')
            try:
                jobstreet_data['job_desc'] = soup.find('div',id='job_description').text.strip().replace('\xa0',"").replace('\n','').replace('\r','')
            except AttributeError :
                jobstreet_data['job_desc'] = None
            try:
                loc = soup.find('div',class_='map-col-wraper').text.strip()
                pattern = re.compile(r"\s+")
                jobstreet_data['details_location'] = pattern.sub(' ',loc).strip()
            except AttributeError:
                jobstreet_data['details_location'] = None
            try:
                firm_snapshot = soup.find_all('div',class_='col-lg-12 col-md-12 col-sm-12')[1].text.strip()
                jobstreet_data['firm_snapshot'] = " ".join(firm_snapshot.split())
            except IndexError:
                jobstreet_data['firm_snapshot'] = None
            try:
                jobstreet_data['company_overview'] = soup.find('div',id='company_overview_all').text.strip().replace('\xa0',"").replace('\n','').replace('\r','').replace('\t','')
            except AttributeError:
                jobstreet_data['company_overview'] = None
            try:
                jobstreet_data['why_join_us_all'] = soup.find('div',id='why_join_us_all').text.strip().replace('\r','').replace('\n','').replace('\t','')
            except AttributeError:
                jobstreet_data['why_join_us_all'] = None
            try:
                date_posted = soup.find(['p','span'],id='posting_date').text.strip().replace("Advertised: ",'')
                jobstreet_data['posted_date'] = parse(date_posted)
            except AttributeError:
                jobstreet_data['posted_date'] = None
        return jobstreet_data
    except Exception as e:
        logger.error('Error in scraping the jobstreet details page of jobsdb connector : {0}'.format(str(e)))
        return None


def main_func(location,page_no=1):
    try:
        source_url = 'https://sg.jobsdb.com/j?q=&l={0}&p={1}'.format(location,str(page_no))
        base_url = 'https://sg.jobsdb.com'
        jobsdb_dict = {}
        jobsdb_dict['success'] = True
        try:
            req = proxied_request(source_url)
            logger.info('successful request to jobsdb connector {0}'.format(source_url))
        except Exception as e:
            jobsdb_dict['success'] = False
            jobsdb_dict['errorMessage'] = str(e)
            logger.warning('request to jobsdb connector {0} failed: {1}'.format(source_url, str(e)))
            return jobsdb_dict
        if req.status_code==200:
            data = []
            soup = BeautifulSoup(req.content, 'lxml')
            try:
                no_of_jobs = soup.find('div',class_='column page-entries-info').find_all('span')[2].text.strip().replace(',','')
            except:
                no_of_jobs = None
            if int(no_of_jobs) >= 500:
                page_no = 50
            else:
                page_no = int(no_of_jobs) // int(10)
                mod = int(no_of_jobs) % int(10)
                if mod == 0 :
                    page_no = page_no
                else:
                    page_no = page_no+int(1)
            jobsdb_dict['page_no'] = page_no
            print(jobsdb_dict['page_no'])
            try:
                cards = soup.find_all(['div','li'],class_=['result sponsored trackable sponsored_top','result'])
            except Exception as e:
                print(str(e))
                jobsdb_dict["data"] = None
                return jobsdb_dict
            for item in cards:
                obj = {}
                try:
                    obj['title'] = item.div.div.h2.find('a').text.strip().replace('|','')
                except AttributeError:
                    obj['title'] = None
                try:
                    details_url = item.div.div.a.get('href')
                    obj['details_url'] = '{0}{1}'.format(base_url, details_url)
                except AttributeError:
                    obj['details_url'] = None
                try:
                    obj['company_name'] = item.div.div.find('span',class_='company').text.strip()
                except AttributeError:
                    obj['company_name'] = None
                try:
                    obj['location'] = item.div.div.find('span',class_='location').text.strip()
                except AttributeError:
                    obj['location'] = None
                try:
                    obj['summary'] = item.div.div.find('div',class_='summary').text.strip().replace('|','')
                except AttributeError:
                    obj['summary'] = None
                try:
                    check_ad = item.div.div.div.find('span',class_='cite').text.strip()
                except AttributeError:
                    check_ad = None
                try:
                    date = item.div.div.div.find('span',class_='date').text.strip()
                    date = date.replace('about', '').replace('ago','')
                    date = parse(date)
                except AttributeError:
                    date = None
                if check_ad == 'AdJobstreet SG':
                    obj['details'] = jobstreet(detail_url=obj['details_url'])
                    obj['date'] = obj['details']['posted_date']
                    del obj['details']['posted_date']
                else:
                    obj['details'] = details_func(detail_url=obj['details_url'])
                    obj['date'] = date
                data.append(obj)
            jobsdb_dict['data'] = data
            jobsdb_dict['created_at'] = datetime.now()
            jobsdb_dict["updated_at"] = datetime.now()
            return jobsdb_dict
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        logger.error('Error in scraping page {0} of the jobsdb  connector : {1}'.format(page_no,str(e)))
        return None

print(main_func(location='Mandai'))