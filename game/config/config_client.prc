# Default window properties...
window-title Cog Invasion Online (Alpha II)
win-origin -1 -1
win-size 640 480
#win-fixed-size 1
load-display pandagl
aux-display pandagl

#clock-mode limited
#clock-frame-rate 10

# Logging...
notify-level warning
notify-level-egg2pg warning
notify-timestamp #f
default-directnotify-level warning

# Filenames...
cursor-filename resources/toonmono.cur
icon-filename resources/icon.ico

default-model-extension .egg

#model-cache-dir ./cache
model-cache-model #t
model-cache-textures #t

physics-debug #f

model-path .

# Audio...

# Woo-hoo!!!! Miles!!
audio-library-name p3openal_audio
#miles-audio-expand-mp3-threshold 10000000
#miles-audio-panda-threads #t
#audio-library-name p3openal_audio

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
vfs-mount resourcepack/phase_14 phase_14

# Server...
server-port 7032
server-address gameserver.coginvasion.com

# Performance...
hardware-animated-vertices #t
sync-video #f
smooth-lag 0.4
basic-shaders-only #f
framebuffer-multisample 0
framebuffer-stencil 0
support-stencil 0
framebuffer-srgb 0
multisamples 0
#garbage-collect-states-rate 0.5

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
want-gta-controls #f
show-minigame-dates #f
want-real-shadows #f
load-stuff #f
want-playground-gags #t
gsg-want-hlsounds #f
explosion-hlsounds #f

ctmusic-numsongs 1

want-pstats 0

allow-incomplete-render 0

egg-load-old-curves 0

show-buffers #f

texture-minfilter mipmap
texture-magfilter linear
text-minfilter linear
text-magfilter linear
gl-coordinate-system default
gl-force-fbo-color 0
garbage-collect-states 1
allow-flatten-color 1
gl-debug 0

text-flatten 1
text-dynamic-merge 1

interpolate-frames 1

threading-model App/Cull/Draw # experimental
assert-abort 0
