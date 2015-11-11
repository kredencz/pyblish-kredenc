import pyblish.api

import nuke


@pyblish.api.log
class ExtractDeadlineNuke(pyblish.api.Extractor):
    """ Gathers optional Nuke related data for Deadline
    """

    families = ['deadline.render']
    hosts = ['nuke']
    version = (0, 1, 0)

    def process(self, instance):

        # getting job data
        job_data = {}
        if instance.has_data('deadlineJobData'):
            job_data = instance.data('deadlineJobData').copy()

        # setting optional data
        job_data['Pool'] = 'comp'
        job_data['ChunkSize'] = '10'
        group = 'nuke'
        job_data['Group'] = group
        job_data['LimitGroups'] = group

        instance.set_data('deadlineJobData', value=job_data)