"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file test_base.py
@author Maverick Liberty
@date June 15, 2018

This is a workaround to resolve the working directory problems with test files.

All new test files should import this file or reimplement this workaround.

"""

import os
import sys
sys.path.append(os.getcwd())
