"""

  Filename: UnoGameHeadPanel.py
  Created by: blach (20Oct14)
  
"""

from panda3d.core import VBase4, Point3

from direct.gui.DirectGui import DirectFrame, DirectLabel

from src.coginvasion.toon.ToonHead import ToonHead

class UnoGameHeadPanel:
	
	def __init__(self):
		self.frameColors = [VBase4(0.153, 0.75, 0.255, 1.0),
							VBase4(0.915, 0.165, 0.165, 1.0),
							VBase4(0.13, 0.59, 0.97, 1.0),
							VBase4(0.976, 0.816, 0.13, 1.0)]
		self.framePositions = [Point3(0.15, 0, -0.15),
							Point3(0.43, 0, -0.15),
							Point3(0.15, 0, -0.43),
							Point3(0.43, 0, -0.43)]
		self.frameList = []
		self.doId2Frame = {}
		
	def generate(self, gender, head, headtype, color, doId, name):
		gui = loader.loadModel("phase_3/models/gui/pick_a_toon_gui.bam")
		bg = gui.find('**/av-chooser_Square_UP')
		container = DirectFrame(relief=None, scale=0.3, parent=base.a2dTopLeft)
		container['image'] = bg
		container['image_color'] = self.frameColors[len(self.frameList)]
		container.setPos(self.framePositions[len(self.frameList)])
		headframe = container.attachNewNode('head')
		headframe.setPosHprScale(0, 5, -0.1, 180, 0, 0, 0.24, 0.24, 0.24)
		toon = ToonHead(None)
		toon.generateHead(gender, head, headtype)
		r, g, b = color
		color = (r, g, b, 1.0)
		toon.setHeadColor(color)
		toon.setDepthWrite(1)
		toon.setDepthTest(1)
		toon.reparentTo(headframe)
		nameLbl = DirectLabel(text=name, text_wordwrap=7.0, parent=container, text_scale=0.13,
						text_fg=(1,1,1,1), text_shadow=(0,0,0,1), relief=None, pos=(0, 0, 0.25))
		cardCount = DirectLabel(text="0", parent=container, text_scale=0.15, text_fg=(1,1,1,1),
							text_shadow=(0,0,0,1), relief=None, pos=(0.26, 0, -0.28))
		self.frameList.append(container)
		self.doId2Frame[doId] = tuple((container, headframe, toon, nameLbl, cardCount))
		
	def updateCardCount(self, doId, direction):
		count = 0
		if self.doId2Frame.has_key(doId):
			container, headframe, toon, nameLbl, cardCount = self.doId2Frame[doId]
			if direction == 0:
				count = int(cardCount['text']) - 1
			elif direction == 1:
				count = int(cardCount['text']) + 1
			cardCount['text'] = str(count)
			
	def destroy(self):
		for frame in self.frameList:
			frame.destroy(); del frame
			
	def delete(self):
		self.destroy()
		self.frameList = None
		self.doId2Frame = None
		self.frameColors = None
		return
