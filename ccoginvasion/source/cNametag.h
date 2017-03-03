/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file cNametag.h
 * @author Brian Lach
 * @date 2016-07-04
 */

#ifndef C_NAMETAG_H
#define C_NAMETAG_H

#include "Python.h"

#include "textNode.h"

class CNametag {
PUBLISHED:
	CNametag();

	void set_chatballoon_size(double width, double height);
	void set_panel_size(double width, double height);

	void get_panel_region(TextNode &tn, PyObject *list);
	void get_chatballoon_region(PyObject *list);

protected:
	double _cb_width;
	double _cb_height;
	double _panel_width;
	double _panel_height;

};

#endif // C_NAMETAG_H
