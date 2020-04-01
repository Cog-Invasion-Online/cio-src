/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file common_shadows_frag.inc.glsl
 * @author Brian Lach
 * @date October 30, 2018
 *
 */
 
#pragma once

#ifdef HAS_SHADOW_SUNLIGHT

#ifndef PSSM_SPLITS
#define SHADOW_TEXEL_SIZE 1.0
#define PSSM_SPLITS 3
#define SHADOW_BLUR 1.5
#define DEPTH_BIAS 0.0001
#endif

uniform float osg_FrameTime;

const float SHADOW_SIZE = 1.0 / SHADOW_TEXEL_SIZE;

#define DO_POISSON 1
#define NUM_POISSON 13
const vec2 poissonDisk[NUM_POISSON] = vec2[](
    vec2(0.0, 0.0), // center check
    vec2(-0.9328896, -0.03145855), // left check offset
    vec2(0.8162807, -0.05964844), // right check offset
    vec2(-0.184551, 0.9722522), // top check offset
    vec2(0.04031969, -0.8589798), // bottom check offset
    
    vec2(  0.3475f,  0.0042f ),
    vec2(  0.8806f,  0.3430f ),
    vec2( -0.0041f, -0.6197f ),
    vec2(  0.0472f,  0.4964f ),
    vec2( -0.3730f,  0.0874f ),
    vec2( -0.9217f, -0.3177f ),
    vec2( -0.6289f,  0.7388f ),
    vec2(  0.5744f, -0.7741f )
);

vec2 poissonDisk_8[8] = vec2[](
    vec2(  0.3475f,  0.0042f ),
    vec2(  0.8806f,  0.3430f ),
    vec2( -0.0041f, -0.6197f ),
    vec2(  0.0472f,  0.4964f ),
    vec2( -0.3730f,  0.0874f ),
    vec2( -0.9217f, -0.3177f ),
    vec2( -0.6289f,  0.7388f ),
    vec2(  0.5744f, -0.7741f )
);

vec2 poissonDisk_16[16] = vec2[](
    vec2( -0.94201624, -0.39906216 ),
    vec2( 0.94558609, -0.76890725 ), 
    vec2( -0.094184101, -0.92938870 ),
    vec2( 0.34495938, 0.29387760 ),
    vec2( -0.91588581, 0.45771432 ),
    vec2( -0.81544232, -0.87912464 ),
    vec2( -0.38277543, 0.27676845 ),
    vec2( 0.97484398, 0.75648379 ),
    vec2( 0.44323325, -0.97511554 ),
    vec2( 0.53742981, -0.47373420 ),
    vec2( -0.26496911, -0.41893023 ),
    vec2( 0.79197514, 0.19090188 ),
    vec2( -0.24188840, 0.99706507 ), 
    vec2( -0.81409955, 0.91437590 ),
    vec2( 0.19984126, 0.78641367 ),
    vec2( 0.14383161, -0.14100790 )
);

float DoShadowSimple(sampler2DArray shadowSampler, vec3 shadowCoord, int cascade, float depthCmp)
{
    return step(depthCmp, texture(shadowSampler, vec3(shadowCoord.xy, cascade)).x);
}

