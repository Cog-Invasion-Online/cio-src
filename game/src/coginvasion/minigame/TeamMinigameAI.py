# Filename: TeamMinigameAI.py
# Created by:  blach (30Apr16)

from TeamMinigame import TEAM1, TEAM2

class TeamMinigameAI:
    """An abstract class for any team based minigame (AI/server side)"""

    def __init__(self):
        # This keeps track of what players are on what team. They are lists of doIds.
        self.playerListByTeam = {TEAM2: [], TEAM1: []}
        self.scoreByTeam = {TEAM1: 0, TEAM2: 0}
        self.winnerTeam = None

    def choseTeam(self, team, avId = None, sendAcceptedMsg = True):
        # A player chose the team they want to be on!
        if avId is None:
            avId = self.air.getAvatarIdFromSender()
        numOnRed = len(self.playerListByTeam[TEAM2])
        numOnBlue = len(self.playerListByTeam[TEAM1])
        if team == TEAM2 and numOnRed > numOnBlue or team == TEAM1 and numOnBlue > numOnRed:
            # Wait a minute, this team is full. Tell the client.
            self.sendUpdateToAvatarId(avId, 'teamFull', [])
            return 0
        else:
            # This team is open, let's accept them onto the team they chose!
            self.playerListByTeam[team].append(avId)
            self.sendUpdate('incrementTeamPlayers', [team])
            if sendAcceptedMsg:
                self.sendUpdateToAvatarId(avId, 'acceptedIntoTeam', [])
            self.sendUpdate('setTeamOfPlayer', [avId, team])
            return 1

    def cleanup(self):
        del self.playerListByTeam
        del self.scoreByTeam
        del self.winnerTeam
