# Default window properties...
window-title Cog Invasion Online (Alpha)
win-origin -1 -1
win-size 640 480
#win-fixed-size 1
load-display pandagl
aux-display pandagl

#clock-mode limited
#clock-frame-rate 10

# Logging...
notify-level info
notify-timestamp #f
notify-level-pgraph warning
notify-level-loader warning
notify-level-gobj warning
notify-level-linmath info
default-directnotify-level info

# Filenames...
cursor-filename resources/toonmono.cur
icon-filename resources/icon.ico

default-model-extension .egg

model-cache-dir
model-cache-model #f
model-cache-textures #f

model-path .

# Audio...

# Woo-hoo!!!! Miles!!
audio-library-name p3miles_audio
miles-audio-expand-mp3-threshold 10000000
miles-audio-panda-threads #t

# Virtual file system...
vfs-mount resourcepack/phase_3 phase_3
vfs-mount resourcepack/phase_3.5 phase_3.5
vfs-mount resourcepack/phase_4 phase_4
vfs-mount resourcepack/phase_5 phase_5
vfs-mount resourcepack/phase_5.5 phase_5.5
vfs-mount resourcepack/phase_6 phase_6
vfs-mount resourcepack/phase_7 phase_7
vfs-mount resourcepack/phase_8 phase_8
vfs-mount resourcepack/phase_9 phase_9
vfs-mount resourcepack/phase_10 phase_10
vfs-mount resourcepack/phase_11 phase_11
vfs-mount resourcepack/phase_12 phase_12
vfs-mount resourcepack/phase_13 phase_13

# Server...
server-port 7032
server-address gameserver.coginvasion.com

# Performance...
hardware-animated-vertices #t
sync-video #f
smooth-lag 0.4
basic-shaders-only #f
framebuffer-multisample 1
multisamples 16

audio-dls-file resources/gm.dls

# Game content...
game-name Cog Invasion
want-weapons #t
want-pies #t
want-chat #t
want-sa-reactions #f
gag-start-key alt
gag-throw-key alt-up
want-firstperson-battle #f
chat-key t
want-WASD #t
want-gta-controls #t
show-minigame-dates #f
want-real-shadows #f
load-stuff #t
want-playground-gags #t

ctmusic-numsongs 1

want-pstats 0

egg-load-old-curves 0

#threading-model App/Cull/Draw

gl-finish #f
gl-force-no-error #t
gl-check-errors #f
gl-force-no-flush #t
gl-force-no-scissor #t