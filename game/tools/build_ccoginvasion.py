import subprocess
import argparse
import sys
import os

if not os.path.isdir("built\\obj"):
    os.makedirs("built\\obj")

panda3d_dir = '..\\..\\Panda3D-CI'

def run_command(cmd):
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
    ret = p.wait()

    if ret != 0:
        print
        print "The following command return a non-zero value (%d): %s" % (ret, cmd)
        sys.exit(ret)

def compile(filename):
    output = os.path.join("built", "obj", os.path.basename(filename))
    output = output.rsplit('.', 1)[0] + '.obj'

    cmd = "cl /nologo /c /EHsc"
    cmd += " /I" + os.path.join(panda3d_dir, "include")
    cmd += " /I" + os.path.join(panda3d_dir, "python", "include")
    cmd += " /Isrc/nametag"
    cmd += " /Isrc/margins"
    cmd += " /Isrc/etc"
    cmd += " /Fo%s %s" % (output, filename)

    run_command(cmd)

compile('../lib/coginvasioncxx/config_ccoginvasion.cxx')
compile('../lib/coginvasioncxx/labelScaler.cxx')

if 1:
    print 'Linking...'

    cmd = "link /DLL /nologo /ignore:4217 /ignore:4049 /out:libccoginvasion.pyd"
    cmd += " /LIBPATH:" + os.path.join(panda3d_dir, "lib")
    cmd += " /LIBPATH:" + os.path.join(panda3d_dir, "python", "libs")

    objects = ("labelScaler.obj", "config_ccoginvasion.obj")

    for obj in objects:
        cmd += " built/obj/" + obj

    libs = ("libp3framework", "libpanda", "libpandafx", "libpandaexpress", "libp3dtool", "libp3dtoolconfig", "libp3direct", "python27",
            "ws2_32", "shell32", "advapi32", "gdi32", "user32", "oleaut32", "ole32", "shell32", "wsock32", "imm32")
    for lib in libs:
        cmd += " %s.lib" % lib

    run_command(cmd)
