/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file cnametag.cpp
 * @author Brian Lach
 * @date 2016-07-04
 */

#include "cnametag.h"

#include <Python.h>

#include <textNode.h>

CNametag::CNametag()
{
}

void CNametag::set_chatballoon_size( double width, double height )
{
        _cb_width = width;
        _cb_height = height;
}

void CNametag::set_panel_size( double width, double height )
{
        _panel_width = width;
        _panel_height = height;
}

void CNametag::get_panel_region( TextNode *tn, PyObject *list )
{
        // Here's the heavy stuff.

        double centerX = ( tn->get_left() + tn->get_right() ) / 2.0;
        double centerY = ( tn->get_bottom() + tn->get_top() ) / 2.0;

        PyObject *left = PyFloat_FromDouble( centerX - ( _panel_width / 2.0 ) );
        PyObject *right = PyFloat_FromDouble( centerX + ( _panel_width / 2.0 ) );
        PyObject *bottom = PyFloat_FromDouble( centerY - ( _panel_height / 2.0 ) );
        PyObject *top = PyFloat_FromDouble( centerY + ( _panel_height / 2.0 ) );

        // Return a python list containing the region data.

        PyList_Insert( list, 0, left );
        PyList_Insert( list, 1, right );
        PyList_Insert( list, 2, bottom );
        PyList_Insert( list, 3, top );
}

void CNametag::get_chatballoon_region( PyObject *list )
{
        // Here's the heavy stuff.

        double width = _cb_width / 2.0;
        PyObject *right_py = PyFloat_FromDouble( width );
        PyObject *left_py = PyFloat_FromDouble( -width );

        double height = _cb_height / 2.0;
        PyObject *top_py = PyFloat_FromDouble( height );
        PyObject *bottom_py = PyFloat_FromDouble( -height );

        // Return a python list containing the region data.

        PyList_Insert( list, 0, left_py );
        PyList_Insert( list, 1, right_py );
        PyList_Insert( list, 2, bottom_py );
        PyList_Insert( list, 3, top_py );
}