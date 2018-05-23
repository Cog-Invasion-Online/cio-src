from src.coginvasion.standalone.StandaloneToon import *

mdl = loader.loadModel("phase_4/models/neighborhoods/toontown_central_beta_notfixed.bam")
mdl.find('**/ground_center').setBin('ground', 18)
mdl.find('**/ground_sidewalk').setBin('ground', 18)
mdl.find('**/ground').setBin('ground', 18)
mdl.find('**/ground_center_coll').setCollideMask(CIGlobals.FloorBitmask)
mdl.find('**/ground_sidewalk_coll').setCollideMask(CIGlobals.FloorBitmask)

mdl.writeBamFile("toontown_central_beta.bam")

base.run()