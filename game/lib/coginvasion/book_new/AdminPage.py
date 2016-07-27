########################################
# Filename: AdminPage.py
# Created by: DecodedLogic (18Jun16)
########################################

from lib.coginvasion.book_new.BookPage import BookPage

class AdminPage(BookPage):
    
    def __init__(self, book):
        BookPage.__init__(self, book, 'Admin Panel')
        
    def load(self):
        BookPage.load(self)
        icons = loader.loadModel('phase_4/models/gui/tfa_images.bam')
        self.icon = icons.find('**/hq-dialog-image')
        icons.detachNode()