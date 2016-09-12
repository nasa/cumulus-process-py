'''
Utilities for processing cumulus data sources
'''

import os
import cumulus.logging as logging


def check_output(filename):
    """ Check for output file existence """
    if not os.path.exists(filename):
        bname = os.path.basename(filename)
        logging.error(
            logging.make_log_string(
                granule_id=bname, process='processing', is_error=1, message='Unable to process %s' % filename
            )
        )
        raise Exception('Error converting file')
