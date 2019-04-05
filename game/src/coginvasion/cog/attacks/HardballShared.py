from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_HARDBALL

Name = "Hardball"
ID = ATTACK_HARDBALL
StateThrow = 1
ModelScale = 10.0
ModelPath = "phase_5/models/props/baseball.bam"
ModelOrigin = Point3(0.0, 0.0, -0.5)

ThrowSoundPath = "phase_5/audio/sfx/SA_hardball_throw_only.ogg"
ThrowAfterTime = 2.95
AttackDuration = 4.0
ThrowPower = 100.0

WantLight = False