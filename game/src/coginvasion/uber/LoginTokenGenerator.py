"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LoginTokenGenerator.py
@author Brian Lach
@date December 8, 2014

"""

import random, string
import LoginToken

def generateLoginToken(ip):
	# The size of the token can be anywhere from 30 to 60 characters.
	size = random.randint(30, 60)
	chars = string.ascii_uppercase + string.digits
	token = ''.join(random.choice(chars) for _ in range(size))
	obj = LoginToken.LoginToken(token, ip)
	return obj
