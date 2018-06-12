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
        for lamp in self.loader.lampLights:
            render.setLight(lamp)
        Street.Street.enter(self, requestStatus)
        base.prepareScene()

    def exit(self):
        for lamp in self.loader.lampLights:
            render.clearLight(lamp)
        Street.Street.exit(self)
