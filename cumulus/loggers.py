import os
import json
import requests
import logging
import datetime
from splunk_handler import SplunkHandler
from dotenv import load_dotenv, find_dotenv
from pythonjsonlogger import jsonlogger

# environment variables
load_dotenv(find_dotenv())


class CumulusFormatter(jsonlogger.JsonFormatter):
    """ Formatting for Cumulus logs """

    def __init__(self, collectionName='', *args, **kwargs):
        super(CumulusFormatter, self).__init__(*args, **kwargs)
        self.collectionName = collectionName

    def format(self, record):
        if isinstance(record.msg, str):
            record.msg = {'message': record.msg}
        if 'message' not in record.msg.keys():
            record.msg['message'] = ''
        record.msg['timestamp'] = datetime.datetime.now().isoformat()
        record.msg['collectionName'] = self.collectionName
        res = super(CumulusFormatter, self).format(record)
        return res


def getLogger(collectionName, splunk=None, stdout=None):
    """ Return logger suitable for Cumulus """
    logger = logging.getLogger(collectionName)
    # clear existing handlers
    logger.handlers = []
    if (stdout is None) and (splunk is None):
        logger.addHandler(logging.NullHandler())
    if stdout is not None:
        handler = logging.StreamHandler()
        #formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        #formatter = logging.Formatter(jsonlogger.JsonFormatter(json_encoder=json.JSONEncoder()))
        handler.setFormatter(CumulusFormatter(collectionName=collectionName))
        #handler.setFormatter(formatter)
        handler.setLevel(stdout['level'])
        logger.addHandler(handler)
    if splunk is not None:
        if set(['host', 'user', 'pass']).issubset(set(splunk.keys())):
            handler = SplunkHandler(
                host=splunk['host'],
                port=splunk.get('port', '8089'),
                username=splunk['user'],
                password=splunk['pass'],
                index=splunk.get('index', 'main'),
                verify=False
            )
            handler.setFormatter(CumulusFormatter(collectionName=collectionName))
            handler.setLevel(splunk['level'])
            logger.addHandler(handler)
        else:
            raise RuntimeError('Splunk logging requires host, user, and pass fields')
    # logging level
    logger.setLevel(logging.INFO)
    return logger


def get_splunk_logs(config, **kwargs):
    """ Get splunk results matching a query """
    url = 'https://{host}:{port}/servicesNS/admin/search/search/jobs/export'.format(
        host=config['host'], port=config['port'])
    search = 'search index="{}"'.format(config['index'])
    for k in kwargs:
        search += ' {}="{}"'.format(k, kwargs[k])
    response = requests.post(url, auth=(config['user'], config['pass']),
                             params={'output_mode': 'json'}, data={'search': search}, verify=False)
    results = []
    for r in response.content.split('\n'):
        if r != '':
            js = json.loads(r)
            if 'result' in js:
                results.append(js['result'])
    return results
