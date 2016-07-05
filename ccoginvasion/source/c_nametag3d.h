#ifndef C_NAMETAG3D_H
#define C_NAMETAG3D_H

#include "c_nametag.h"

class CNametag3d : public CNametag {
PUBLISHED:
	void get_chatballoon_region(LPoint3& center, double height_3d, PyObject* list);
	double get_scale(double distance, double scale_factor);
};

#endif // C_NAMETAG3D_H
