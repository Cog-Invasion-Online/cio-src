"""

  Filename: CameraShyLevelLoader.py
  Created by: DecodedLogic (06Nov15)

  This module is only suppose to generate a single level. If you want another level, you have to
  start a new instance. Cleanup deletes all the necessary variables to build levels.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import Point3, Vec3, NodePath, Material

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.distributed.HoodMgr import HoodMgr
from src.coginvasion.dna.DNALoader import *

hoodMgr = HoodMgr()

class CameraShyLevelLoader:
    notify = directNotify.newCategory('CameraShyLevelLoader')

    levelData = {
        'TT_maze' : {
            'name' : CIGlobals.ToontownCentral,
            'models' : {
                'phase_4/models/minigames/maze_1player.bam' : {'name' : 'maze', 'scale' : Point3(3.0, 3.0, 3.0)},
                'phase_4/models/minigames/maze_1player_collisions.egg' : {'name' : 'maze_collisions', 'scale' : Point3(3.0, 3.0, 3.0)},
                'phase_4/models/minigames/tag_arena.bam' : {'name' : "tag_arena_bg", 'pos' : Point3(0, 0, -0.5), 'scale' : Point3(2.0, 2.0, 2.0)}
            },
            'spawnPoints' : [
                [Point3(0, 0, 0), Vec3(0, 0, 0)],
                [Point3(-23.89, 18.58, 0.00), Vec3(90.00, 0.00, 0.00)],
                [Point3(-23.89, 6.30, 0.00), Vec3(0.00, 0.00, 0.00)],
                [Point3(23.78, 6.30, 0.00), Vec3(0.00, 0.00, 0.00)],
                [Point3(8.12, -17.79, 0.00), Vec3(270.00, 0.00, 0.00)]
            ]
        },
        'DG_playground' : {
            'name' : CIGlobals.DaisyGardens,
            'dna': [
                'phase_8/dna/storage_DG.pdna',
                'phase_8/dna/storage_DG_sz.pdna',
                'phase_8/dna/daisys_garden_sz.pdna'
            ],
            'spawnPoints': hoodMgr.dropPoints[CIGlobals.DaisyGardens]
        }
    }

    def __init__(self):
        self.level = None
        self.dnaStore = DNAStorage()

        self.levelGeom = None
        self.olc = None

        # To keep track of all the models.
        self.models = []

    def setLevel(self, level):
        self.level = level

    def getLevel(self):
        return self.level

    def load(self):
        if not self.level:
            self.notify.warning('Attempted to load a null level!')
            return

        self.unload()
        data = self.levelData[self.level]

        # Are we loading a DNA level?
        if data.get('dna'):
            dnaFiles = data['dna']
            loadDNAFile(self.dnaStore, 'phase_4/dna/storage.pdna')

            for index in range(len(dnaFiles)):
                if 'storage' not in dnaFiles[index]:
                    # It's an environment file, let's load that up and reparent it to render.
                    node = loader.loadDNAFile(self.dnaStore, dnaFiles[index])
                    if node.getNumParents() == 1:
                        self.levelGeom = NodePath(node.getParent(0))
                        self.levelGeom.reparentTo(hidden)
                    else:
                        self.levelGeom = hidden.attachNewNode(node)
                    self.levelGeom.flattenMedium()
                    gsg = base.win.getGsg()
                    if gsg:
                        self.levelGeom.prepareScene(gsg)
                    self.levelGeom.reparentTo(render)
                else:
                    # It's just a storage file, let's just load that up.
                    loadDNAFile(self.dnaStore, dnaFiles[index])
        elif data.get('models'):
            models = data['models']
            for model, modifiers in models.items():
                mdl = loader.loadModel(model)

                if modifiers.get('name'):
                    mdl.setName(modifiers['name'])

                if modifiers.get('hpr'):
                    mdl.setHpr(modifiers['hpr'])

                if modifiers.get('pos'):
                    mdl.setPos(modifiers['pos'])

                if modifiers.get('scale'):
                    mdl.setScale(modifiers['scale'])

                if modifiers.get('parent'):
                    mdl.reparentTo(modifiers['parent'])
                else:
                    mdl.reparentTo(render)
                self.models.append(mdl)
        else:
            self.notify.warning('Attempted to load a level with no data on how to generate it. Level is empty!')
            return

        self.olc = ZoneUtil.getOutdoorLightingConfig(data.get('name'))
        self.olc.setupAndApply()

        self.levelLoaded()

    def unload(self):
        if self.models:
            if len(self.models) > 0:
                for model in self.models:
                    model.removeNode()
        self.models = []
        if self.levelGeom:
            self.levelGeom.removeNode()
            self.levelGeom = None
        if self.olc:
            self.olc.cleanup()
            self.olc = None
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

        # This is set outside of the class, so no need to check if it exists.
        hoodMgr = None

    def cleanup(self):
        try:
            self.CameraShyLevelLoader_deleted
        except:
            self.CameraShyLevelLoader_deleted = 1
            if self.dnaStore:
                self.unload()
            self.models = None
            self.levelGeom = None
            self.olc = None
            self.dnaStore = None
            self.levelData = None

    def levelLoaded(self):
        if self.level == 'TT_maze':
            for model in self.models:
                if model.getName() == 'maze':
                    brightenMat = Material()
                    brightenMat.setShininess(2.0)
                    brightenMat.setEmission((0, 0.25, 0.16, 1))

                    walls = model.find('**/maze_walls') 
                    walls.setSz(1.5)
                    walls.setTexture(loader.loadTexture('phase_4/maps/DGhedge.jpg'), 1)
                    walls.setMaterial(brightenMat)
                    
                    floor = model.find('**/maze_floor')
                    floor.setTexture(loader.loadTexture('phase_4/maps/grass.jpg'), 1)
                    model.setShaderAuto()
                    
                elif model.getName() == 'maze_collisions':
                    model.hide()
                    model.setTransparency(1)
                    model.setColorScale(1, 1, 1, 0)
                    for node in model.findAllMatches('**'):
                        node.setSz(1.5)
                elif model.getName() == 'tag_arena_bg':
                    model.find('**/g1').removeNode()

    def getSpawnPoints(self):
        if self.level:
            points = self.levelData[self.level].get('spawnPoints')

            # Do we need to disect the pos and hpr coordinates?
            if points in hoodMgr.dropPoints.values():
                twoPointArray = []
                for posHpr in points:
                    twoPointArray.append(
                        Point3(
                            posHpr[0],
                            posHpr[1],
                            posHpr[2]
                        ),
                        Vec3(
                            posHpr[3],
                            posHpr[4],
                            posHpr[5]
                        )
                    )
                points = twoPointArray
            return points
        else:
            self.notify.warning('Attempted to get spawn points of a null level!')
            return None
