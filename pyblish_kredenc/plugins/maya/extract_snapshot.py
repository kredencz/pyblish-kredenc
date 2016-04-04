import os
import contextlib

import pyblish.api
from pyblish_kredenc.vendor import capture

import pyblish_kredenc.utils as pyblish_utils

from maya import cmds
import pymel.core as pm

import json

def load_preset(path):
    """Load options json from path"""
    with open(path, "r") as f:
        return json.load(f)

@pyblish.api.log
class ExtractSnapshot(pyblish.api.Extractor):
    """Extract review instances as a quicktime

    Arguments:
        startFrame (float): Start frame of output
        endFrame (float): End frame of output
        width (int): Width of output in pixels
        height (int): Height of output in pixels
        format (str): Which format to use for the given filename,
            defaults to "qt"
        compression (str): Which compression to use with the given
            format, defaults to "h264"
        offScreen (bool): Capture off-screen
        maintainAspectRatio (bool): Whether or not to modify height for width
            in order to preserve the current aspect ratio.
        show (str): Space-separated list of which node-types to show,
            e.g. "nurbsCurves polymeshes"

    """

    families = ["review"]
    hosts = ["maya"]
    optional = True
    label = "Snapshot"

    def process(self, instance):
        self.log.info("Extracting capture..")
        components = instance.data['ftrackComponents'].copy()
        self.log.debug('Components: {}'.format(components))

        format = instance.data('format') or 'image'
        # # compression = instance.data('compression') or 'h264'
        off_screen = instance.data('offScreen', False)
        maintain_aspect_ratio = instance.data('maintainAspectRatio', True)

        camera = instance[0]

        preset_name = 'default'

        preset_path = os.path.join(os.path.dirname(pyblish_utils.__file__),
                                   'capture_presets',
                                   (preset_name + '.json'))

        try:
            preset = capture.parse_active_view()
        except:
            self.log.debug(pyblish_utils.__file__)
            preset = load_preset(preset_path)
            preset['camera'] = camera

        # Ensure name of camera is valid
        sourcePath = os.path.normpath(instance.context.data('currentFile'))
        path, extension = os.path.splitext(sourcePath)
        path = (path + ".jpg")

        self.log.info("Outputting to %s" % path)

        with maintained_time():
            output = capture.snap(
                filename=path,
                format=format,
                viewer=False,
                off_screen=off_screen,
                maintain_aspect_ratio=maintain_aspect_ratio,
                overwrite=True,
                quality=80,
                **preset
                )


        instance.data["outputPath_jpg"] = output


@contextlib.contextmanager
def maintained_time():
    ct = cmds.currentTime(query=True)
    try:
        yield
    finally:
        cmds.currentTime(ct, edit=True)
