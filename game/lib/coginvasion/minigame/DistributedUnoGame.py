"""

  Filename: DistributedUnoGame.py
  Created by: blach (15Oct14)

"""

import DistributedMinigame
import UnoGameGlobals as UGG
import UnoGameCardDeck
from lib.coginvasion.globals import CIGlobals
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from lib.coginvasion.holiday.HolidayManager import HolidayType

class DistributedUnoGame(DistributedMinigame.DistributedMinigame):

    def __init__(self, cr):
        try:
            self.DistributedUnoGame_initialized
            return
        except:
            self.DistributedUnoGame_initialized = 1
        DistributedMinigame.DistributedMinigame.__init__(self, cr)
        self.cardDeck = UnoGameCardDeck.UnoGameCardDeck(self)
        self.numCards = 0 # The number of cards currently in our deck.
        self.hasCalledZero = False
        self.cards = []
        self.drawBtn = None
        self.callBtn = None
        self.playByPlay = None
        self.cardToFollow = None
        self.newColorDialog = None
        self.newColorTitle = None
        self.newColorRed = None
        self.newColorBlue = None
        self.newColorGreen = None
        self.newColorYellow = None
        self.lastCardPlaced = None
        self.unoCalled = False
        self.table = None
        self.background = None
        return

    def deleteWorld(self):
        #if self.background:
        #    self.background.removeNode()
        #    self.background = None
        #if self.table:
        #    self.table.removeNode()
        #    self.table = None
        if self.background:
            self.background.destroy()
            self.background = None
        camera.reparentTo(render)
        camera.setPos(0, 0, 0)
        camera.setHpr(0, 0, 0)

    def load(self):
        #self.background = loader.loadModel("phase_6/models/golf/golf_outdoor_zone.bam")
        #self.background.setPos(-60, -20, 0)
        #self.background.reparentTo(render)
        #self.table = loader.loadModel("phase_6/models/golf/game_table.bam")
        #self.table.setPos(91.7, 5.68547, 1.2)
        #self.table.setHpr(30, 1.45363, 0)
        #self.table.reparentTo(render)
        self.background = OnscreenImage(image = "phase_4/maps/uno_bg.png")
        self.background.setSx(1.93)
        self.background.setBin("background", 10)
        self.setMinigameMusic("phase_4/audio/bgm/minigame_race.mid")
        self.setDescription("Play the Uno card game against the other players and win to get a big prize!")
        self.setWinnerPrize(135)
        self.setLoserPrize(10)
        #camera.reparentTo(self.table)
        #camera.setP(-90)
        #camera.setY(-0.9)
        #camera.setZ(22)
        DistributedMinigame.DistributedMinigame.load(self)

    def enterPlay(self):
        DistributedMinigame.DistributedMinigame.enterPlay(self)
        self.createGui()

    def enterGameOver(self, winner=0, winnerDoId=0, allPrize = 0):
        self.cardDeck.disableAll()
        self.drawBtn['state'] = DGG.DISABLED
        self.callBtn['state'] = DGG.DISABLED
        DistributedMinigame.DistributedMinigame.enterGameOver(self, winner, winnerDoId, allPrize)

    def createGui(self):
        self.deleteGui()
        uno_gui = loader.loadModel("phase_4/models/minigames/mg_uno_call_btn_gui.egg")
        gui = loader.loadModel("phase_3/models/gui/quit_button.bam")
        self.drawBtn = DirectButton(text="Draw", relief=None, text_scale = 0.055, scale=1, parent=base.a2dBottomLeft,
                                geom=(gui.find('**/QuitBtn_UP'),
                                    gui.find('**/QuitBtn_DN'),
                                    gui.find('**/QuitBtn_RLVR'),
                                    gui.find('**/QuitBtn_UP')),
                                pos=(0.18, 0, 0.1), geom_scale = (0.6, 1.0, 1.0), command=self.d_requestNewCard)
        self.callBtn = DirectButton(geom=(uno_gui.find('**/mg_uno_call_btn-idle'),
                                uno_gui.find('**/mg_uno_call_btn-down'),
                                uno_gui.find('**/mg_uno_call_btn-rlvr'),
                                uno_gui.find('**/mg_uno_call_btn-disabled')),
                        relief=None,
                        scale=0.3,
                        parent=base.a2dBottomLeft,
                        pos=(0.18, 0, 0.305),
                        command=self.d_callUno)
        self.callBtn['state'] = DGG.DISABLED
        self.playByPlay = OnscreenText(text="", font=CIGlobals.getMickeyFont(), scale=0.1,
                                fg=(0, 0.8, 0, 1), pos=(0, 0.85), wordwrap=15.0)
        self.cardDeck.generate()
        self.createTimer()
        gui.removeNode()
        del gui

    def d_callUno(self):
        self.callBtn['state'] = DGG.DISABLED
        self.unoCalled = True
        self.localAv.b_setChat(CIGlobals.UnoCall)
        self.sendUpdate("callUno", [])

    def deleteGui(self):
        if self.drawBtn:
            self.drawBtn.destroy(); self.drawBtn = None
        if self.callBtn:
            self.callBtn.destroy(); self.callBtn = None
        if self.playByPlay:
            self.playByPlay.destroy(); self.playByPlay = None
        self.cardDeck.disable()
        self.deleteTimer()

    def setPlayerTurn(self, doId):
        if self.numCards == 1:
            if not self.unoCalled:
                self.callBtn['state'] = DGG.NORMAL
        elif self.numCards == 0 and not self.hasCalledZero:
            self.hasCalledZero = True
            self.d_noCards()
        else:
            self.callBtn['state'] = DGG.DISABLED
        if self.localAvId == doId:
            # It's our turn!
            self.setPlayByPlay(UGG.EVENT_NEW_TURN % "your")
            self.cardDeck.enableAll(self.cardToFollow)
            self.drawBtn['state'] = DGG.NORMAL
        else:
            self.cardDeck.disableAll()
            self.drawBtn['state'] = DGG.DISABLED
        self.cardDeck.updateCardToFollowGui()

    def requestNewCardColor(self):
        self.createNewColorGui()

    def d_noCards(self):
        self.sendUpdate("noCards", [])

    def createNewColorGui(self):
        gui = loader.loadModel("phase_4/models/minigames/mg_uno_game_cards.egg")
        self.newColorDialog = OnscreenImage(image=DGG.getDefaultDialogGeom(), scale=(1.5, 1, 1))
        self.newColorTitle = DirectLabel(text="Choose A Card Color", text_scale=0.12, text_pos=(0, 0.3), relief=None)
        self.newColorBlue = DirectButton(image=gui.find('**/mg_uno_numcards_blue_blank'), relief=None,
                                scale=(0.2, 0.35, 0.35), pos=(-0.325, 0, -0.075), command=self.d_takeNewCardColor,
                                extraArgs=[str(UGG.CARD_BLUE)])
        self.newColorRed = DirectButton(image=gui.find('**/mg_uno_numcards_red_blank'), relief=None,
                                scale=(0.2, 0.35, 0.35), pos=(-0.125, 0, -0.075), command=self.d_takeNewCardColor,
                                extraArgs=[str(UGG.CARD_RED)])
        self.newColorGreen = DirectButton(image=gui.find('**/mg_uno_numcards_green_blank'), relief=None,
                                scale=(0.2, 0.35, 0.35), pos=(0.075, 0, -0.075), command=self.d_takeNewCardColor,
                                extraArgs=[str(UGG.CARD_GREEN)])
        self.newColorYellow = DirectButton(image=gui.find('**/mg_uno_numcards_yellow_blank'), relief=None,
                                scale=(0.2, 0.35, 0.35), pos=(0.275, 0, -0.075), command=self.d_takeNewCardColor,
                                extraArgs=[str(UGG.CARD_YELLOW)])

    def deleteNewColorGui(self):
        if self.newColorDialog:
            self.newColorDialog.destroy(); self.newColorDialog = None
        if self.newColorTitle:
            self.newColorTitle.destroy(); self.newColorTitle = None
        if self.newColorBlue:
            self.newColorBlue.destroy(); self.newColorBlue = None
        if self.newColorRed:
            self.newColorRed.destroy(); self.newColorRed = None
        if self.newColorGreen:
            self.newColorGreen.destroy(); self.newColorGreen = None
        if self.newColorYellow:
            self.newColorYellow.destroy(); self.newColorYellow = None

    def deleteAllCards(self):
        for card in self.cards:
            card.removeNode(); del card

    def d_takeNewCardColor(self, id):
        self.deleteNewColorGui()
        self.sendUpdate("takeNewCardColor", [self.lastCardPlaced, id])

    def setNewCardColor(self, id):
        if self.cardToFollow != None:
            self.cardToFollow += id

    def placeCard(self, doId, cardId):
        cards = loader.loadModel("phase_4/models/minigames/mg_uno_game_cards.egg")
        card = cards.find('**/' + UGG.cardId2cardTex[cardId])
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            holidayTexture = loader.loadTexture('winter/maps/uno/%s.png' % (card.getName()))
            card.setTexture(holidayTexture, 1)
        card.setScale(0.4, 0.49, 0.49)
        card.reparentTo(aspect2d)
        self.cards.append(card)
        if self.localAvId != doId:
            LerpPosInterval(card,
                    duration=1.0,
                    pos=(0, 0, 0.1),
                    startPos=(-1.5, 0, 1.5),
                    blendType="easeOut").start()
        else:
            self.numCards -= 1
            LerpPosInterval(card,
                    duration=1.0,
                    pos=(0,0,0.1),
                    startPos=(0, 0, -1.5),
                    blendType="easeOut").start()
            LerpScaleInterval(card,
                    duration=1.0,
                    scale=(0.4, 0.49, 0.49),
                    startScale=(0.3, 0.3, 0.23),
                    blendType="easeOut").start()
            self.lastCardPlaced = cardId
        self.cardToFollow = cardId
        cards.removeNode()
        del cards

    def setPlayByPlay(self, pbp):
        if self.playByPlay:
            self.playByPlay.setText(pbp)

    def d_requestNewCard(self):
        """ Request a new card out of the deck from the AI. """
        self.sendUpdate("requestNewCard", [])

    def d_requestPlaceCard(self, id):
        self.sendUpdate("requestPlaceCard", [id])

    def takeNewCard(self, cardId):
        """ The AI sent us a new card, let's put in our deck. """
        self.cardDeck.drawCard(cardId)
        self.numCards += 1

    def d_wasDealed(self):
        """ Tell the AI that we have been dealed our cards. """
        self.sendUpdate("wasDealed", [])

    def announceGenerate(self):
        DistributedMinigame.DistributedMinigame.announceGenerate(self)
        # Preload cards so the game doesn't freeze at the beginning.
        cards = loader.loadModel('phase_4/models/minigames/mg_uno_game_cards.egg')
        cards.reparentTo(aspect2d)
        cards.removeNode()
        del cards
        self.load()

    def generate(self):
        base.localAvatar.disableChatInput()
        DistributedMinigame.DistributedMinigame.generate(self)

    def disable(self):
        DistributedMinigame.DistributedMinigame.disable(self)
        base.localAvatar.createChatInput()
        self.deleteWorld()
        self.deleteGui()
        self.deleteNewColorGui()
        self.deleteAllCards()
        self.cardDeck.delete()
        self.numCards = None
        self.cardToFollow = None
        self.lastCardPlaced = None
        self.unoCalled = None
        self.hasCalledZero = None
        return
