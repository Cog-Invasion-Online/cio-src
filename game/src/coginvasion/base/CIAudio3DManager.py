"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIAudio3DManager.py
@author Brian Lach
@date June 20, 2018

"""

from panda3d.core import Vec3

from direct.task import Task
from direct.showbase.Audio3DManager import Audio3DManager

class CIAudio3DManager(Audio3DManager):
    """Fixes entries not being removed from the dictionary when a NodePath goes away."""

    def update(self, task=None):
        """
        Updates position of sounds in the 3D audio system. Will be called automatically
        in a task.
        """
        # Update the positions of all sounds based on the objects
        # to which they are attached

        # The audio manager is not active so do nothing
        if hasattr(self.audio_manager, "getActive"):
            if self.audio_manager.getActive()==0:
                return Task.cont

        for known_object, sounds in list(self.sound_dict.items()):
            node_path = known_object.getNodePath()
            if not node_path or node_path.isEmpty():
                # The node has been deleted.
                del self.sound_dict[known_object]
                continue

            pos = node_path.getPos(self.root)

            for sound in sounds:
                vel = self.getSoundVelocity(sound)
                sound.set3dAttributes(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2])

        # Update the position of the listener based on the object
        # to which it is attached
        if self.listener_target:
            pos = self.listener_target.getPos(self.root)
            forward = self.root.getRelativeVector(self.listener_target, Vec3.forward())
            up = self.root.getRelativeVector(self.listener_target, Vec3.up())
            vel = self.getListenerVelocity()
            self.audio_manager.audio3dSetListenerAttributes(pos[0], pos[1], pos[2], vel[0], vel[1], vel[2], forward[0], forward[1], forward[2], up[0], up[1], up[2])
        else:
            self.audio_manager.audio3dSetListenerAttributes(0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1)
        return Task.cont

