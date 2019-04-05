from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_BITE

Name = "Bite"
ID = ATTACK_BITE
StateThrow = 1
ModelPath = "phase_5/models/props/teeth-mod.bam"
ModelScale = 6.0
ModelAngles = Point3(0.0, 0.0, 180.0)

ThrowAfterTime = 2.95
AttackDuration = 4.0
ThrowPower = 100.0
WantLight = False
