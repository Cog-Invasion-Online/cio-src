"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ButterflyGlobals.py
@author Brian Lach
@date December 28, 2017

"""

from panda3d.core import Point3

from src.coginvasion.globals import CIGlobals

SitTime = [1.0, 20.0]
Speed = 2

StateIdx2State = {0: 'off', 1: 'sit', 2: 'fly'}

Spots = {
    CIGlobals.ToontownCentralId: [
        Point3(-54.2873306274, -4.53878879547, 0.00864257663488),
        Point3(-17.1854743958, 24.9851093292, 0.00864257663488),
        Point3(11.2990150452, 24.2988739014, 0.00864257663488),
        Point3(37.0859107971, 35.0179519653, 0.00864257663488),
        Point3(51.3255119324, -25.0889587402, 0.00864257849753),
        Point3(30.3549499512, -48.7701835632, 0.00864258036017),
        Point3(-11.3033571243, -55.3707885742, 0.0082556353882),
        Point3(-21.7303085327, -29.6253452301, 0.00808911304921),
        Point3(-12.5859603882, -10.1374444962, 0.00808911304921),
        Point3(3.25078988075, -11.407541275, 0.00808911304921),
        Point3(14.0121564865, 7.01403141022, 0.00808911304921)
    ]
}