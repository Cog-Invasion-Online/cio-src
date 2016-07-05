#include "c_nametag3d.h"

#include <cmath>

void CNametag3d::get_chatballoon_region(LPoint3& center, double height_3d, PyObject* list)
{
	double left = center[0] - (m_cb_width / 2.0);
	double right = left + m_cb_width;
	PyObject* left_py = PyFloat_FromDouble(left);
	PyObject* right_py = PyFloat_FromDouble(right);

	double bottom = height_3d - 2.4;
	double top = bottom + m_cb_height;
	PyObject* bottom_py = PyFloat_FromDouble(bottom);
	PyObject* top_py = PyFloat_FromDouble(top);

	PyList_Insert(list, 0, left_py);
	PyList_Insert(list, 1, right_py);
	PyList_Insert(list, 2, bottom_py);
	PyList_Insert(list, 3, top_py);
}

double CNametag3d::get_scale(double distance, double scale_factor)
{
	return sqrt(distance) * scale_factor;
}