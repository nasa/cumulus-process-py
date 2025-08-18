import os
import gzip
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from cumulus_process.s3 import download, upload


def upload_files(files, bucket, prefix):
    """uploads list of local files to a given bucket and prefix

    Arguments:
        files: list of file paths
        bucket: name of the bucket to upload the data to
        prefix: the prefix key the appears before the filename

    Returns:
        returns a list of s3 uris e.g. s3://example-bucket/my/prefix/filename.txt
    """
    list_of_uris = []
    for f in files:
        s3_uri = os.path.join('s3://', bucket, prefix, os.path.basename(f))
        list_of_uris.append(upload(f, s3_uri))
    return list_of_uris


def dict_to_xml(meta, pretty=False, root='Granule'):
    """ Convert dictionary metadata to XML string """
    # for lists, use the singular version of the parent XML name
    singular_key_func = lambda x: x[:-1]
    # convert to XML
    if root is None:
        xml = str(dicttoxml(meta, root=False, attr_type=False, item_func=singular_key_func))
    else:
        xml = str(dicttoxml(meta, custom_root=root, attr_type=False, item_func=singular_key_func))
    # The <Point> XML tag does not follow the same rule as singular
    # of parent since the parent in CMR is <Boundary>. Create metadata
    # with the <Points> parent, and this removes that tag
    xml = xml.replace('<Points>', '').replace('</Points>', '')
    # pretty print
    if pretty:
        dom = parseString(xml)
        xml = dom.toprettyxml()
    return xml


def write_metadata(meta, fout, pretty=False):
    """ Write metadata dictionary as XML file """
    xml = dict_to_xml(meta, pretty=pretty)
    with open(fout, 'w') as f:
        f.write(xml)


def gunzip(fname, remove=False):
    """ Unzip a file, creating new file """
    f = os.path.splitext(fname)[0]
    with gzip.open(fname, 'rb') as fin:
        with open(f, 'wb') as fout:
            fout.write(fin.read())
    if remove:
        os.remove(fname)
    return f


def basename(filename):
    """ Strip path and extension """
    return os.path.splitext(os.path.basename(filename))[0]
