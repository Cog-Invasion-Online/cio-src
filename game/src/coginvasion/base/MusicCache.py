from panda3d.core import VirtualFileSystem

# song name : AudioSound object
Cache = {}

def precacheMusicDir(musicDir, extension = "ogg"):
    global Cache
    
    vfs = VirtualFileSystem.getGlobalPtr()
    songList = vfs.scanDirectory(musicDir)
    if not songList:
        print "No music in {0}".format(musicDir)
        return
    for vFile in songList.getFiles():
        fn = vFile.getFilename()
        if fn.getExtension() == extension:
            Cache[fn.getBasenameWoExtension()] = fn.getFullpath()

def precacheMusic(extension = "ogg"):
    phases = [3, 3.5, 4, 5, 5.5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    for phaseNum in phases:
        phase = "phase_" + str(phaseNum)
        musicDir = phase + "/audio/bgm"
        precacheMusicDir(musicDir, extension)

def findSong(songName):
    path = Cache.get(songName, None)
    if not path:
        return None

    song = base.loadMusic(path)
    return song