float DoShadowPoisson16Sample(sampler2DArray shadowSampler, vec3 shadowCoord, int cascade, float depthCmp)
{
    vec2 vPoissonOffset[8] = vec2[]( vec2(  0.3475f,  0.0042f ),
				 vec2(  0.8806f,  0.3430f ),
				 vec2( -0.0041f, -0.6197f ),
				 vec2(  0.0472f,  0.4964f ),
				 vec2( -0.3730f,  0.0874f ),
				 vec2( -0.9217f, -0.3177f ),
				 vec2( -0.6289f,  0.7388f ),
				 vec2(  0.5744f, -0.7741f ) );
				 
    float flScaleOverMapSize = SHADOW_BLUR;		// Tweak parameters to shader
    vec2 vNoiseOffset = vec2(0);
    vec4 vLightDepths = vec4(0);
    vec4 accum = vec4(0);
    vec2 rotOffset = vec2(0);
    
    vec2 shadowMapCenter = shadowCoord.xy;
    vec4 objDepth = vec4(min(depthCmp, 0.99999));
    
    // 2D Rotation Matrix setup
    vec3 RMatTop = vec3(0);
    vec3 RMatBottom = vec3(0);
    RMatTop.xy = vec2(1, 1);
    RMatBottom.xy = vec2(-1.0, 1.0) * RMatTop.yx;
    
    RMatTop *= flScaleOverMapSize;
    RMatBottom *= flScaleOverMapSize;
    RMatTop.z = shadowMapCenter.x;
    RMatBottom.z = shadowMapCenter.y;
    
    float fResult = 0.0;
    
    for (int i = 0; i < 2; i++)
    {
	rotOffset.x = dot(RMatTop.xy, vPoissonOffset[4*i+0].xy) + RMatTop.z;
	rotOffset.y = dot(RMatBottom.xy, vPoissonOffset[4*i+0].xy) + RMatBottom.z;
	vLightDepths.x = texture(shadowSampler, vec3(rotOffset, cascade)).x;
	
	rotOffset.x = dot(RMatTop.xy, vPoissonOffset[4*i+1].xy) + RMatTop.z;
	rotOffset.y = dot(RMatBottom.xy, vPoissonOffset[4*i+1].xy) + RMatBottom.z;
	vLightDepths.y = texture(shadowSampler, vec3(rotOffset, cascade)).x;
	
	rotOffset.x = dot(RMatTop.xy, vPoissonOffset[4*i+2].xy) + RMatTop.z;
	rotOffset.y = dot(RMatBottom.xy, vPoissonOffset[4*i+2].xy) + RMatBottom.z;
	vLightDepths.z = texture(shadowSampler, vec3(rotOffset, cascade)).x;
	
	rotOffset.x = dot(RMatTop.xy, vPoissonOffset[4*i+3].xy) + RMatTop.z;
	rotOffset.y = dot(RMatBottom.xy, vPoissonOffset[4*i+3].xy) + RMatBottom.z;
	vLightDepths.w = texture(shadowSampler, vec3(rotOffset, cascade)).x;

	accum += vec4(greaterThan(vLightDepths, objDepth));
    }
    
    fResult = dot(accum, vec4(0.125));
	
    return fResult;
}

