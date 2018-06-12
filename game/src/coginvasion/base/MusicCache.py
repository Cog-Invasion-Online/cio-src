from panda3d.core import VirtualFileSystem, Filename

# song name : AudioSound object
Cache = {}

def precacheMusic(extension = "ogg"):
    global Cache

    phases = [3, 3.5, 4, 5, 5.5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    vfs = VirtualFileSystem.getGlobalPtr()
    for phaseNum in phases:
        phase = "phase_" + str(phaseNum)
        musicDir = phase + "/audio/bgm"
        songList = vfs.scanDirectory(musicDir)
        if not songList:
            print "No music in phase {0}".format(phaseNum)
            continue
        for vFile in songList.getFiles():
            fn = vFile.getFilename()
            if fn.getExtension() == extension:
                Cache[fn.getBasenameWoExtension()] = fn.getFullpath()

    print Cache

def findSong(songName):
    path = Cache.get(songName, None)
    if not path:
        return None

    song = base.loadMusic(path)
    return song