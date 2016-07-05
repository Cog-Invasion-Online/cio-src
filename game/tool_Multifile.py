"""

  Filename: tool_Multifile.py
  Created by: DuckyDuck1553 (6Nov14)

"""

import os, argparse, glob

parser = argparse.ArgumentParser(description = "Do things with a multifile.")
parser.add_argument("--filename", default = "phase_3.mf", help = "The file to be used.")
parser.add_argument("--mtype", default = "compile", help = "Compile or decompile.")
args = parser.parse_args()

multify = '..\\Panda3D-CI\\bin\\multify.exe'

def do(mtype, filename):
    cmd = os.path.join(multify)
    if mtype == "decompile":
        cmd += " -x -f %s -p \"cio-03-06-16_lsphases\"" % filename
    elif mtype == "compile":
        cmd += " -c -f %s %s -p \"cio-03-06-16_lsphases\"" % (filename + '.mf', filename)
    os.system(cmd)

def do_phase0():
    cmd = os.path.join(multify)
    cmd += " -c -f phase_0.mf models"
    os.system(cmd)

def do_all(mtype):
    if mtype == 'compile':
        search = "phase_*"
    else:
        search = '*.mf'
    for multifile in glob.glob(search):
        if multifile[-1:].isdigit():
            do(mtype, multifile)
    if mtype == 'compile':
        do_phase0()

if args.filename.lower() == "all":
    do_all(args.mtype.lower())
else:
    do(args.mtype.lower(), args.filename)