float DoShadowNvidiaPCF5x5Guassian(sampler2DArray shadowSampler, vec3 shadowCoord, int cascade, float depthCmp)
{
    float fEpsilonX = SHADOW_TEXEL_SIZE;
    float fTwoEpsilonX = 2.0 * fEpsilonX;
    float fEpsilonY = fEpsilonX;
    float fTwoEpsilonY = fTwoEpsilonX;
    
    vec3 shadowMapCenter_objDepth = shadowCoord;
    vec2 shadowMapCenter = shadowMapCenter_objDepth.xy;
    float objDepth = depthCmp;
    
    vec4 vOneTaps;
    vOneTaps.x = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(fTwoEpsilonX, fTwoEpsilonY), cascade)).x);
    vOneTaps.y = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(-fTwoEpsilonX, fTwoEpsilonY), cascade)).x);
    vOneTaps.z = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(fTwoEpsilonX, -fTwoEpsilonY), cascade)).x);
    vOneTaps.w = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(-fTwoEpsilonX, -fTwoEpsilonY), cascade)).x);
    float flOneTaps = dot(vOneTaps, vec4(1.0 / 331.0));
    
    vec4 vSevenTaps;
    vSevenTaps.x = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(fTwoEpsilonX, 0), cascade)).x);
    vSevenTaps.y = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(-fTwoEpsilonX, 0), cascade)).x);
    vSevenTaps.z = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(0, fTwoEpsilonY), cascade)).x);
    vSevenTaps.w = step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(0, -fTwoEpsilonY), cascade)).x);
    float flSevenTaps = dot(vSevenTaps, vec4(7.0f / 331.0f));

    vec4 vFourTapsA, vFourTapsB;
    vFourTapsA.x = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  fTwoEpsilonX,  fEpsilonY    ), cascade) ).x);
    vFourTapsA.y = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  fEpsilonX,     fTwoEpsilonY ), cascade) ).x);
    vFourTapsA.z = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2( -fEpsilonX,     fTwoEpsilonY ), cascade) ).x);
    vFourTapsA.w = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2( -fTwoEpsilonX,  fEpsilonY    ), cascade) ).x);
    vFourTapsB.x = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2( -fTwoEpsilonX, -fEpsilonY    ), cascade) ).x);
    vFourTapsB.y = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2( -fEpsilonX,    -fTwoEpsilonY ), cascade) ).x);
    vFourTapsB.z = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  fEpsilonX,    -fTwoEpsilonY ), cascade) ).x);
    vFourTapsB.w = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  fTwoEpsilonX, -fEpsilonY    ), cascade) ).x);
    float flFourTapsA = dot( vFourTapsA, vec4( 4.0f / 331.0f) );
    float flFourTapsB = dot( vFourTapsB, vec4( 4.0f / 331.0f) );

    vec4 v20Taps;
    v20Taps.x = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  fEpsilonX,  fEpsilonY ), cascade) ).x);
    v20Taps.y = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2( -fEpsilonX,  fEpsilonY ), cascade) ).x);
    v20Taps.z = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  fEpsilonX, -fEpsilonY ), cascade) ).x);
    v20Taps.w = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2( -fEpsilonX, -fEpsilonY ), cascade) ).x);
    float fl20Taps = dot( v20Taps, vec4(20.0f / 331.0f));

    vec4 v33Taps;
    v33Taps.x = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  fEpsilonX,  0 ), cascade) ).x);
    v33Taps.y = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2( -fEpsilonX,  0 ), cascade) ).x);
    v33Taps.z = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  0, fEpsilonY ), cascade) ).x);
    v33Taps.w = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter + vec2(  0, -fEpsilonY ), cascade) ).x);
    float fl33Taps = dot( v33Taps, vec4(33.0f / 331.0f));

    float flCenterTap = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter, cascade)).x) * (55.0f / 331.0f);

    // Sum all 25 Taps
    return flOneTaps + flSevenTaps + flFourTapsA + flFourTapsB + fl20Taps + fl33Taps + flCenterTap;
}

const float nearPlane = 1.0;
const int blockerSearchNumSamples = 16;
const float lightWorldSize = .5;
const float lightFrustumWidth = 10.0;
const float lightSizeUV = lightWorldSize / lightFrustumWidth;

float PCSS_PenumbraSize(float zReceiver, float zBlocker)
{
    return (zReceiver - zBlocker) / zBlocker;
}

float PCSS_PCF(sampler2DArray shadowSampler, int cascade, vec3 shadowCoord, float depthCmp, float filterRadiusUV)
{
    float sum = 0.0;
    for (int i = 0; i < 16; i++)
    {
	vec2 offset = poissonDisk_16[i] * filterRadiusUV;
	sum += step(depthCmp, texture(shadowSampler, vec3(shadowCoord.xy + offset, cascade)).x);
    }
    return sum / 16.0;
}

void PCSS_FindBlocker(sampler2DArray shadowSampler, vec3 shadowCoord, int cascade, float depthCmp, inout float avgBlockerDepth, inout int blockers)
{
    float searchWidth = min(1.0, lightSizeUV * (depthCmp - nearPlane) / depthCmp);
    
    float blockerSum = 0;
    
    for (int i = 0; i < blockerSearchNumSamples; i++)
    {
	float shadowMapDepth = texture(shadowSampler, vec3(shadowCoord.xy + (poissonDisk_16[i] * searchWidth), cascade)).x;
	if (shadowMapDepth < depthCmp)
	{
	    blockerSum += shadowMapDepth;
	    blockers++;
	}
    }
    
    avgBlockerDepth = blockerSum / blockers;
}

float DoShadowPCSS(sampler2DArray shadowSampler, vec3 shadowCoord, int cascade, float depthCmp)
{
    float avgBlockerDepth = 0.0;
    int numBlockers = 0;
    PCSS_FindBlocker(shadowSampler, shadowCoord, cascade, depthCmp, avgBlockerDepth, numBlockers);
    
    if (numBlockers < 1) return 1.0;
    
    float penumbraRatio = PCSS_PenumbraSize(depthCmp, avgBlockerDepth);
    float filterRadiusUV = penumbraRatio * lightSizeUV * nearPlane / depthCmp;
    
    return PCSS_PCF(shadowSampler, cascade, shadowCoord, depthCmp, filterRadiusUV);
}

