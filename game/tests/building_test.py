from src.coginvasion.standalone.StandaloneToon import *
from src.coginvasion.cogoffice.DistributedCogOfficeBattle import DistributedCogOfficeBattle, PROPS, CogTV
from src.coginvasion.cogoffice.CogOfficeConstants import *
from src.coginvasion.cog.Dept import BOSS
from src.coginvasion.base.Lighting import IndoorLightingConfig

from direct.gui.DirectGui import DirectLabel

from panda3d.core import *

import random

#op = DirectOptionMenu(text = "options", items = ["hi", "bye"], scale = 0.1, initialitem = 1)

props = []
floorModel = None

flr = EXECUTIVE_FLOOR

ilc = None

def getRoomData(name):
    dataList = DistributedCogOfficeBattle.ROOM_DATA[flr].get(name)
    return dataList
    


def loadFloor():
    global floorModel
    global ilc

    path = getRoomData('room_mdl')
    grounds = getRoomData('grounds')
    floorModel = loader.loadModel(path)
    floorModel.reparentTo(render)
    for ground in grounds:
        floorModel.find(ground).setBin('ground', 18)
        
    lights = getRoomData('lights')
    ilc = IndoorLightingConfig.makeDefault()
    ilc.lights = lights
    #ilc.ambient = Vec4(0.3, 0.3, 0.3, 1.0)
    ilc.visLights = True
    ilc.setup()
    #ilc.lightNPs[0].node().setShadowCaster(True, 512, 512)
    ilc.apply()

    dataList = getRoomData('props')
    for propData in dataList:
        name = propData[0]
        otherProps = []
        if isinstance(PROPS[name], list):
            for i in xrange(len(PROPS[name])):
                if i == 0:
                    continue
                path = PROPS[name][i]
                otherProps.append(path)
        x, y, z = propData[1], propData[2], propData[3]
        h, p, r = propData[4], propData[5], propData[6]
        scale = propData[7]
        if isinstance(PROPS[name], list):
            propMdl = loader.loadModel(PROPS[name][0])
        else:
            if name == 'tv_on_wall':
                print "TVONWALL"
                # This is a tv with a movie texture.
                propMdl = CogTV()
            else:
                propMdl = loader.loadModel(PROPS[name])
                if name in ['light_panel']:
                    propMdl.setTwoSided(True)
        propMdl.reparentTo(render)
        propMdl.setPosHpr(x, y, z, h, p, r)
        propMdl.setScale(scale)
        if name == 'photo_frame':
            painting = random.choice(DistributedCogOfficeBattle.DEPT_2_PAINTING[BOSS])
            propMdl.find('**/photo').setTexture(loader.loadTexture(painting), 1)
        for oPropPath in otherProps:
            oPropMdl = loader.loadModel(oPropPath)
            oPropMdl.reparentTo(propMdl)
        props.append(propMdl)

        for guardData in POINTS[flr]['guard']:
            posData = guardData[1]
            pos = Point3(posData[0], posData[1], posData[2])
            lbl = DirectLabel(text = "GUARD", pos = pos + (0, 0, 1), text_scale = 1, text_decal = True, relief = None, parent = render)
            lbl.setBillboardAxis()

loadFloor()

base.run()