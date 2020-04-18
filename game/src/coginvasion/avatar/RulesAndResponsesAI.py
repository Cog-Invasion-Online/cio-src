class RulesAndResponsesAI:
    
    @staticmethod
    def setRule(ruleName, avs):
        if isinstance(avs, list):
            for av in avs:
                av.handleRule(ruleName)
        else:
            avs.handleRule(ruleName)
            
    @staticmethod
    def setGlobalRule(ruleName):
        messenger.send('globalrule', [ruleName])
