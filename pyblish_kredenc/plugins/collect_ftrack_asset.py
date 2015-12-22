import pyblish.api
import ftrack


@pyblish.api.log
class CollectFtrackAsset(pyblish.api.Collector):

    """ Validate the existence of Asset, AssetVersion and Components.
    """

    order = pyblish.api.Collector.order + 0.41
    label = 'Collect Asset Attributes'

    def process(self, instance, context):

        # skipping instance if ftrackData isn't present
        if not context.has_data('ftrackData'):
            self.log.info('No ftrackData present. Skipping this instance')
            return

        # skipping instance if ftrackComponents isn't present
        if not instance.has_data('ftrackComponents'):
            self.log.info('No ftrackComponents present\
                           Skipping this instance')
            return

        ftrack_data = context.data('ftrackData').copy()

        instance.data['ftrackAssetName'] = ftrack_data['Task']['name']

        if ftrack_data['Task']['type'] == 'Lighting':
            instance.data['ftrackAssetType'] = 'render'
        if ftrack_data['Task']['type'] == 'COmpositing':
            instance.data['ftrackAssetType'] = 'comp'
        if ftrack_data['Task']['type'] == 'lookdev':
            instance.data['ftrackAssetType'] = 'img'
        if ftrack_data['Task']['type'] == 'Modeling':
            instance.data['ftrackAssetType'] = 'geo'

        self.log.info(instance.data['ftrackAssetType'])
        self.log.info(instance.data['ftrackAssetName'])