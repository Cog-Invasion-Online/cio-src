"""

  Filename: GunGameLevelLoader.py
  Created by: blach (22Apr15)

"""

from pandac.PandaModules import NodePath, Vec3, Point3, CompassEffect
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import OnscreenText

from lib.coginvasion.hood.SkyUtil import SkyUtil
from lib.coginvasion.distributed.HoodMgr import HoodMgr
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.dna.DNALoader import *
import GunGameGlobals as GGG

hoodMgr = HoodMgr()

class GunGameLevelLoader:
    notify = directNotify.newCategory("GunGameLevelLoader")

    LevelData = {
        # momada means: Mix Of Mint And District Attorney's
        'momada': {
            'name': CIGlobals.ToonBattleOriginalLevel,
            'camera': (Point3(0.0, -25.80, 7.59), Vec3(0.00, 0.00, 0.00)),
            'models': [
                "phase_11/models/lawbotHQ/LB_Zone03a.bam",
                "phase_11/models/lawbotHQ/LB_Zone04a.bam",
                "phase_11/models/lawbotHQ/LB_Zone7av2.bam",
                "phase_11/models/lawbotHQ/LB_Zone08a.bam",
                "phase_11/models/lawbotHQ/LB_Zone13a.bam",
                "phase_10/models/cashbotHQ/ZONE17a.bam",
                "phase_10/models/cashbotHQ/ZONE18a.bam",
                "phase_11/models/lawbotHQ/LB_Zone22a.bam"
            ],
            'parents': [
                render,
                "EXIT",
                "EXIT",
                "EXIT",
                "ENTRANCE",
                "ENTRANCE",
                "ENTRANCE",
                "EXIT"
            ],
            'model_positions': [
                Point3(0.00, 0.00, 0.00),
                Point3(-1.02, 59.73, 0.00),
                Point3(0.00, 74.77, 0.00),
                Point3(0.00, 89.37, -13.50),
                Point3(16.33, -136.53, 0.00),
                Point3(-1.01, -104.40, 0.00),
                Point3(0.65, -23.86, 0.00),
                Point3(-55.66, -29.01, 0.00)
            ],
            'model_orientations': [
                Vec3(0.00, 0.00, 0.00),
                Vec3(0.00, 0.00, 0.00),
                Vec3(90.00, 0.00, 0.00),
                Vec3(180.00, 0.00, 0.00),
                Vec3(97.00, 0.00, 0.00),
                Vec3(359.95, 0.00, 0.00),
                Vec3(90.00, 0.00, 0.00),
                Vec3(270.00, 0.00, 0.00)
            ],
            'spawn_points': [
                (Point3(0, 0, 0), Vec3(0, 0, 0)),
                (Point3(-20, 50, 0), Vec3(0, 0, 0)),
                (Point3(20, 50, 0), Vec3(0, 0, 0)),
                (Point3(0, 120, 0), Vec3(0, 0, 0)),
                (Point3(0, 100, 0), Vec3(180, 0, 0)),
                (Point3(-90, 0, 0), Vec3(0, 0, 0)),
                (Point3(-170, 0, 0), Vec3(0, 0, 0)),
                (Point3(-90, 50, 0), Vec3(0, 0, 0)),
                (Point3(-170, 50, 0), Vec3(0, 0, 0)),
                (Point3(35, 250, 0), Vec3(-90, 0, 0)),
                (Point3(0, 285, 0), Vec3(180, 0, 0)),
                (Point3(-185, 250, 0), Vec3(90, 0, 0))
            ]
        },

        'dg': {
            'name': CIGlobals.DaisyGardens,
            'camera': (Point3(-33.13, -3.20, 48.62), Vec3(326.31, 332.68, 0.00)),
            'dna': [
                'phase_8/dna/storage_DG.pdna',
                'phase_8/dna/storage_DG_sz.pdna',
                'phase_8/dna/daisys_garden_sz.pdna'
            ],
            'sky': 'TT',
            'spawn_points': hoodMgr.dropPoints[CIGlobals.DaisyGardens]
        },

        'mml': {
            'name': CIGlobals.MinniesMelodyland,
            'camera': (Point3(-54.42, -91.05, 34.89), Vec3(315.29, 336.80, 0.00)),
            'dna': [
                'phase_6/dna/storage_MM.pdna',
                'phase_6/dna/storage_MM_sz.pdna',
                'phase_6/dna/minnies_melody_land_sz.pdna'
            ],
            'sky': 'MM',
            'spawn_points': hoodMgr.dropPoints[CIGlobals.MinniesMelodyland]
        },

        'oz': {
            'name': CIGlobals.OutdoorZone,
            'camera': (Point3(-54.42, -91.05, 34.89), Vec3(315.29, 336.80, 0.00)),
            'dna': [
                'phase_6/dna/storage_OZ.pdna',
                'phase_6/dna/storage_OZ_sz.pdna',
                'phase_6/dna/outdoor_zone_sz.pdna'
            ],
            'sky': 'TT',
            'spawn_points': hoodMgr.dropPoints[CIGlobals.OutdoorZone]
        },

        'cbhq': {
            'name': CIGlobals.CashbotHQ,
            'camera': (Point3(302.64, 5.00, 15.20), Vec3(135.00, 341.57, 0.00)),
            'model': 'phase_10/models/cogHQ/CashBotShippingStation.bam',
            'sky': None,
            'spawn_points': hoodMgr.dropPoints[CIGlobals.CashbotHQ]
        },

        'sbf': {
            'name': CIGlobals.SellbotFactory,
            'camera': (Point3(0, 0, 0), Vec3(0, 0, 0)),
            'model': "phase_9/models/cogHQ/SelbotLegFactory.bam",
            'sky': 'cog',
            'sky_scale': 10.0,
            'occluders': 'phase_9/models/cogHQ/factory_sneak_occluders.egg',
            'spawn_points': {GGG.Teams.BLUE: [
                    (Point3(13, 30, 3.73), Point3(0, 0, 0)), (Point3(21, 30, 3.73), Point3(0, 0, 0)), (Point3(29, 30, 3.73), Point3(0, 0, 0)),
                    (Point3(13, 20, 3.73), Point3(0, 0, 0)), (Point3(21, 20, 3.73), Point3(0, 0, 0)), (Point3(29, 30, 3.73), Point3(0, 0, 0))],
                GGG.Teams.RED: [
                    (Point3(-644.43, 378.12, 8.73), Point3(270, 0, 0)), (Point3(-644.43, 370.75, 8.73), Point3(270, 0, 0)), (Point3(-644.43, 363.22, 8.73), Point3(270, 0, 0)),
                    (Point3(-659.05, 378.12, 8.73), Point3(270, 0, 0)), (Point3(-659.05, 370.75, 8.73), Point3(270, 0, 0)), (Point3(-659.05, 363.22, 8.73), Point3(270, 0, 0))]
            },
            'flag_points': {GGG.Teams.BLUE: [Point3(213.23, 340.59, 19.73), Point3(90, 0, 0)],
                GGG.Teams.RED: [Point3(-543.60, 595.79, 9.73), Point3(270, 0, 0)]},
            'flagpoint_points': {GGG.Teams.BLUE: [Point3(-543.60, 595.79, 9.73), Point3(270, 0, 0)],
                GGG.Teams.RED: [Point3(213.23, 340.59, 19.73), Point3(0, 0, 0)]}
        },
        
        'ttc' : {
            'name' : CIGlobals.ToontownCentral,
            'dna' : [
                'phase_4/dna/storage_TT.pdna',
                'phase_4/dna/storage_TT_sz.pdna',
                'phase_4/dna/new_ttc_sz.pdna',
            ],
            'sky' : 'TT',
            'spawn_points' : [
                (9.90324401855, 91.9139556885, 8.0364112854, -545.909545898, 0.0, 0.0),
                (77.9181442261, 50.953086853, 7.52815723419, -598.509460449, 0.0, 0.0),
                (93.7379760742, 6.37303066254, 7.99749088287, -626.209533691, 0.0, 0.0),
                (39.0383415222, -81.5989837646, 8.01874637604, -694.309265137, 0.0, 0.0),
                (-19.2093048096, -95.1359481812, 8.07303524017,  -731.409240723, 0.0, 0.0),
                (-84.4093933105, -45.4780502319, 8.06541728973, -781.809143066, 0.0, 0.0),
                (-92.2512283325, 2.41426730156, 8.03108692169, -811.70916748, 0.0, 0.0),
                (46.8868179321, 81.3593673706, 8.04793071747, -955.309509277, 0.0, 0.0),
                (32.3203735352, 90.0017929077, 8.06353855133, -884.409301758, 0.0, 0.0)
            ],
            'cap_point' : Point3(-1.5, 0, 0)
        }
    }

    SkyData = {
        'TT': 'phase_3.5/models/props',
        'MM': 'phase_6/models/props',
        'cog': 'phase_9/models/cogHQ',

        'MovingSkies': ['TT']
    }

    def __init__(self, mg):
        self.mg = mg
        self.levelName = None
        self.dnaStore = DNAStorage()
        self.loadingText = None

        # for not momada only:
        self.levelGeom = None
        self.skyUtil = None
        self.skyModel = None
        self.occluders = None

        # for momada only:
        self.momadaAreas = []
        self.momadaAreaName2areaModel = {}

    def getFlagPoint_Point(self, team):
        return self.LevelData[self.levelName]['flagpoint_points'][team]

    def getFlagPoint(self, team):
        return self.LevelData[self.levelName]['flag_points'][team]
    
    def getCapturePoint(self):
        return self.LevelData[self.levelName]['cap_point']

    def setLevel(self, level):
        self.levelName = level

    def getLevel(self):
        return self.levelName

    def getCameraOfCurrentLevel(self):
        return self.LevelData[self.getLevel()]['camera']

    def getSpawnPoints(self):
        # Return the spawn points for this level.
        pointData = self.LevelData[self.levelName]['spawn_points']
        if self.levelName == "momada":
            return pointData
        else:
            if self.mg.gameMode in [GGG.GameModes.CASUAL, GGG.GameModes.KOTH]:
                # These points come from lib.coginvasion.distributed.HoodMgr,
                # which is a tuple of a bunch of arrays with pos as first
                # 3, and hpr as last 3 list elements.
                #
                # Disect the arrays and return a tuple holding a Point3 pos, and a Vec3 hpr.
                array = []
                for posAndHpr in pointData:
                    array.append(
                        (
                            Point3(
                                posAndHpr[0],
                                posAndHpr[1],
                                posAndHpr[2]
                            ),

                            Vec3(
                                posAndHpr[3],
                                posAndHpr[4],
                                posAndHpr[5]
                            )
                        )
                    )
            elif self.mg.gameMode == GGG.GameModes.CTF:
                array = pointData[self.mg.team]
            return array

    def getNameOfCurrentLevel(self):
        return self.LevelData[self.getLevel()]['name']

    def load(self):
        self.unload()
        if self.loadingText:
            self.loadingText.destroy()
            self.loadingText = None
        self.loadingText = OnscreenText(text = "",
            font = CIGlobals.getMinnieFont(), fg = (1, 1, 1, 1))
        self.loadingText.setBin('gui-popup', 0)
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        if self.levelName == "momada":
            # momada is completely different from the other levels,
            # so it has it's own separate method for loading.
            self.__momadaLoad()
        elif self.levelName in ['cbhq', 'sbf']:
            # Cog hqs are just one model with everything in it. no dna loading needed.
            modelPath = self.LevelData[self.levelName]['model']
            self.levelGeom = loader.loadModel(modelPath)
            self.levelGeom.flattenMedium()
            self.levelGeom.reparentTo(render)
            if self.LevelData[self.levelName]['sky'] != None:
                self.skyModel = loader.loadModel(self.SkyData['cog'] + '/cog_sky.bam')
                self.skyUtil = SkyUtil()
                self.skyUtil.startSky(self.skyModel)
                self.skyModel.reparentTo(render)
                self.skyModel.setScale(self.LevelData[self.levelName].get('sky_scale', 1.0))
            if self.LevelData[self.levelName].get('occluders'):
                self.occluders = loader.loadModel(self.LevelData[self.levelName]['occluders'])
                for occluderNode in self.occluders.findAllMatches('**/+OccluderNode'):
                    base.render.setOccluder(occluderNode)
                    occluderNode.node().setDoubleSided(True)
            if self.levelName == 'sbf':
                base.camLens.setFar(250)
        else:
            # It's a playground with dna and stuff. Just do the
            # normal loading procedure.
            dnaFiles = self.LevelData[self.levelName]['dna']
            skyType = self.LevelData[self.levelName]['sky']
            skyPhase = self.SkyData[skyType]
            loadDNAFile(self.dnaStore, 'phase_4/dna/storage.pdna')
            for index in range(len(dnaFiles)):
                if index == len(dnaFiles) - 1:
                    node = loadDNAFile(self.dnaStore, dnaFiles[index])
                    if node.getNumParents() == 1:
                        self.levelGeom = NodePath(node.getParent(0))
                        self.levelGeom.reparentTo(hidden)
                    else:
                        self.levelGeom = hidden.attachNewNode(node)
                    if self.levelName == 'ttc' and dnaFiles[index] == 'phase_4/dna/new_ttc_sz.pdna':
                        self.levelGeom.find('**/prop_gazebo_DNARoot').removeNode()
                    else:
                        self.levelGeom.flattenMedium()
                    gsg = base.win.getGsg()
                    if gsg:
                        self.levelGeom.prepareScene(gsg)
                    self.levelGeom.reparentTo(render)
                else:
                    loadDNAFile(self.dnaStore, dnaFiles[index])
            children = self.levelGeom.findAllMatches('**/*doorFrameHole*')
            
            for child in children:
                child.hide()
            self.skyModel = loader.loadModel(skyPhase + "/" + skyType + "_sky.bam")
            self.skyUtil = SkyUtil()
            self.skyUtil.startSky(self.skyModel)
            self.skyModel.reparentTo(camera)
            ce = CompassEffect.make(NodePath(), CompassEffect.PRot | CompassEffect.PZ)
            self.skyModel.node().setEffect(ce)
        if self.loadingText:
            self.loadingText.destroy()
            self.loadingText = None

    def __momadaLoad(self):

        def attachArea(itemNum):
            name = 'MomadaArea-%s' % itemNum
            area = self.momadaAreaName2areaModel.get(name)
            parents = self.LevelData['momada']['parents']
            parent = parents[itemNum]
            if type(parent) == type(""):
                parent = self.momadaAreas[itemNum - 1].find('**/' + parent)
            pos = self.LevelData['momada']['model_positions'][itemNum]
            hpr = self.LevelData['momada']['model_orientations'][itemNum]
            area.reparentTo(parent)
            area.setPos(pos)
            area.setHpr(hpr)

        _numItems = 0
        name = None
        for item in self.LevelData['momada']['models']:
            name = 'MomadaArea-%s' % _numItems
            area = loader.loadModel(item)
            self.momadaAreas.append(area)
            self.momadaAreaName2areaModel[name] = area
            attachArea(_numItems)
            _numItems += 1
            self.notify.info("Loaded and attached %s momada areas." % _numItems)

    def unload(self):
        render.clearOccluder()
        if self.levelName == "sbf":
            base.camLens.setFar(CIGlobals.DefaultCameraFar)
        if self.levelName == "momada":
            for area in self.momadaAreas:
                self.momadaAreas.remove(area)
                area.removeNode()
                del area
            self.momadaAreas = []
            self.momadaAreaName2areaModel = {}
        else:
            if self.occluders:
                self.occluders.removeNode()
                self.occluders = None
            if self.skyUtil:
                self.skyUtil.stopSky()
                self.skyUtil = None
            if self.skyModel:
                self.skyModel.removeNode()
                self.skyModel = None
            if self.levelGeom:
                self.levelGeom.removeNode()
                self.levelGeom = None

    def cleanup(self):
        self.momadaAreas = None
        self.momadaAreaName2areaModel = None
        if self.dnaStore:
            self.dnaStore.reset_nodes()
            self.dnaStore.reset_hood_nodes()
            self.dnaStore.reset_place_nodes()
            self.dnaStore.reset_hood()
            self.dnaStore.reset_fonts()
            self.dnaStore.reset_DNA_vis_groups()
            self.dnaStore.reset_textures()
            self.dnaStore.reset_block_numbers()
            self.dnaStore.reset_block_zones()
            self.dnaStore.reset_suit_points()
        self.dnaStore = None
