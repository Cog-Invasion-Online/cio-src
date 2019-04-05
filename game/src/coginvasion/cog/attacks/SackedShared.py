from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_SACKED

Name = "Sacked"
ID = ATTACK_SACKED
StateThrow = 1
ModelPath = "phase_5/models/props/sandbag-mod.bam"
ModelAngles = Point3(0.0, 90.0, 180.0)
ModelOrigin = Point3(0.0, -2.8, -0.3)

ThrowAfterTime = 2.95
AttackDuration = 4.0
ThrowPower = 100.0
