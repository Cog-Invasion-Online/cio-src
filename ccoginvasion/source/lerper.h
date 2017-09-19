/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file lerper.h
 * @author Brian Lach
 * @date March 22, 2017
 */

#ifndef LERPER_H
#define LERPER_H

#include <py_panda.h>
#include <lpoint3.h>

#include "config_ccoginvasion.h"

class Lerper {
PUBLISHED:
	Lerper(PN_stdfloat initial_val, PN_stdfloat lerp_ratio);
	Lerper(LPoint3f &initial_p3, PN_stdfloat lerp_ratio);

	PN_stdfloat lerp_to_float(PN_stdfloat goal);
	LPoint3f &lerp_to_p3(LPoint3f &goal);

	void set_last_float(PN_stdfloat val);
	void set_last_p3(LPoint3f &val);

	const LPoint3f &get_last_p3() const;
	PN_stdfloat get_last_float() const;

	void set_lerp_ratio(PN_stdfloat lerp_ratio);
	PN_stdfloat get_lerp_ratio() const;

private:
	PN_stdfloat _lerp_ratio;

	PN_stdfloat _last_float;
	LPoint3f _last_p3;
};

#endif // LERPER_H