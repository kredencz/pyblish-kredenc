import os
import contextlib
import subprocess

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
class ExtractQuicktime(pyblish.api.Extractor):
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
    label = "Quicktime"

    def process(self, instance):
        self.log.info("Extracting capture..")
        components = instance.data['ftrackComponents'].copy()
        self.log.debug('Components: {}'.format(components))

        camera = instance[0]

        if 'persp' in camera:
            self.log.info("If you want movie review, create a camera with \
                          '_cam' suffix")
            return

        fmt = instance.data('format') or 'image'
        compression = instance.data('compression') or 'png'
        off_screen = instance.data('offScreen', False)
        maintain_aspect_ratio = instance.data('maintainAspectRatio', True)


        check_viewport = False

        # Choose preset
        preset_name = 'default'

        ### PROJECT FILTERING

        # KOS Presets
        if instance.context.data['ftrackData']['Project']['code'] == 'kos':
            preset_name = 'kos'
            check_viewport = True
            if instance.context.data['ftrackData']['Task']['type'] in ['Animation', 'Layout', 'Lookdev']:
                preset_name = 'kos_anim'
        # HBT Presets
        if instance.context.data['ftrackData']['Project']['code'] == 'hbt':
            self.log.info('hbt')
            preset_name = 'hbt'
            check_viewport = False


        # load Preset
        preset_path = os.path.join(os.path.dirname(pyblish_utils.__file__),
                                   'capture_presets',
                                   (preset_name + '.json'))

        if check_viewport:
            try:
                preset = capture.parse_active_view()
            except:
                preset = load_preset(preset_path)
                preset['camera'] = camera
        else:
            preset = load_preset(preset_path)
            preset['camera'] = camera

        dir_path = pyblish_utils.temp_dir(instance)

        # Ensure name of camera is valid
        sourcePath = os.path.normpath(instance.context.data('currentFile'))
        path, extension = os.path.splitext(sourcePath)
        image_folder, filename = os.path.split(path)
        output_images = os.path.join(dir_path, filename)


        self.log.info("Outputting images to %s" % output_images)

        with maintained_time():
            outputI = capture.capture(
                filename=output_images,
                format=fmt,
                viewer=False,
                compression=compression,
                off_screen=off_screen,
                maintain_aspect_ratio=maintain_aspect_ratio,
                overwrite=True,
                quality=70,
                **preset
                )

        audio = ''

        if audio != '':
            audio = '-i ' + audio + ' -map 0 -map 1 -c:a libtwolame'
        paddingExp = ".%4d"
        filename, extension = os.path.splitext(outputI)
        filename, padding = os.path.splitext(filename)
        outputI = filename + paddingExp + extension
        outputV = (path + ".mov")
        instance.data["outputPath_qt"] = outputV
        self.log.info("Outputting video to %s" % outputV)
        output = subprocess.call('ffmpeg -i {0} {2} -c:v libx264 -preset veryslow -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -crf 22 -y {1}'.format(outputI, outputV, audio))




@contextlib.contextmanager
def maintained_time():
    ct = cmds.currentTime(query=True)
    try:
        yield
    finally:
        cmds.currentTime(ct, edit=True)
