"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DLStreet.py
@author Brian Lach
@date July 26, 2015

"""

import Street

class DLStreet(Street.Street):

    def enter(self, requestStatus):
        Street.Street.enter(self, requestStatus)
        base.prepareScene()

    def exit(self):
        for lampList in self.loader.lampLights.values():
            for lamp in lampList:
                render.clearLight(lamp)
        Street.Street.exit(self)
