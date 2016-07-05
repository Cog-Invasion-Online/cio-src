#ifndef C_NAMETAG_H
#define C_NAMETAG_H

#include "stdafx.h"

#include "Python.h"

#include "textNode.h"

class CNametag {
PUBLISHED:
	CNametag();

	void set_chatballoon_size(double width, double height);
	void set_panel_size(double width, double height);

	void get_panel_region(TextNode& tn, PyObject* list);
	void get_chatballoon_region(PyObject* list);

protected:
	double m_cb_width;
	double m_cb_height;
	double m_panel_width;
	double m_panel_height;

};

#endif // C_NAMETAG_H
