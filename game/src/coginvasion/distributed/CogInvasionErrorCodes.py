"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CogInvasionErrorCodes.py
@author Brian Lach
@date January 25, 2015

"""

EC_MULTIPLE_LOGINS = 110
EC_BAD_TOKEN = 111
EC_INVALID_ACCOUNT = 112
EC_NON_EXISTENT_AV = 113
EC_OCCUPIED_SLOT_CREATION_ATTEMPT = 114
EC_EJECT_VERSION = 124
EC_EJECT_DC = 125

UnknownErrorMsg = "An unexpected problem has occured. (Error code %s) Your connection has been lost, but you should be able to connect again and go right back into the game."

ErrorCode2ErrorMsg = {
	EC_MULTIPLE_LOGINS: "You have been disconnected because someone has logged into your account on another computer.",
	EC_BAD_TOKEN: "You have been disconnected because your login token is invalid.",
	EC_INVALID_ACCOUNT: "You have been disconnected because your account is invalid.",
	EC_NON_EXISTENT_AV: "You have been disconnected because you tried to do something to a non-existent Toon.",
	EC_OCCUPIED_SLOT_CREATION_ATTEMPT: "You have been disconnected because you tried to create a Toon on an occupied slot.",
    EC_EJECT_VERSION: "You have been disconnected because your game files are out of date. Please run the game from the launcher to download the latest files.",
    EC_EJECT_DC: "You have been disconnected because your game files are out of date. Please run the game from the launcher to download the latest files."
}
