# Priorities:
MP_low = 0
MP_normal = 1
MP_high = 2
MP_urgent = 3


def updateMarginVisibles():
    messenger.send('MarginVisible-update')
