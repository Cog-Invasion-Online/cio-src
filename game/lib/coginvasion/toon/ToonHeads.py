"""
  
  Filename: ToonHeads.py
  Created by: blach (??July14)
  
"""

from lib.coginvasion.globals import CIGlobals
import json
import random
from direct.directnotify.DirectNotifyGlobal import directNotify
from pandac.PandaModules import Point3
from direct.actor import Actor

lookSpots = [(50, 0, 0),
			(-50, 0, 0),
			(50, 35, 0),
			(-50, 35, 0),
			(50, -35, 0),
			(-50, -35, 0),
			(0, 35, 0),
			(0, -35, 0),
			(0, 0, 0)]

class ToonHeads(Actor.Actor):
	notify = directNotify.newCategory("ToonHeads")
	
	def __init__(self):
		Actor.Actor.__init__(self)
	
	def generateFromFile(self, jsonfile, slot):
		infoFile = open(jsonfile)
		jsonInfo = json.load(infoFile)

		if not jsonInfo["toon" + str(slot)]["head"] == "dog":
			h = loader.loadModel("phase_3/models/char/" + jsonInfo["toon" + str(slot)]["head"] + "-heads-" + str(CIGlobals.getModelDetail(CIGlobals.Toon)) + ".bam")
		else:
			h = loader.loadModel("phase_3/models/char/tt_a_chr_" + jsonInfo["toon" + str(slot)]["headtype"] + "_head_" + str(CIGlobals.getModelDetail(CIGlobals.Toon)) + ".bam")
		if jsonInfo["toon" + str(slot)]["headtype"] == "1":
			try: h.find('**/eyes-long').hide()
			except: pass
			try: h.find('**/ears-long').hide()
			except: pass
			try: h.find('**/head-long').hide()
			except: pass
			try:
				h.find('**/joint_pupilR_long').hide()
				h.find('**/joint_pupilL_long').hide()
			except: pass
			try: h.find('**/head-front-long').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-long-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass
		elif jsonInfo["toon" + str(slot)]["headtype"] == "2":
			try: h.find('**/eyes-short').hide()
			except: pass
			try: h.find('**/ears-short').hide()
			except: pass
			try: h.find('**/head-short').hide()
			except: pass
			try:
				h.find('**/joint_pupilR_short').hide()
				h.find('**/joint_pupilL_short').hide()
			except: pass
			try: h.find('**/head-front-short').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-long-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass
		elif jsonInfo["toon" + str(slot)]["headtype"] == "3":
			try: h.find('**/eyes-long').hide()
			except: pass
			try: h.find('**/ears-long').hide()
			except: pass
			try: h.find('**/head-long').hide()
			except: pass
			try:
				h.find('**/joint_pupilR_long').hide()
				h.find('**/joint_pupilL_long').hide()
			except: pass
			try: h.find('**/head-front-long').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-short-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass
		elif jsonInfo["toon" + str(slot)]["headtype"] == "4":
			try: h.find('**/eyes-short').hide()
			except: pass
			try: h.find('**/ears-short').hide()
			except: pass
			try: h.find('**/head-short').hide()
			except: pass
			try:
				h.find('**/joint_pupilR_short').hide()
				h.find('**/joint_pupilL_short').hide()
			except: pass
			try: h.find('**/head-front-short').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-short-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass

		try:
			if jsonInfo["toon" + str(slot)]["head"] == 'monkey':
				pass
			else:
				h.find('**/ears-long').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
				h.find('**/ears-short').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
		except:
			pass
		try:
			h.find('**/head-front-short').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
			h.find('**/head-front-long').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
			h.find('**/head-short').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
			h.find('**/head-long').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
		except:
			pass
		try:
			h.find('**/head-front').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
			h.find('**/head').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
		except:
			pass
		try:
			if jsonInfo["toon" + str(slot)]["head"] == 'dog' or jsonInfo["toon" + str(slot)]["head"] == 'monkey':
				pass
			else:
				h.find('**/ears').setColor(jsonInfo["toon" + str(slot)]["headcolor"][0], jsonInfo["toon" + str(slot)]["headcolor"][1], jsonInfo["toon" + str(slot)]["headcolor"][2], jsonInfo["toon" + str(slot)]["headcolor"][3])
		except:
			pass
			
		if jsonInfo["toon" + str(slot)]["gender"] == "girl":
			print jsonInfo["toon" + str(slot)]["head"]
			lashes = loader.loadModel("phase_3/models/char/" + jsonInfo["toon" + str(slot)]["head"] + "-lashes.bam")
			lashes.reparentTo(h)
			if jsonInfo["toon" + str(slot)]["headtype"] == "1" or jsonInfo["toon" + str(slot)]["headtype"] == "dgm_skirt" or jsonInfo["toon" + str(slot)]["headtype"] == "dgm_shorts" or jsonInfo["toon" + str(slot)]["headtype"] == "dgs_shorts":
				lashes.find('**/open-long').hide()
				lashes.find('**/closed-long').hide()
				lashes.find('**/closed-short').hide()
			elif jsonInfo["toon" + str(slot)]["headtype"] == "2" or jsonInfo["toon" + str(slot)]["headtype"] == "dgl_shorts":
				lashes.find('**/open-short').hide()
				lashes.find('**/closed-short').hide()
				lashes.find('**/closed-long').hide()
			elif jsonInfo["toon" + str(slot)]["headtype"] == "3" or jsonInfo["toon" + str(slot)]["headtype"] == "dgm_skirt" or jsonInfo["toon" + str(slot)]["headtype"] == "dgm_shorts" or jsonInfo["toon" + str(slot)]["headtype"] == "dgs_shorts":
				lashes.find('**/open-long').hide()
				lashes.find('**/closed-long').hide()
				lashes.find('**/closed-short').hide()
			elif jsonInfo["toon" + str(slot)]["headtype"] == "4" or jsonInfo["toon" + str(slot)]["headtype"] == "dgl_shorts":
				lashes.find('**/open-short').hide()
				lashes.find('**/closed-short').hide()
				lashes.find('**/closed-long').hide()
		return h
		
	def startLookAround(self, head):
		self.head = head
		delay = random.randint(3, 10)
		
		taskMgr.doMethodLater(delay, self.lookAtSpot, "lookAtSpot")
		
	def lookAtSpot(self, task):
		spot = random.randint(0, len(lookSpots) - 1)
		delay = random.randint(3, 10)
		lookInt = self.head.hprInterval(3,
									Point3(lookSpots[spot]),
									startHpr=(self.head.getHpr()), blendType='easeInOut')
		lookInt.start()
		task.delayTime = delay
		return task.again
		
	def stop(self):
		taskMgr.remove("lookAtSpot")
		
	def generate(self, gender, head, headtype):
		if not head == "dog":
			h = loader.loadModel("phase_3/models/char/" + head + "-heads-" + str(CIGlobals.getModelDetail(CIGlobals.Toon)) + ".bam")
		else:
			h = Actor("phase_3/models/char/tt_a_chr_" + headtype + "_head_" + str(CIGlobals.getModelDetail(CIGlobals.Toon)) + ".bam",
									{"neutral": "phase_3/models/char/tt_a_chr_" + headtype + "_head_neutral.bam",
									"run": "phase_3/models/char/tt_a_chr_" + headtype + "_head_run.bam",
									"walk": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_walk.bam",
									"pie": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_pie-throw.bam",
									"fallb": "phase_4/models/char/tt_a_chr_" + headtype + "_head_slip-backward.bam",
									"fallf": "phase_4/models/char/tt_a_chr_" + headtype + "_head_slip-forward.bam",
									"lose": "phase_5/models/char/tt_a_chr_" + headtype + "_head_lose.bam",
									"win": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_victory-dance.bam",
									"squirt": "phase_5/models/char/tt_a_chr_" + headtype + "_head_water-gun.bam",
									"zend": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_jump-zend.bam",
									"tele": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_teleport.bam",
									"book": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_book.bam",
									"leap": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_leap_zhang.bam",
									"jump": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_jump-zhang.bam",
									"happy": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_jump.bam",
									"shrug": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_shrug.bam",
									"hdance": "phase_5/models/char/tt_a_chr_" + headtype + "_head_happy-dance.bam",
									"wave": "phase_3.5/models/char/tt_a_chr_" + headtype + "_head_wave.bam"})
		if headtype == "1":
			try: h.find('**/eyes-long').hide()
			except: pass
			try: h.find('**/ears-long').hide()
			except: pass
			try: h.find('**/head-long').hide()
			except: pass
			try:
				h.find('**/joint_pupilR_long').hide()
				h.find('**/joint_pupilL_long').hide()
			except: pass
			try: h.find('**/head-front-long').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-long-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass
		elif headtype == "2":
			try: h.find('**/eyes-short').hide()
			except: pass
			try: h.find('**/ears-short').hide()
			except: pass
			try: h.find('**/head-short').hide()
			except: pass
			try:
				h.find('**/joint_pupilR_short').hide()
				h.find('**/joint_pupilL_short').hide()
			except: pass
			try: h.find('**/head-front-short').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-long-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass
		elif headtype == "3":
			try: h.find('**/eyes-long').hide()
			except: pass
			try: h.find('**/ears-long').hide()
			except: pass
			try: h.find('**/head-long').hide()
			except: pass
			try:
				h.find('**/joint_pupilR_long').hide()
				h.find('**/joint_pupilL_long').hide()
			except: pass
			try: h.find('**/head-front-long').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-short-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass
		elif headtype == "4":
			try: h.find('**/eyes-short').hide()
			except: pass
			try: h.find('**/ears-short').hide()
			except: pass
			try: h.find('**/head-short').hide()
			except: pass
			try: h.find('**/head-front-short').hide()
			except: pass
			try: h.find('**/muzzle-long-laugh').hide()
			except: pass
			try: h.find('**/muzzle-long-angry').hide()
			except: pass
			try: h.find('**/muzzle-long-smile').hide()
			except: pass
			try: h.find('**/muzzle-long-sad').hide()
			except: pass
			try: h.find('**/muzzle-long-surprise').hide()
			except: pass
			try: h.find('**/muzzle-short-neutral').hide()
			except: pass
			try: h.find('**/muzzle-short-laugh').hide()
			except: pass
			try: h.find('**/muzzle-short-angry').hide()
			except: pass
			try: h.find('**/muzzle-short-smile').hide()
			except: pass
			try: h.find('**/muzzle-short-sad').hide()
			except: pass
			try: h.find('**/muzzle-short-surprise').hide()
			except: pass
			
		if gender == "girl":
			lashes = loader.loadModel("phase_3/models/char/" + head + "-lashes.bam")
			lashes.reparentTo(h)
			if headtype == "1" or headtype == "dgm_skirt" or headtype == "dgm_shorts" or headtype == "dgs_shorts":
				lashes.find('**/open-long').hide()
				lashes.find('**/closed-long').hide()
				lashes.find('**/closed-short').hide()
			elif headtype == "2" or headtype == "dgl_shorts":
				lashes.find('**/open-short').hide()
				lashes.find('**/closed-short').hide()
				lashes.find('**/closed-long').hide()
			elif headtype == "3" or headtype == "dgm_skirt" or headtype == "dgm_shorts" or headtype == "dgs_shorts":
				lashes.find('**/open-long').hide()
				lashes.find('**/closed-long').hide()
				lashes.find('**/closed-short').hide()
			elif headtype == "4" or headtype == "dgl_shorts":
				lashes.find('**/open-short').hide()
				lashes.find('**/closed-short').hide()
				lashes.find('**/closed-long').hide()
			return tuple((h, lashes))
		else:
			return h
