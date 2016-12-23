"""
  
  Filename: HoodGui.py
  Created by: blach (04Oct14)
  
"""

from direct.gui.DirectGui import OnscreenText
from direct.interval.IntervalGlobal import LerpFunc, Sequence, Wait, Func

from src.coginvasion.globals import CIGlobals

def fadeText(a, lbl):
	lbl['fg'] = (1, 0.3, 0.5, a)
	
def startFade(lbl):
	LerpFunc(fadeText,
			fromData=1.0,
			toData=0.0,
			duration=1.0,
			extraArgs=[lbl]).start()

def announceHood(hood):
	nameLbl = OnscreenText(text="%s\n%s" % (hood, CIGlobals.Playground),
						scale=0.15, font=CIGlobals.getMickeyFont(), pos=(0, -0.65), fg=(1, 0.3, 0.5, 1.0))
	Sequence(Wait(2.5), Func(startFade, nameLbl), Wait(1), Func(nameLbl.destroy)).start()
	
