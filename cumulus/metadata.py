'''
  Utilities to faciliate logging from Cumulus projects
'''

import os
import datetime
import xml.sax.saxutils


METADATA_TEMPLATE = '''
<Granule>
   <GranuleUR>{granule_ur}</GranuleUR>
   <InsertTime>{insert_time}</InsertTime>
   <LastUpdate>{last_update}</LastUpdate>
   <Collection>
     <ShortName>{short_name}</ShortName>
     <VersionId>1</VersionId>
   </Collection>
   <OnlineAccessURLs>
        <OnlineAccessURL>
            <URL>https://72a8qx4iva.execute-api.us-east-1.amazonaws.com/dev/getGranule?granuleKey={data_name}/{granule_ur}</URL>
        </OnlineAccessURL>
    </OnlineAccessURLs>
   <Orderable>true</Orderable>
</Granule>
'''


def write_metadata(filename, dataid, dataname='', outdir='./'):
    """ Write metadata for data file filename of type data_name """
    # output metadata
    bname = os.path.basename(filename)
    fout = os.path.join(outdir, bname + '.meta.xml')
    info = {
        'data_name': dataname,
        'granule_ur': bname,
        'insert_time': datetime.datetime.utcnow().isoformat(),
        'last_update': datetime.datetime.utcnow().isoformat(),
        'short_name': dataid
    }
    # Ensure that no XML-invalid characters are included
    info = {k: xml.sax.saxutils.escape(v) for k, v in info.items()}
    with open(fout, 'w') as _f:
        _f.write(METADATA_TEMPLATE.format(**info))
    return fout
