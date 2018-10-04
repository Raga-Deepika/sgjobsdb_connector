from bs4 import BeautifulSoup as bs
import os,sys,re, linecache
import requests
import random
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.WARNING)
logger.setLevel(logging.ERROR)


logging.basicConfig(filename="jobsch.logs",level=logging.DEBUG, format='%(asctime)s:%(name)s:%(message)s')

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

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))



def jobs_ch_jds(job_url,page=1):
    try:
        jobDict = {}
        jobDict['success'] = True
        jobDict['data'] = []
        job_url_ = '{0}&page={1}='.format(job_url,str(page))
        try:
            req = proxied_request(job_url)
            logger.info('succesful req to {0}'.format(job_url_))
        except Exception as e:
            logger.warning('request to {0} failed : {1}'.format(job_url_,str(e)))
        soup = bs(req.content,'lxml')
        try:
            cards = soup.find_all('div',class_='serp-item')
        except Exception as e:
            PrintException()
            cards = []
            print(str(e))
        #print(cards)
        for card in cards:
            temp = {}
            try:
                temp['job_title'] = card.find('h2',class_='e-heading serp-item-head-1').text.strip()
            except AttributeError:
                PrintException()
                temp['job_title'] = None
            try:
                temp['detail_url'] = 'https://www.jobs.ch{0}'.format(card.find('h2',class_='e-heading serp-item-head-1').a.get('href'))
            except AttributeError:
                PrintException()
                temp['detail_url'] = None
            try:
                temp['company_name'] = card.find('h3',class_='e-heading serp-item-head-2').a.get('title')
            except AttributeError:
                PrintException()
                temp['company_name'] = None
            print(temp['company_name'])
            try:
                unwanted = card.find('a')
                unwanted.extract()
                temp['location'] = card.find('h3',class_='e-heading serp-item-head-2').text.strip().replace('—','').replace(temp['company_name'],'').strip()
            except AttributeError:
                PrintException()
                temp['location'] = None
            try:
                temp['job_snippet'] = card.find('p', class_='hidden-xs serp-item-head-3').text.strip()
            except AttributeError:
                PrintException()
                temp['job_snippet'] = None
            try:
                temp['date_posted'] = card.find('div', class_='badge-pool').find_all('span')[0].text.strip()
            except AttributeError:
                PrintException()
                temp['date_posted'] = None
            try:
                temp['position'] = [c.text.strip() for c in card.find('div', class_='badge-pool').find_all('span') if 'position' in c.text.strip().lower()]
            except Exception as e:
                logger.error('Error in {0}'.format(e))
                PrintException()
                temp['position'] = None
            try:
                req_ = requests.get(temp['detail_url'])
                logger.info('succesful details request for {0}'.format(temp['detail_url']))
            except Exception as e:
                PrintException()
                logger.warning('request for detail for {0} : {1}'.format(temp['detail_url'],str(e)))

            soup_ = bs(req_.content,'lxml')
            try:
                temp['job_description'] = soup_.find('div',class_='container vacancy-detail-content').text.strip()
            except AttributeError:
                temp['job_description'] = None
            jobDict['data'].append(temp)
        return jobDict
    except Exception as e:
        logger.error('Error in scraping jobs_ch for {0} : {1}'.format(job_url_,str(e)))
        return None


print(jobs_ch_jds(job_url='https://www.jobs.ch/en/vacancies/?region=14&term=', page=1))