float SampleCascade(sampler2DArray shadowSampler, vec3 proj, float depthCmp, int cascade, int diskIdx)
{
	float val = texture(shadowSampler, vec3(proj.xy + (poissonDisk[diskIdx].xy * SHADOW_BLUR), cascade)).r;
	return step(depthCmp, val);
}

float SampleCascade8(sampler2DArray shadowSampler, vec3 proj, int cascade, float depthCmp, int i)
{
    return step(depthCmp, texture(shadowSampler, vec3(proj.xy + (poissonDisk_8[i].xy * SHADOW_BLUR), cascade)).r);
}

float SampleCascadeGather(sampler2DArray shadowSampler, vec3 coords, float depthCmp)
{
    vec4 shadow = step(vec4(depthCmp), textureGather(shadowSampler, coords, 0));
    float avg = dot(shadow, vec4(0.25));
    return avg;
}

float noise(vec2 seed)
{
    return fract(sin(dot(seed.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

float DoShadowGather(sampler2DArray shadowSampler, vec3 proj, int cascade, float depthCmp)
{
    float shad = 0.0;
    for (int i = 0; i < 8; i++)
    {
        shad += SampleCascadeGather(shadowSampler, vec3(proj.xy + (poissonDisk_8[i].xy * SHADOW_BLUR), cascade), depthCmp);
    }
    shad *= 0.125;
    
    return shad;
}

float DoShadowPCF5Tap(sampler2DArray shadowSampler, vec3 shadowCoord, int cascade, float depthCmp)
{
    float fEpsilonX = SHADOW_TEXEL_SIZE;
    float fTwoEpsilonX = 2.0 * fEpsilonX;
    float fEpsilonY = fEpsilonX;
    float fTwoEpsilonY = fTwoEpsilonX;
    
    vec3 shadowMapCenter_objDepth = shadowCoord;
    vec2 shadowMapCenter = shadowMapCenter_objDepth.xy;
    float objDepth = depthCmp;

    float shadow = step(objDepth, texture( shadowSampler, vec3(shadowMapCenter, cascade)).x);
    shadow += step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(fTwoEpsilonX, fTwoEpsilonY), cascade)).x);
    shadow += step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(-fTwoEpsilonX, fTwoEpsilonY), cascade)).x);
    shadow += step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(fTwoEpsilonX, -fTwoEpsilonY), cascade)).x);
    shadow += step(objDepth, texture(shadowSampler, vec3(shadowMapCenter + vec2(-fTwoEpsilonX, -fTwoEpsilonY), cascade)).x);
    shadow /= 5.0;
    
    return shadow;
}

float DoShadowPoissonV1(sampler2DArray shadowSampler, vec3 proj, int cascade, float depthCmp)
{
    //float lshad = step(depthCmp, texture(shadowSampler, vec3(proj.xy, cascade)).x);
    //lshad += step(depthCmp, texture(shadowSampler, vec3(proj.xy + vec2(1, 1) * SHADOW_BLUR, cascade)).x);
    //lshad += step(depthCmp, texture(shadowSampler, vec3(proj.xy + vec2(-1, 1) * SHADOW_BLUR, cascade)).x);
    //lshad += step(depthCmp, texture(shadowSampler, vec3(proj.xy + vec2(1, -1) * SHADOW_BLUR, cascade)).x);
    //lshad += step(depthCmp, texture(shadowSampler, vec3(proj.xy + vec2(-1, -1) * SHADOW_BLUR, cascade)).x);
    
    //if (lshad > 0.1 && lshad < 4.9)
    //{
	    // pixel was not totally in light or totally in shadow
	    // do more samples
	    //for (int i = 5; i < NUM_POISSON; i++)
	    //{
		//lshad += SampleCascade(shadowSampler, proj, depthCmp, cascade, i);
	    //}
	    
	    //lshad /= NUM_POISSON;
	    
	//    lshad += DoShadowPoisson16Sample(shadowSampler, proj, cascade, depthCmp);
	 //   lshad /= 6.0;
	    
	 //   return lshad;
    //}
    
    //lshad /= 5.0;
    
    float lshad = 0.0;
    for (int i = 0; i < NUM_POISSON; i++)
    {
	lshad += SampleCascade(shadowSampler, proj, depthCmp, cascade, i);
    }
    lshad /= NUM_POISSON;
    
    return lshad;
}

