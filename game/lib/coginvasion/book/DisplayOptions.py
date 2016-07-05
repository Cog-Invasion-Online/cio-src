########################################
# Filename: DisplayOptions.py
# Created by: blach (??Jul14)
########################################

from lib.coginvasion.manager.SettingsManager import SettingsManager

class DisplayOptions:
	
	def initializeWindow(self):
		SettingsManager().getSettings("settings.json")
