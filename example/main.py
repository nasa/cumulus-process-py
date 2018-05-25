import os
from cumulus_process import Process, helpers


class Modis(Process):
    """
        A subclass of Process for processing fake modis products 
        This is an example and does not intended for processing MODIS Products
    """

    @property
    def input_keys(self):
        """ This property is helps the processing step to distinguish incoming
            files from one another
        """
        return {
            'hdf': r"^M.{6}.A[\d]{7}\.[\S]{6}\.006.[\d]{13}\.hdf$",
            'thumbnail': r"^BROWSE\.M.{6}.A[\d]{7}\.[\S]{6}\.006.[\d]{13}\.hdf$",
            'meta': r"^M.{6}.A[\d]{7}\.[\S]{6}\.006.[\d]{13}\.hdf\.met$"
        }
    
    def __init__(self, i, path=None, config={}, **kwargs):
        """ This is where you can check the incoming cumulus message
            config and input and raise Errors if they are incorrect
        """
        # we first call the original's class init to prepare the class instance 
        super(Modis, self).__init__(i, path, config, **kwargs)

        # then check to see if all the required config keys are provided
        required = ['bucket', 'fileStagingDir']

        for requirement in required:
            if requirement not in self.config.keys():
                raise Exception('%s config key is missing' % requirement)

        # we also expect to receive the input as a list
        if not isinstance(i, list):
            raise Exception('Modis process expects to receive input as a list')
        self.input = i

    
    def process(self):
        """
            All subclasses of Process class are expected to implement the
            process method. The actual processing goes here. We are only faking
            the process in this example
        """

        # Let's download the hdf file
        # the fetch method of the process class uses the input_keys properties and
        # the self.input list to determine which files matches a given key
        # it then downloads them. It returns a list because of multiple files could
        # match the given regex. in this example we are sure that only one file
        # matches each regex
        self.fetch('hdf', remote=True)[0]

        # and the thumbnail
        thumbnail = self.fetch('thumbnail')[0]

        # and the metadata
        self.fetch('meta')[0]

        # now lets upload all one of the downloaded files with a new name to the remote
        # location given in the config
        new_file = os.path.join(os.path.dirname(thumbnail), 'new_file.jpg')
        os.rename(thumbnail, new_file)
        outputs = helpers.upload_files([new_file], self.config['bucket'], self.config['fileStagingDir'])

        # and now return the list of uploaded files
        return self.input + outputs


# to activate the CLI for the process class this line should be added
if __name__ == "__main__":
    Modis.cli()