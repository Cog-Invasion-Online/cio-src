/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file lerper.cpp
 * @author Brian Lach
 * @date March 22, 2017
 */

#include "lerper.h"

#include <clockObject.h>

#include <math.h>

Lerper::Lerper( PN_stdfloat initial_val, PN_stdfloat lerp_ratio )
{
        _last_float = initial_val;
        _lerp_ratio = lerp_ratio;
}

Lerper::Lerper( LPoint3f &initial_p3, PN_stdfloat lerp_ratio )
{
        _last_p3 = initial_p3;
        _lerp_ratio = lerp_ratio;
}

void Lerper::set_last_float( PN_stdfloat val )
{
        _last_float = val;
}

void Lerper::set_last_p3( LPoint3f &val )
{
        _last_p3 = val;
}

static PN_stdfloat get_real_lr( PN_stdfloat lr )
{
        return 1 - pow( 1 - (double)lr, ClockObject::get_global_clock()->get_dt() * 30.0 );
}

PN_stdfloat Lerper::lerp_to_float( PN_stdfloat goal )
{
        PN_stdfloat lr = get_real_lr( _lerp_ratio );
        _last_float = goal * lr + _last_float * ( 1 - lr );
        return _last_float;
}

LPoint3f &Lerper::lerp_to_p3( LPoint3f &goal )
{
        PN_stdfloat lr = get_real_lr( _lerp_ratio );
        _last_p3 = goal * lr + _last_p3 * ( 1 - lr );
        return _last_p3;
}

const LPoint3f &Lerper::get_last_p3() const
{
        return _last_p3;
}

PN_stdfloat Lerper::get_last_float() const
{
        return _last_float;
}

void Lerper::set_lerp_ratio( PN_stdfloat lerp_ratio )
{
        _lerp_ratio = lerp_ratio;
}

PN_stdfloat Lerper::get_lerp_ratio() const
{
        return _lerp_ratio;
}