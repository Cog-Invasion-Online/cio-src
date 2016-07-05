"""

  Filename: UnoGameCardDeck.py
  Created by: blach (18Oct14)

"""

from direct.gui.DirectGui import DirectFrame, OnscreenImage, DirectButton
from direct.gui.DirectGui import DirectScrolledList, DGG
import UnoGameGlobals as UGG
from lib.coginvasion.holiday.HolidayManager import HolidayType

class UnoGameCardDeck(DirectFrame):

    def __init__(self, ug):
        DirectFrame.__init__(self, relief=None, sortOrder=50, parent=base.a2dBottomCenter)
        self.initialiseoptions(UnoGameCardDeck)
        self.container = DirectFrame(parent=self, relief=None)
        self.title = None
        self.cards = []
        self.cardBtns = []
        self.numCards = 0
        self.unoGame = ug
        self.deck = None
        self.cardToFollowGui = None
        self.holiday = base.cr.holidayManager.getHoliday()
        self.gui = None
        self.loadCards()
        return

    def loadCards(self):
        self.gui = loader.loadModel("phase_4/models/minigames/mg_uno_game_cards.egg")
        if self.holiday == HolidayType.CHRISTMAS:
            cards = self.gui.find('**/mg_uno_numcards_green_7').getParent().getChildren()
            for child in cards:
                child.setTexture(loader.loadTexture('winter/maps/uno/%s.png' % (child.getName())), 1)

    def updateCardToFollowGui(self):
        self.deleteCardToFollowGui()
        if self.unoGame.cardToFollow[-2:] == str(UGG.CARD_BLUE):
            self.cardToFollowGui = OnscreenImage(image = self.getCard('mg_uno_numcards_blue_blank'),
                parent = base.a2dRightCenter)
        elif self.unoGame.cardToFollow[-2:] == str(UGG.CARD_RED):
            self.cardToFollowGui = OnscreenImage(image = self.getCard('mg_uno_numcards_red_blank'),
                parent = base.a2dRightCenter)
        elif self.unoGame.cardToFollow[-2:] == str(UGG.CARD_GREEN):
            self.cardToFollowGui = OnscreenImage(image = self.getCard('mg_uno_numcards_green_blank'),
                parent = base.a2dRightCenter)
        elif self.unoGame.cardToFollow[-2:] == str(UGG.CARD_YELLOW):
            self.cardToFollowGui = OnscreenImage(image = self.getCard('mg_uno_numcards_yellow_blank'),
                parent = base.a2dRightCenter)
            
        if self.cardToFollowGui:
            self.cardToFollowGui.setScale(0.25, 0.3, 0.3)
            self.cardToFollowGui.setPos(-0.175, 0, -0.75)

    def deleteCardToFollowGui(self):
        if self.cardToFollowGui:
            self.cardToFollowGui.destroy()
            self.cardToFollowGui = None

    def getCard(self, cardType):
        cards = loader.loadModel("phase_4/models/minigames/mg_uno_game_cards.egg")
        card = cards.find('**/' + cardType)
        if self.holiday == HolidayType.CHRISTMAS:
            holidayTexture = loader.loadTexture('winter/maps/uno/%s.png' % (card.getName()))
            card.setTexture(holidayTexture, 1)
        return card

    def generate(self):
        self.container["image"] = "phase_4/maps/mg_uno_card_deck.png"
        self.container.setTransparency(True)
        self.container.setZ(-0.456)
        self.container.setSx(2)
        self.container.setSz(1)
        gui = loader.loadModel("phase_3.5/models/gui/friendslist_gui.bam")
        numItemsVisible = 5
        itemHeight = -0.25
        self.deck = DirectScrolledList(itemFrame_relief = DGG.SUNKEN,
            decButton_pos= (0.35, 0, -0.02),
            decButton_geom=(gui.find('**/Horiz_Arrow_UP'),
                            gui.find('**/Horiz_Arrow_DN'),
                            gui.find('**/Horiz_Arrow_Rllvr'),
                            gui.find('**/Horiz_Arrow_UP')),
            decButton_relief = None,
            decButton_hpr=(0, 0, 90),
            incButton_pos= (0.35, 0, 1.95),
            incButton_geom=(gui.find('**/Horiz_Arrow_UP'),
                            gui.find('**/Horiz_Arrow_DN'),
                            gui.find('**/Horiz_Arrow_Rllvr'),
                            gui.find('**/Horiz_Arrow_UP')),
            incButton_hpr=(0, 0, -90),
            incButton_relief = None,
            pos = (-0.936, 0, -0.41),
            hpr = (0, 0, 90),
            scale = 0.97,
            numItemsVisible = numItemsVisible,
            forceHeight = itemHeight,
            itemFrame_frameSize = (-0.2, 0.2, -0.37, 1.5),
            itemFrame_pos = (0.35, 0, 0.4),
            itemFrame_borderWidth=(0.02, 0.02),
        )

    def disable(self):
        if self.deck:
            self.deck.destroy(); self.deck = None
        for btn in self.cardBtns:
            btn.destroy(); del btn
        self.deleteCardToFollowGui()
        return

    def delete(self):
        DirectFrame.destroy(self)
        self.disable()
        self.gui.removeNode()
        self.gui = None
        self.cards = None
        self.title = None
        self.container = None
        self.cardBtns = None
        self.numCards = None
        self.unoGame = None
        self.deck = None
        return

    def drawCard(self, id):
        card = self.getCard(UGG.cardId2cardTex[id])
        card.setScale(0.225, 0.3, 0.3)
        card.setR(-90)
        cardBtn = DirectButton(geom=card, relief=None, scale=(0.3, 0.3, 0.23), command=self.placeCard)
        cardBtn.setPythonTag('id', id)
        cardBtn['extraArgs'] = [id, cardBtn]
        cardBtn['state'] = DGG.DISABLED
        if not self.deck:
            self.generate()
        self.deck.addItem(cardBtn)
        self.cardBtns.append(cardBtn)
        self.enableAll(self.unoGame.cardToFollow)
        # Scroll to the card we just added to the deck.
        self.deck.scrollTo(len(self.cardBtns))
        card.removeNode()
        del card

    def enableAll(self, cardToFollow=None):
        for btn in self.cardBtns:
            if cardToFollow != None:
                if (cardToFollow == btn.getPythonTag('id') or cardToFollow[:2] == btn.getPythonTag('id')[:2] or
                        cardToFollow[-2:] == btn.getPythonTag('id')[-2:] or btn.getPythonTag('id') == str(UGG.CARD_WILD) or
                        btn.getPythonTag('id') == str(UGG.CARD_WILD_DRAW_FOUR)):
                    btn['state'] = DGG.NORMAL
                else:
                    btn['state'] = DGG.DISABLED
            else:
                btn['state'] = DGG.NORMAL

    def disableAll(self):
        for btn in self.cardBtns:
            btn['state'] = DGG.DISABLED

    def placeCard(self, id, btn):
        self.deck.removeItem(btn)
        self.cardBtns.remove(btn)
        self.disableAll()
        self.unoGame.d_requestPlaceCard(id)
