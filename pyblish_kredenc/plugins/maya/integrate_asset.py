import shutil
import os
import pyblish.api


@pyblish.api.log
class ConformAsset(pyblish.api.Conformer):
    """Copies asset to it's final location
    """

    families = ['model', 'rig', 'cache', 'camera', 'look']
    label = 'Integrate Assets'

    def process(self, instance):

        extractedPaths = [v for k,v in instance.data.items() if k.startswith('outputPath')]
        self.log.debug(extractedPaths)
        for path in extractedPaths:

            sourcePath = path
            filename, ext = os.path.splitext(sourcePath)
            self.log.debug('source filename: ' + filename)
            self.log.debug('source ext: ' + ext)
            publishFile = instance.data['publishFile']
            publishFile = os.path.splitext(publishFile)[0] + ext
            self.log.debug(publishFile)

            components = instance.data['ftrackComponents']

            components[str(ext)[1:]] = {'path': publishFile}

            self.log.debug('components: {}'.format(str(components)))

            if not os.path.exists(os.path.dirname(publishFile)):
                os.makedirs(os.path.dirname(publishFile))

            self.log.info('Copying model from location: {}'.format(sourcePath))
            self.log.info('Copying model to location: {}'.format(publishFile))
            shutil.copy(sourcePath, publishFile)

            instance.data['publishFile'] = publishFile
