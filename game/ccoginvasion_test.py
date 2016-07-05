from panda3d.core import *
loadPrcFile('config/config_client.prc')

from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()

import ccoginvasion

ccoginvasion.CTMusicData.initialize_chunk_data()
ccoginvasion.CTMusicManager.spawn_load_tournament_music_task()

mgr = None

def poll_loaded(task):
    global mgr
    if ccoginvasion.CTMusicManager.is_loaded():
        mgr = ccoginvasion.CTMusicManager()
        mgr.start_music()
        
        base.accept('control-5', mgr.set_clip_request, ["5050_orchestra"])
        base.accept('5', mgr.set_clip_request, ["5050_base"])
        base.accept('control-l', mgr.set_clip_request, ["located_orchestra"])
        base.accept('l', mgr.set_clip_request, ["located_base"])
        base.accept('control-r', mgr.set_clip_request, ["running_away_orchestra"])
        base.accept('r', mgr.set_clip_request, ["running_away_base"])
        base.accept('control-g', mgr.set_clip_request, ["getting_worse_orchestra"])
        base.accept('g', mgr.set_clip_request, ["getting_worse_base"])
        base.accept('control-i', mgr.set_clip_request, ["intro_orchestra"])
        base.accept('i', mgr.set_clip_request, ["intro_base"])
        base.accept('shift-s', mgr.set_clip_request, ['static_cooldown'])
        base.accept('a', mgr.set_clip_request, ["arresting_you"])
        base.accept('h', mgr.set_clip_request, ["high_speed_cooldown_base"])
        base.accept('control-h', mgr.set_clip_request, ["high_speed_cooldown_orchestra"])
        base.accept('v', mgr.set_clip_request, ["very_low_speed_cooldown"])
        base.accept('c', mgr.set_clip_request, ["low_speed_cooldown_1"])
        base.accept('control-c', mgr.set_clip_request, ["low_speed_cooldown_2"])
        base.accept('shift-a', mgr.set_clip_request, ["approaching_base"])
        base.accept('shift-control-a', mgr.set_clip_request, ["approaching_orchestra"])
        base.accept('control-a', mgr.set_clip_request, ["arrested_1"])
        base.accept('e', mgr.set_clip_request, ["evaded_1"])
        base.accept('f', mgr.set_clip_request, ["intro_orchestra_from_located"])
        
        return task.done
    return task.cont

base.taskMgr.add(poll_loaded, "poll_loaded")

PStatClient.connect()

base.run()
