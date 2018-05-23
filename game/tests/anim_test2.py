from src.coginvasion.standalone.StandaloneToon import *

don = loader.loadModel("phase_4/models/char/daisyduck_1600.bam")
don.reparentTo(render)
don.place()

base.startDirect()
base.run()