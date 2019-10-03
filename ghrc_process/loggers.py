
import logging
import datetime
from pythonjsonlogger import jsonlogger


class CumulusFormatter(jsonlogger.JsonFormatter):
    """ Formatting for Cumulus logs """

    def format(self, record):
        # if just a string, convert to JSON
        if isinstance(record.msg, str):
            record.msg = {'message': record.msg}
        # create blank msg if not present
        if 'message' not in record.msg.keys():
            record.msg['message'] = ''
        record.msg['timestamp'] = datetime.datetime.now().isoformat()
        if hasattr(record, 'collectionName'):
            record.msg['collectionName'] = record.collectionName
        if hasattr(record, 'granuleId'):
            record.msg['granuleId'] = record.granuleId
        record.msg['level'] = record.levelname
        res = super(CumulusFormatter, self).format(record)
        return res


def getLogger(name, stdout=None):
    """ Return logger suitable for Cumulus """
    logger = logging.getLogger(name)
    # clear existing handlers
    logger.handlers = []
    if (stdout is None):
        logger.addHandler(logging.NullHandler())
    if stdout is not None:
        handler = logging.StreamHandler()
        handler.setLevel(stdout['level'])
        handler.setFormatter(CumulusFormatter())
        logger.addHandler(handler)
    # logging level
    logger.setLevel(1)
    return logger
