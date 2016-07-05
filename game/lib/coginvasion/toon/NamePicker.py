"""
  
  Filename: NamePicker.py
  Created by: blach (??June14)
  
"""

from lib.coginvasion.globals import CIGlobals
from direct.gui.DirectGui import OnscreenText, DirectEntry, DirectButton


class NamePicker:
	def __init__(self):
		self.instructions = OnscreenText(text="Type your name", scale=0.1, fg=(1,1,1,1), pos=(0, 0.8, 0.8), shadow=(0,0,0,1))
		self.nameEntry = DirectEntry(focus=1, initialText="Toon", width=10, scale=0.1, pos=(-0.5, 0.3, 0.3), command=self.confirmNameAndContinue)
		self.confirmBtn = DirectButton(text="Confirm", scale=0.1, pos=(0, 0.1, 0.1), command=self.confirmNameAndContinue, extraArgs=[self.nameEntry.get()])
	def confirmNameAndContinue(self, textEntered):
		try:
			self.badName_lbl.remove()
			del self.badName_lbl
		except:
			pass
		if self.nameEntry.get().isspace() or len(self.nameEntry.get()) <= 0:
			self.badName_lbl = OnscreenText(text=CIGlobals.InvalidName, scale=0.09, fg=(1,0,0,1), pos=(0, -0.1, -0.1), shadow=(0,0,0,1))
			return
		else:
			self.instructions.remove()
			self.nameEntry.remove()
			self.confirmBtn.remove()
			try:
				self.badName_lbl.remove()
			except:
				pass
			messenger.send("nameConfirmed", [self.nameEntry.get()])
