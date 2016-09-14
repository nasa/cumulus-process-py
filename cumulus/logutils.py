import os
import logging
import datetime
from splunk_handler import SplunkHandler


def get_logger():
    """ Return a logger """
    log = logging.getLogger()
    # if splunk envvars all set then use splunk!
    if set(['SPLUNK_HOST', 'SPLUNK_USERNAME', 'SPLUNK_PASSWORD']).issubset(set(os.environ.keys())):
        splunk = SplunkHandler(
            host=os.environ['SPLUNK_HOST'],
            port=os.environ.get('SPLUNK_PORT', '8089'),
            username=os.environ['SPLUNK_USERNAME'],
            password=os.environ['SPLUNK_PASSWORD'],
            index=os.environ.get('SPLUNK_INDEX', 'main'),
            verify=False
        )
        log = log.addHandler(splunk)
        # by default, only levels above INFO will write to Splunk
        # DEBUG is useful in that it will _not_ be sent to Splunk
    log.setLevel(logging.INFO)
    return log


def make_log_string(data_pipeline_id=os.environ.get('PIPELINE_ID'), dataset_id=os.environ.get('DATASET_ID'), is_error=0, **kwargs):
    '''
    Make a key=value log string that Splunk can easily ingest
    `kwargs` should include `granule_id`, `process`, and `message`, amongst others
    Will return something like:
    'timestamp="2016-09-07T17:33:53.910244" data_pipeline_id="foo" bar="baz"'
    '''
    kwargs['timestamp'] = datetime.datetime.now().isoformat()
    kwargs['data_pipeline_id'] = data_pipeline_id
    kwargs['dataset_id'] = dataset_id
    kwargs['is_error'] = is_error
    log_message = ' '.join(['{k}="{v}"'.format(k=k, v=v) for k, v in kwargs.items()])
    return log_message
