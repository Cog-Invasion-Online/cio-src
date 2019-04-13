"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Metadata.py
@author Maverick Liberty (Adapted from 'game' class concept)
@date October 4, 2018

@desc This replaces the old 'game' class that was a builtin that didn't follow conventions or
make a lot of sense name-wise.

"""

import datetime
import os
import sys

class Metadata:
    PROCESS_NAME = 'coginvasion'
    PROCESS = 'client'
    SERVER_ADDRESS = os.environ.get('GAME_SERVER')
    RESOURCE_ENCRYPTION_PASSWORD = 'cio-03-06-16_lsphases'
    BUILD_NUMBER = 0
    BUILD_TYPE = 'Dev'
    BUILD_DATE = '{:%B %d, %Y}'.format(datetime.datetime.now())
    VERSION = '0.0.0'
    IS_PRODUCTION = 0
    PHASE_DIRECTORY = './resources/'
    USE_RENDER_PIPELINE = 0
    USE_LIGHTING = 1
    USE_REAL_SHADOWS = 1
    PHYS_FIXED_TIMESTEP = 1
    PHYS_SUBSTEPS = 1
    MULTITHREADED_PIPELINE = 0
    
    def __init__(self):
        try:
            # Let's try to load the `builddata` module.
            import builddata
            self.BUILD_NUMBER = int(builddata.BUILDNUM)
            self.BUILD_TYPE = builddata.BUILDTYPE
            self.BUILD_DATE = builddata.BUILDDATE
            self.VERSION = builddata.BUILDVER
            
            # Let's load phases from the root directory in production.
            self.PHASE_DIRECTORY = './'
            self.IS_PRODUCTION = 1
        except: pass
        
        if self.USE_RENDER_PIPELINE:
            sys.path.insert(0, './renderpipeline')
            
    def getBuildInformation(self):
        return 'Version {0} (Build {1} : {2})'.format(self.VERSION, self.BUILD_NUMBER, self.BUILD_TYPE)
