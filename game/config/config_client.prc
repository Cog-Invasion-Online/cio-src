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
notify-level info
notify-level-egg2pg warning
notift-level-bspfile debug
notify-level-pgraph warning
notify-level-loader warning
notify-level-gobj warning
notify-level-bspmaterial warning
notify-level-display warning
notify-level-raytrace warning
notify-level-glgsg warning
notify-level-gsg warning
notify-level-bullet error
notify-level-linmath error
notify-timestamp #f
default-directnotify-level info

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
connect-method net

# Resync clocks every minute.
# This may need to be shrinked even further.
time-manager-freq 60

# 150-300 ms latency
simulated-latency 1
simulated-latency-min 0.15
simulated-latency-max 0.3

# Performance...
hardware-animated-vertices #t
sync-video #f
smooth-lag 0.2
smooth-prediction-lag 0.0
basic-shaders-only #f
framebuffer-multisample 0
framebuffer-stencil 0
support-stencil 0
framebuffer-srgb 0
framebuffer-alpha 1
default-texture-color-space sRGB
textures-srgb 1
multisamples 0
garbage-collect-states-rate 0.5

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
want-playground-gags #f
gsg-want-hlsounds #f
explosion-hlsounds #f

hdr-min-avglum 3.0
hdr-percent-bright-pixels 2.0
hdr-percent-target 60.0
hdr-debug-histogram #f

want-pssm 1
pssm-debug-cascades 0
pssm-splits 3
pssm-size 2048
pssm-shadow-depth-bias 0.0001
pssm-max-distance 200
pssm-sun-distance 400
pssm-normal-offset-scale 3.0
pssm-softness-factor 2.0
pssm-cache-shaders 1
pssm-ambient-light-identifier 0.2 0.2 0.2
pssm-ambient-light-min 0.2 0.2 0.2
pssm-ambient-light-scale 1.0
shadow-depth-bits 32
stencil-bits 0

# Time averaged lighting in BSP levels to reduce popping
light-average 1
light-lerp-speed 5.0

ctmusic-numsongs 1

want-pstats 0
pstats-gpu-timing 0
pstats-host 127.0.0.1
pstats-view-on-server 1

preload-textures 0
preload-simple-textures 1
texture-compression 1
allow-incomplete-render 1
allow-async-bind 1
restore-initial-pose 0

flatten-collision-nodes 1

egg-load-old-curves 0

show-buffers #f

texture-minfilter mipmap
texture-magfilter linear
text-minfilter linear
text-magfilter linear
gl-coordinate-system default
gl-force-fbo-color 0
garbage-collect-states 0
allow-flatten-color 1
gl-debug 0
gl-finish 0
gl-debug-synchronous 1
gl-debug-abort-level fatal
gl-depth-zero-to-one 0
gl-force-depth-stencil 0
glsl-preprocess 1

text-flatten 1
text-dynamic-merge 1

interpolate-frames 1

#threading-model Cull/Draw # experimental
assert-abort 0

textures-power-2 none

precache-assets 1

mat_rimlight 1
mat_envmaps 1
mat_phong 1

r_ambientboost 1
r_ambientmin 0.3
r_ambientfraction 0.1
r_ambientfactor 5.0
