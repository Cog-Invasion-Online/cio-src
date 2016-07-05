# Filename: CIMovie.py
# Created by:  blach (5Aug15)

from panda3d.core import *
loadPrcFile('config/Confauto.prc')
loadPrcFile('config/config_client.prc')

from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
base.cTrav = CollisionTraverser()
base.shadowTrav = CollisionTraverser()

from direct.distributed.ClientRepository import ClientRepository
cr = ClientRepository([])
cr.isShowingPlayerIds = False

from direct.interval.IntervalGlobal import *
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.toon import Toon
from lib.coginvasion.hood.TTCHood import TTCHood

def makeToon(dna = None, name = None):
	toon = Toon.Toon(cr)
	if not dna:
		toon.setDNAStrand(toon.dnaStrand)
	else:
		toon.setDNAStrand(dna)
	if name:
		toon.setName(name)
		toon.setupNameTag()
	toon.animFSM.request('neutral')
	toon.initializeRay("toonRay", 0.01)
	toon.reparentTo(render)
	return toon
	
def makeSuit(head, skele = 0):
	suit = Suit.Suit()
	bodyData = CIGlobals.SuitBodyData[head]
	suit.generateSuit(bodyData[0], head, bodyData[1], 20, skele)
	suit.animFSM.request('neutral')
	suit.reparentTo(render)
	return suit
	
ttc = TTCHood(cr)
ttc.createHood()

t1 = makeToon()

base.run()
