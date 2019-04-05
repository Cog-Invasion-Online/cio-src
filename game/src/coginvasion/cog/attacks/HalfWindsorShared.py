from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_HALF_WINDSOR

Name = "Half Windsor"
ID = ATTACK_HALF_WINDSOR
StateThrow = 1
ModelPath = "phase_5/models/props/half-windsor.bam"
ModelScale = 6.0
ModelAngles = Point3(90.0, 0.0, 90.0)
ModelOrigin = Point3(0.0, -1.6, -1.0)

ThrowAfterTime = 2.95
AttackDuration = 4.0
ThrowPower = 100.0
ThrowSoundPath = "phase_5/audio/sfx/SA_powertie_throw.ogg"
WantLight = False
