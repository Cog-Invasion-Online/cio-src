from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_MARKET_CRASH
from src.coginvasion.cog.attacks.GenericThrowShared import ThrowAfterTime, AttackDuration, PlayRate, ThrowPower, StateThrow

Name = "Market Crash"
ID = ATTACK_MARKET_CRASH
StateThrow = StateThrow
ModelPath = "phase_5/models/props/newspaper.bam"
ModelScale = 3.0
ModelAngles = Point3(90.0, 0.0, 270.0)
ModelOrigin = Point3(0.41, -0.06, -0.06)

ThrowAfterTime = ThrowAfterTime
AttackDuration = AttackDuration
ThrowPower = ThrowPower
PlayRate = PlayRate
