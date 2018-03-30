/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file cnametag3d.cpp
 * @author Brian Lach
 * @date 2016-07-04
 */

#include "cnametag3d.h"

#include <Python.h>

#include <cmath>

void CNametag3d::get_chatballoon_region( const LPoint3f &center, double height_3d, PyObject *list )
{
        double left = center[0] - ( _cb_width / 2.0 );
        double right = left + _cb_width;
        PyObject *left_py = PyFloat_FromDouble( left );
        PyObject *right_py = PyFloat_FromDouble( right );

        double bottom = height_3d - 2.4;
        double top = bottom + _cb_height;
        PyObject *bottom_py = PyFloat_FromDouble( bottom );
        PyObject *top_py = PyFloat_FromDouble( top );

        PyList_Insert( list, 0, left_py );
        PyList_Insert( list, 1, right_py );
        PyList_Insert( list, 2, bottom_py );
        PyList_Insert( list, 3, top_py );
}

double CNametag3d::get_scale( double distance, double scale_factor )
{
        return sqrt( distance ) * scale_factor;
}