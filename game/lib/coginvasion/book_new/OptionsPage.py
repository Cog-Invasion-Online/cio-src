########################################
# Filename: OptionsPage.py
# Created by: DecodedLogic (17Jun16)
# HAPPY BIRTHDAY COG INVASION ONLINE!!!
#         2 YEAR ANNIVERSARY
########################################

from lib.coginvasion.book_new.BookPage import BookPage

class OptionsPage(BookPage):
    
    def __init__(self, book):
        BookPage.__init__(self, book, 'Options', wantHeader = True)
        
    def load(self):
        BookPage.load(self)
        icons = loader.loadModel('phase_3.5/models/gui/sos_textures.bam')
        self.icon = icons.find('**/switch')
        icons.detachNode()