
import os
import re
import datetime
import logging
import json
import xml.sax.saxutils
import cumulus.s3 as s3


class Granule(object):
    """ Class representing a data granule and processing """

    s3_uri = 's3://cumulus-1st-test-private/staging'

    def __init__(self, payload, path=''):
        """ Initialize granule with a payload containing a recipe """
        if isinstance(payload, str):
            if payload[0:5] == 's3://':
                # s3 location
                payload = s3.download_json(payload)
            else:
                if not os.path.exists(payload):
                    raise ValueError("Payload file %s does not exist" % payload)
                with open(payload, 'r') as f:
                    payload = json.loads(f.read())
        self.payload = payload
        self._check_payload()
        self.path = path

    @property
    def id(self):
        """ Granule ID """
        return self.payload['granuleRecord']['granuleId']

    def process(self):
        """ Process a granule locally """
        # this function should operate on input files and generate output files
        pass

    def metadata(self, save=False):
        """ Retrieve metada for granule """
        info = {
            'data_name': self.payload['granuleRecord']['collectionName'],
            'granule_ur': self.payload['granuleRecord']['granuleId'],
            'insert_time': datetime.datetime.utcnow().isoformat(),
            'last_update': datetime.datetime.utcnow().isoformat(),
            'short_name': self.payload['granuleRecord']['collectionName']
        }
        # Ensure that no XML-invalid characters are included
        info = {k: xml.sax.saxutils.escape(v) for k, v in info.items()}
        md = METADATA_TEMPLATE.format(**info)
        if save:
            fout = os.path.join(self.path, info['data_name'] + '.meta.xml')
            with open(fout, 'w') as f:
                f.write(md)
            return fout
        else:
            return md

    def _check_payload(self):
        """ Test validity of payload """
        try:
            assert('granuleRecord' in self.payload)
            assert('recipe' in self.payload['granuleRecord'])
            assert('files' in self.payload['granuleRecord'])
            assert('processStep' in self.payload['granuleRecord']['recipe'])
            assert('config' in self.payload['granuleRecord']['recipe']['processStep'])
        except:
            raise ValueError("Invalid payload")

    @property
    def recipe(self):
        """ Get recipe dictionary """
        return self.payload['granuleRecord']['recipe']

    @property
    def input_files(self):
        """ Input files of granule """
        _files = self.recipe['processStep']['config']['inputFiles']
        return {f: self.payload['granuleRecord']['files'][f] for f in _files}

    @property
    def output_files(self):
        """ Output files for granule """
        _files = self.recipe['processStep']['config']['outputFiles']
        return {f: self.payload['granuleRecord']['files'][f] for f in _files}

    def download(self):
        """ Download input files from S3 """
        self.local_input = []
        for f in self.input_files:
            file = self.input_files[f]
            if file.get('stagingFile', None):
                fname = s3.download(file['stagingFile'], path=self.path)
            elif file.get('archivedFile', None):
                fname = s3.download(file['archivedFile'], path=self.path)
            else:
                raise ValueError('Input files not provided')
            self.local_input.append(fname)
        return self.local_input

    def upload(self, base_uri):
        """ Upload output files to S3 """
        # get list of output files to upload
        files = os.listdir(self.path)
        to_upload = {}
        for f in self.output_files:
            file = self.output_files[f]
            for fname in files:
                if re.match(file['regex'], fname):
                    # if a match, add it and continue loop
                    to_upload[f] = os.path.join(self.path, fname)
                    continue
        # attempt uploading of files
        successful_uploads = []
        for f in to_upload:
            fname = to_upload[f]
            try:
                uri = s3.upload(fname, base_uri)
                self.payload['granuleRecord']['files'][f]['stagingFile'] = uri
                successful_uploads.append(uri)
            except Exception as e:
                logging.error("Error uploading file %s: %s" % (os.path.basename(fname), str(e)))
        # not all files were created
        if len(to_upload) < len(self.output_files):
            raise RuntimeError("Not all output files were created")
        # not all files were uploaded
        if len(successful_uploads) < len(self.output_files):
            raise IOError("Error uploading output files")

        return successful_uploads

    def next(self, dispatcher):
        """ Send payload to dispatcher lambda """
        # update payload
        self.payload['previousStep'] = self.payload['nextStep']
        self.payload['nextStep'] = self.payload['nextStep'] + 1
        # invoke dispatcher lambda
        s3.invoke_lambda(self.payload)


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