float DoShadowPoissonV2(sampler2DArray shadowSampler, vec3 proj, int cascade, float depthCmp)
{
    float lshad = SampleCascade(shadowSampler, proj, depthCmp, cascade, 0);
    lshad += SampleCascade(shadowSampler, proj, depthCmp, cascade, 1);
    lshad += SampleCascade(shadowSampler, proj, depthCmp, cascade, 2);
    lshad += SampleCascade(shadowSampler, proj, depthCmp, cascade, 3);
    lshad += SampleCascade(shadowSampler, proj, depthCmp, cascade, 4);
    
    if (lshad > 0.1 && lshad < 4.9)
    {
	    // pixel was not totally in light or totally in shadow
	    // do more samples
	    for (int i = 5; i < NUM_POISSON; i++)
	    {
		lshad += SampleCascade(shadowSampler, proj, depthCmp, cascade, i);
	    }
	    
	    lshad /= NUM_POISSON;
	    
	    return lshad;
    }
    
    lshad /= 5.0;
    
    return lshad;
}

int FindCascade(vec4 shadowCoords[PSSM_SPLITS], inout vec3 proj, inout float depthCmp)
{
	for (int i = 0; i < PSSM_SPLITS; i++)
	{
		proj = shadowCoords[i].xyz;
		if (proj.x >= 0.0 && proj.x <= 1.0 && proj.y >= 0.0 && proj.y <= 1.0)
		{
			depthCmp = proj.z - DEPTH_BIAS;
			return i;
		}
	}
}

void GetSunShadow(inout float lshad, sampler2DArray shadowSampler, vec4 shadowCoords[PSSM_SPLITS], float NdotL)
{	
	lshad = 0.0;
	
	// We can guarantee that the pixel is in shadow if
	// it's facing away from the light source.
	//
	// We only do this on models. Doing this on brushes
	// will cause brush faces facing away from the fake shadows
	// to be dark.
	//#if !defined(BUMPED_LIGHTMAP) && !defined(FLAT_LIGHTMAP)
		if (NdotL < 0.0)
		{
			return;
		}
	//#endif
	
	vec3 proj = vec3(0);
	float depthCmp = 0.0;
	int cascade = FindCascade(shadowCoords, proj, depthCmp);
	
	lshad = DoShadowGather(shadowSampler, proj, cascade, depthCmp);

    //#if SHADER_QUALITY == SHADERQUALITY_HIGH
        //lshad = DoShadowPoisson16Sample(shadowSampler, proj, cascade, depthCmp);
    //#elif SHADER_QUALITY == SHADERQUALITY_MEDIUM
        //lshad = DoShadowPCF5Tap(shadowSampler, proj, cascade, depthCmp);
    //#elif SHADER_QUALITY == SHADERQUALITY_LOW
        //lshad = DoShadowSimple(shadowSampler, proj, cascade, depthCmp);
    //#endif
}

void DoBlendShadow(inout vec3 diffuseLighting, sampler2DArray shadowSampler,
                   vec4 shadowCoords[PSSM_SPLITS],
                   vec3 ambientLightIdentifier, vec3 ambientLightMin, float ambientLightScale)
{
    float shadow = 0.0;
    GetSunShadow(shadow, shadowSampler, shadowCoords, 0.0);
    shadow = 1.0 - shadow;
    
    vec3 lightDelta = diffuseLighting - ambientLightMin;
    lightDelta -= dot(ambientLightIdentifier, lightDelta) * ambientLightIdentifier;
    float shadowMask = lightDelta.x * lightDelta.x + lightDelta.y * lightDelta.y + lightDelta.z * lightDelta.z;
    shadowMask = 1.0 - clamp(shadowMask * ambientLightScale, 0, 1);
    
    diffuseLighting = min(diffuseLighting, mix(diffuseLighting, ambientLightMin, shadow * shadowMask));
}

#endif
