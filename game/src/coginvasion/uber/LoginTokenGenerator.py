"""

  Filename: LoginTokenGenerator.py
  Created by: DuckyDuck1553 (08Dec14)

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
