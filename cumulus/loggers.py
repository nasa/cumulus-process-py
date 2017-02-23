
import os
import json
import requests
import logging
import datetime
from splunk_handler import SplunkHandler
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger

# load envvars
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)


class CumulusFormatter(jsonlogger.JsonFormatter):
    """ Formatting for Cumulus logs """

    def __init__(self, collectionName='', granuleId='', *args, **kwargs):
        super(CumulusFormatter, self).__init__(*args, **kwargs)
        self.collectionName = collectionName
        self.granuleId = granuleId

    def format(self, record):
        if isinstance(record.msg, str) or isinstance(record.msg, unicode):
            record.msg = {'message': record.msg}
        if 'message' not in record.msg.keys():
            record.msg['message'] = ''
        record.msg['timestamp'] = datetime.datetime.now().isoformat()
        record.msg['collectionName'] = self.collectionName
        record.msg['granuleId'] = self.granuleId
        record.msg['level'] = record.levelname
        res = super(CumulusFormatter, self).format(record)
        return res


def add_formatter(logger, collectionName='', granuleId=''):
    """ Add CumulusFormatter to logger """
    for handler in logger.handlers:
        handler.setFormatter(CumulusFormatter(collectionName=collectionName, granuleId=granuleId))
    return logger


def getLogger(name, splunk=None, stdout=None):
    """ Return logger suitable for Cumulus """
    logger = logging.getLogger(name)
    # clear existing handlers
    logger.handlers = []
    if (stdout is None) and (splunk is None):
        logger.addHandler(logging.NullHandler())
    if stdout is not None:
        handler = logging.StreamHandler()
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
            handler.setLevel(splunk['level'])
            logger.addHandler(handler)
        else:
            raise RuntimeError('Splunk logging requires host, user, and pass fields')
    # logging level
    logger.setLevel(1)
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
