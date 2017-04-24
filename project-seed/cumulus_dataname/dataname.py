
import os
import logging
import datetime
from cumulus.granule import Granule
from collections import OrderedDict as od


class DATANAME(Granule):
    """ A MODIS Granule """

    inputs = ['inputfie']

    @classmethod
    def process(cls, input, path='./', logger=logging.getLogger(__name__), publish=None):
        """ Process granule input file(s) into output file(s) """
        """
            The Granule class automatically fetches input files and uploads output files, while
            validating both, before and after this process() function. Therefore, the process function
            can retrieve the files from self.input_files[key] where key is the name given to that input
            file (e.g., "hdf-data", "hdf-thumbnail").
            The Granule class takes care of logging, validating, writing out metadata, and reporting on timing
        """
        output = {}

        bname = os.path.basename(input['inputfile'])

        fout = bname + '.out'

        # create output file and validate

        output['outputfile'] = fout

        # Create metadata file
        fout = os.path.join(path, bname + '.meta.xml')
        output['metafile'] = fout

        meta = od([
            ('GranuleUR', bname),
            ('InsertTime', datetime.datetime.utcnow().isoformat()),
            ('LastUpdate', datetime.datetime.utcnow().isoformat()),
            ('Collection', od([
                ('ShortName', 'DATASHORTNAME'),
                ('VersionId', 'VERSION')
            ]))
        ])

        cls.write_metadata(meta, fout)

        return output
