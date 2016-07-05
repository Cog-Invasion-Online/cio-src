print "Starting Cog Invasion Online."
import os
import sys
REQUIRED_ENVIRONMENT_VARS = ["ACCOUNT_NAME", "GAME_SERVER", "LOGIN_TOKEN", "GAME_VERSION"]
for VAR in REQUIRED_ENVIRONMENT_VARS:
    if not os.environ.get(VAR, None):
        print "Exiting: Some environment variables are not set."
        sys.exit()

from libcoginvasion import *

from encodings import hex_codec
from encodings import ascii
import lib.coginvasion.base.CIStartGlobal
