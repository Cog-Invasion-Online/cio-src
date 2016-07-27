########################################
# Filename: ShtickerBook.py
# Created by: DecodedLogic (17Jun16)
# HAPPY BIRTHDAY COG INVASION ONLINE!!!
#         2 YEAR ANNIVERSARY
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.StateData import StateData

from direct.gui.DirectGui import DirectButton
from direct.gui.DirectGui import DGG, DirectFrame

from panda3d.core import TextNode

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.book_new.MapPage import MapPage
from lib.coginvasion.book_new.OptionsPage import OptionsPage
from lib.coginvasion.book_new.DistrictsPage import DistrictsPage
from lib.coginvasion.book_new.AdminPage import AdminPage
from lib.coginvasion.hood import ZoneUtil

class ShtickerBook(DirectFrame, StateData):
    notify = directNotify.newCategory('ShtickerBook')
    
    def __init__(self, doneEvent):
        DirectFrame.__init__(self, sortOrder = DGG.BACKGROUND_SORT_INDEX)
        StateData.__init__(self, doneEvent)
        self.initialiseoptions(ShtickerBook)

        # Pages that are registered to be used.
        self.pages = []
        
        # The page buttons
        self.pageBtns = []
        
        # The page that we're currently looking at.
        self.currentPage = None
        
        # Sound effects that are to be loaded.
        self.bookOpenSfx = None
        self.bookCloseSfx = None
        self.pageTurnSfx = None
        
        # The physical GUI element variables.
        self.nextPageBtn = None
        self.prevPageBtn = None
        
        # The sequence node with all the images we'll be using.
        self.bookElements = None
        
        # This is the frame that all the tab buttons are
        # reparented to.
        self.tabButtonFrame = None
        
        self.hide()
        
    def registerPage(self, page):
        # Only add the page if we pass the restriction.
        if not len(page.getRestriction()) or base.localAvatar.getAdminToken() in page.getRestriction():
            page.load()
            self.pages.append(page)
            
    def setCurrentPage(self, page):
        if self.currentPage and self.currentPage != page:
            self.currentPage.exit()
            self.pageTurnSfx.play()
        self.currentPage = page
        self.currentPage.enter()
        self.adjustPageButtons()
        
    def changePage(self, direction):
        pIndex = self.pages.index(self.currentPage)
        if direction == 0:
            # We're heading right down the list.
            if pIndex + 1 < len(self.pages):
                self.setCurrentPage(self.pages[pIndex + 1])
        elif direction == 1:
            # We're heading left down the list.
            if pIndex - 1 >= 0:
                self.setCurrentPage(self.pages[pIndex - 1])
            
    def getPages(self):
        return self.pages
    
    def adjustPageButtons(self):        
        if not self.prevPageBtn:
            button = self.bookElements.find('**/arrow_button')
            button_dn = self.bookElements.find('**/arrow_down')
            button_rlvr = self.bookElements.find('**/arrow_rollover')
            
            self.prevPageBtn = DirectButton(parent = self, geom = (button, button_dn, button_rlvr), 
                relief = None, pos = (-0.83, 0, -0.655), scale = (-0.1, 0.1, 0.1), command = self.changePage, 
            extraArgs = [1])
            
            self.nextPageBtn = DirectButton(parent = self, geom = (button, button_dn, button_rlvr),
                relief = None, pos = (0.83, 0, -0.655), scale = (0.1, 0.1, 0.1), command = self.changePage,
            extraArgs = [0])
        
        pIndex = self.pages.index(self.currentPage)
        if pIndex - 1 < 0:
            self.prevPageBtn.hide()
            self.ignore('arrow_left-up')
        else:
            self.prevPageBtn.show()
            self.acceptOnce('arrow_left-up', self.changePage, [1])
            
        if pIndex + 1 == len(self.pages):
            self.nextPageBtn.hide()
            self.ignore('arrow_right-up')
        else:
            self.nextPageBtn.show()
            self.acceptOnce('arrow_right-up', self.changePage, [0])
            
    def loadPageTabButtons(self):
        for i in xrange(len(self.pages)):
            page = self.pages[i]
            btnOffset = i * 0.07
            pageBtn = DirectButton(parent = self.tabButtonFrame, relief = DGG.RAISED, 
                frameSize = (-0.575, 0.575, -0.575, 0.575), 
                borderWidth = (0.05, 0.05), 
                text=('', '', page.getName(), ''),
                text_align = TextNode.ALeft, 
                text_pos = (1, -0.2), 
                text_scale = 0.75, 
                text_fg = (1, 1, 1, 1), 
                text_shadow = (0, 0, 0, 1), 
                geom = page.getIcon(),
                image = page.getIcon(),
                image_scale = page.getIconScale(), 
                geom_scale = page.getIconScale(), 
                geom_color = page.getIconColor(), 
                pos=(0, 0, -btnOffset), 
            scale=0.06, command = self.setCurrentPage, extraArgs = [page])
            self.pageBtns.append(pageBtn)
            
        
    def enter(self, lastBookPage):
        if self.isEntered == 0:
            
            if lastBookPage is None:
                lastBookPage = self.pages[2]
            else:
                self.currentPage = self.pages[lastBookPage]
                lastBookPage = self.currentPage
                
            # Hide the environment and change the background
            # color to blue.
            render.hide()
            base.setBackgroundColor(0.05, 0.15, 0.4)
            
            # Create the main book image (frame) and play the
            # open sfx.
            self.tabButtonFrame = DirectFrame(parent = self, relief = None, pos = (0.93, 1, 0.575), scale = 1.25)
            self.loadPageTabButtons()
            self.bookOpenSfx.play()
            
            # Let's enter the current page.
            self.setCurrentPage(lastBookPage)
            self.show()
        StateData.enter(self)
            
    def exit(self):        
        if self.isEntered:
            if self.currentPage:
                self.currentPage.exit()
            
            # Show the environment and return the background color.
            base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
            render.show()
            
            # Let's hide our stuff.
            self.hide()
            
            # Play the exit sfx.
            self.bookCloseSfx.play()
            
            # Let's ignore the page buttons.
            self.ignore('arrow_right-up')
            self.ignore('arrow_left-up')
        StateData.exit(self)
        
    def load(self):
        StateData.load(self)
        
        # Load up the sfx
        self.bookOpenSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_open.ogg')
        self.bookCloseSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_delete.ogg')
        self.pageTurnSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_stickerbook_turn.ogg')
        
        # Load up the sequence node with all the images we need.
        self.bookElements = loader.loadModel('phase_3.5/models/gui/stickerbook_gui.bam')
        
        # Let's load up the main frame.
        self['image'] = self.bookElements.find('**/big_book')
        self['image_scale'] = (2, 1, 1.5)
        self['scale'] = (2, 1, 1.5)
        self.resetFrameSize()
        
        # Let's register our pages.
        self.registerPage(OptionsPage(self))
        self.registerPage(DistrictsPage(self))
        self.registerPage(MapPage(self))
        self.registerPage(AdminPage(self))
        
    def unload(self):
        StateData.unload(self)
        
        # Destroy our page buttons.
        for tab in self.pageBtns:
            tab.destroy()
            self.pageBtns.remove(tab)
        
        # Destroy our pages.
        for page in self.pages:
            page.unload()
            self.pages.remove(page)
        
        # Destroy the main book image and the page buttons.
        self.nextPageBtn.destroy()
        self.prevPageBtn.destroy()
        self.tabButtonFrame.destroy()
        self.destroy()
        
        # Let's get rid of our elements.
        self.bookElements.removeNode()
        
        # Let's get rid of our sfx.
        self.bookOpenSfx.stop()
        self.bookCloseSfx.stop()
        self.pageTurnSfx.stop()
        
        del self.bookOpenSfx
        del self.bookCloseSfx
        del self.pageTurnSfx
        del self.bookElements
        del self.nextPageBtn
        del self.prevPageBtn
        del self.tabButtonFrame
        del self.currentPage
        del self.pageBtns
        del self.pages
        
    def finished(self, zone, shardId = None):
        if base.localAvatar.isDead() and type(zone) == type(1):
            return
        doneStatus = {}
        if zone in [CIGlobals.ToontownCentralId, CIGlobals.MinigameAreaId,
        CIGlobals.TheBrrrghId, CIGlobals.DonaldsDreamlandId, CIGlobals.MinniesMelodylandId,
        CIGlobals.DaisyGardensId, CIGlobals.DonaldsDockId]:
            doneStatus["mode"] = 'teleport'
            doneStatus["zoneId"] = zone
            doneStatus["hoodId"] = ZoneUtil.getHoodId(zone)
            doneStatus["where"] = ZoneUtil.getWhereName(zone)
            doneStatus["how"] = 'teleportIn'
            doneStatus["avId"] = base.localAvatar.doId
            doneStatus["shardId"] = None
            doneStatus["loader"] = ZoneUtil.getLoaderName(zone)
        else:
            doneStatus["mode"] = zone
            if zone == "switchShard":
                doneStatus["shardId"] = shardId
        self.doneStatus = doneStatus
        messenger.send(self.doneEvent)
        
    def getBookElements(self):
        return self.bookElements
    
    def getCurrentPage(self):
        return self.currentPage