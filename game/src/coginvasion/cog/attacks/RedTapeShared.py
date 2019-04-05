from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_RED_TAPE

Name = "Red Tape"
ID = ATTACK_RED_TAPE
StateThrow = 1
ModelPath = "phase_5/models/props/redtape.bam"
ModelScale = 1.0
ModelOrigin = Point3(0.35, 0.0, -0.5)
ModelAngles = Point3(0.0, 90.0, 0.0)

ThrowSoundPath = "phase_5/audio/sfx/SA_red_tape.ogg"
ThrowPower = 200.0
ThrowAfterTime = 2.95
AttackDuration = 4.0
