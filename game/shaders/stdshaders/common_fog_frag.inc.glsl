/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file common_fog_frag.inc.glsl
 * @author Brian Lach
 * @date October 31, 2018
 *
 */
 
#pragma once

#ifdef FOG

uniform vec4 fogData[2];

void GetFogLinear(inout vec4 result, vec4 fogColor, float dist, vec4 fogData)
{
	result.rgb = mix(fogColor.rgb, result.rgb, clamp((fogData.z - dist) * fogData.w, 0, 1));
}

void GetFogExp(inout vec4 result, vec4 fogColor, float dist, float density)
{
	result.rgb = mix(fogColor.rgb, result.rgb, clamp(exp2(density * dist * -1.442695), 0, 1));
}

void GetFogExpSqr(inout vec4 result, vec4 fogColor, float dist, vec4 fogData)
{
	result.rgb = mix(fogColor.rgb, result.rgb, clamp(exp2(fogData.x * fogData.x * dist * dist * -1.442695), 0, 1));
}

void ApplyFog(inout vec4 result, vec4 eyePos)
{
    float dist = length(eyePos.xyz);

	#if defined(BLEND_MODULATE)
		vec4 fogColor = vec4(0.5, 0.5, 0.5, 1.0);
	#elif defined(BLEND_ADDITIVE)
		vec4 fogColor = vec4(0, 0, 0, 1.0);
	#else
		vec4 fogColor = fogData[0];
	#endif

    GetFogExp(result, fogColor, dist, fogData[1].x);
}

#endif
