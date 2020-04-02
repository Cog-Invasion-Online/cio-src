/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file common_frag.inc.glsl
 * @author Brian Lach
 * @date October 30, 2018
 *
 */
 
#pragma once

#pragma include "shaders/stdshaders/common.inc.glsl"

#ifdef HDR
uniform float _exposureAdjustment[1];
#endif

bool AlphaTest(float alpha)
{
	#if ALPHA_TEST == 1 // never draw
		return false;
        
	#elif ALPHA_TEST == 2 // less
		return alpha < ALPHA_TEST_REF;
        
	#elif ALPHA_TEST == 3 // equal
		return alpha == ALPHA_TEST_REF;
        
	#elif ALPHA_TEST == 4 // less equal
		return alpha <= ALPHA_TEST_REF;
        
	#elif ALPHA_TEST == 5 // greater
		return alpha > ALPHA_TEST_REF;
        
	#elif ALPHA_TEST == 6 // not equal
		return alpha != ALPHA_TEST_REF;
        
	#elif ALPHA_TEST == 7 // greater equal
		return alpha >= ALPHA_TEST_REF;
        
	#else
        return true;
        
    #endif
}

bool ClipPlaneTest(vec4 position, vec4 clipPlane)
{
	return (dot(position.xyz, clipPlane.xyz) + clipPlane.w) > 0;
}

void FinalOutput(inout vec4 color)
{
    #ifdef HDR
	#ifndef BLEND_MODULATE // tone mapping a DecalModulate doesn't work
	    color.rgb *= _exposureAdjustment[0];
	#endif
    #else
	color.rgb = clamp(color.rgb, 0, 1);
    #endif
}
