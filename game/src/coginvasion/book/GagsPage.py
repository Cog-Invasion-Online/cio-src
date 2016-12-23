########################################
# Filename: GagsPage.py
# Created by: DecodedLogic (18Jun16)
########################################

from src.coginvasion.book.BookPage import BookPage
from src.coginvasion.gui.BackpackGUI import BackpackGUI

class GagsPage(BookPage):

    def __init__(self, book):
        BookPage.__init__(self, book, 'Gags')
        self.gui = None

    def load(self):
        BookPage.load(self)
        invIcons = loader.loadModel("phase_3.5/models/gui/inventory_icons.bam")
        self.icon = invIcons.find('**/inventory_tart')
        self.iconScale = 7.0
        invIcons.detachNode()

    def enter(self):
        BookPage.enter(self)
        self.gui = BackpackGUI()
        self.gui.createGUI()

    def exit(self):
        if self.gui:
            self.gui.deleteGUI()
            self.gui = None
        BookPage.exit(self)
