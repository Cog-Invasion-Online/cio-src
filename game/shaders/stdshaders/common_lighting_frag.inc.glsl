/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file common_lighting_frag.inc.glsl
 * @author Brian Lach
 * @date October 30, 2018
 *
 */
 
#pragma once

#pragma include "shaders/stdshaders/common.inc.glsl"
#pragma include "shaders/stdshaders/common_shadows_frag.inc.glsl"
#pragma include "shaders/stdshaders/common_brdf_frag.inc.glsl"

#define LIGHTTYPE_DIRECTIONAL	0
#define LIGHTTYPE_POINT			1
#define LIGHTTYPE_SPHERE		2
#define LIGHTTYPE_SPOT			3

#ifdef LIGHTWARP
    uniform sampler2D lightwarpSampler;
#endif

/**
 * Per-light parameters that are needed to
 * calculate the light's contribution.
 * 
 * V	:	camera->fragment (eye space)
 * N	:	fragment normal (eye space)
 * L	:	light->fragment (eye space)
 * H	:	light->fragment halfvector (eye space)
 */
struct LightingParams_t
{
    // All in eye-space
    
    // These are calculated once ahead of time
    // before calculating any lights
    vec4 fragPos;
    vec3 V; // camera->fragment
    vec3 N; // fragment normal
    float NdotV;
    float roughness;
    float roughness2;
    float metallic;
    vec3 specularColor;
    vec3 albedo;

    // This information is filled in for a light
    // before it gets calculated
    vec4 lDir;
    vec4 lPos;
    vec4 lColor;
    vec4 lAtten;
    vec4 falloff2;
    vec4 falloff3;
    float spotCosCutoff;
    float spotExponent;
    
    // These ones are calculated by the light
    vec3 L; // light->fragment ( or in case of directional light, direction of light )
    vec3 H; // half (light->fragment)
    float NdotL;
    float NdotH;
    float VdotH;
    float attenuation;
    float distance;
    
    // Sum of each light radiance,
    // filled in one-by-one.
    vec3 totalRadiance;
};

LightingParams_t newLightingParams_t(vec4 eyePos, vec3 eyeVec, vec3 eyeNormal, float NdotV,
                                     float roughness, float metallic, vec3 specular,
                                     vec3 albedo)
{
    LightingParams_t params = LightingParams_t(
        eyePos,
        eyeVec,
        eyeNormal,
        NdotV,
        roughness*roughness,
        roughness*roughness*roughness*roughness,
        metallic,
        specular,
        albedo,
        
        vec4(0),
        vec4(0),
        vec4(0),
        vec4(0),
        vec4(0),
        vec4(0),
        0.0,
        0.0,
        
        vec3(0),
        vec3(0),
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        
        vec3(0)
    );
    
    return params;
}

float GetFalloff(vec4 falloff, vec4 falloff2, float dist)
{
    float falloffevaldist = min(dist * 16.0, falloff2.z);
    
    float lattenv = falloffevaldist * falloffevaldist;
    lattenv *= falloff.z;                   // quadratic
    lattenv += falloff.y * falloffevaldist; // linear
    lattenv += falloff.x;                   // constant
    lattenv = 1.0 / lattenv;
    
    return lattenv;
}

float HasHardFalloff(vec4 falloff2)
{
    return float(falloff2.y > falloff2.x);
}

float CheckHardFalloff(vec4 falloff2, float dist, float dot)
{
    return float(dist * 16.0 <= falloff2.y);
}

float HardFalloff(LightingParams_t params)
{
    float hasHardFalloff = HasHardFalloff(params.falloff2);
    float hardFalloff = CheckHardFalloff(params.falloff2, params.distance, params.NdotL);
    return not(and(hasHardFalloff, not(hardFalloff)));
}

void ApplyHardFalloff(inout float falloff, vec4 falloff2, float dist, float dot)
{
    float t = falloff2.y - falloff2.x;
    t /= (dist * 16.0) - falloff2.x;
    
    t = clamp(t, 0, 1);
    t -= 1.0;
    
    float mult = t * t * t *( t * ( t* 6.0 - 15.0 ) + 10.0 );
    
    falloff *= mult;
}

void ComputeLightHAndDots(inout LightingParams_t params)
{
    #if SHADER_QUALITY > SHADERQUALITY_LOW
        params.H = normalize(params.L + params.V);
    #endif
    
    params.NdotL = dot(params.N, params.L);
    #ifdef HALFLAMBERT
        params.NdotL = clamp(params.NdotL * 0.5 + 0.5, 0.001, 1.0);
        #ifndef LIGHTWARP
            params.NdotL *= params.NdotL;
        #endif
    #else // HALFLAMBERT
        params.NdotL = clamp(params.NdotL, 0.001, 1.0);
    #endif // HALFLAMBERT
    #ifdef LIGHTWARP
        vec4 lwSample = texture(lightwarpSampler, vec2(params.NdotL, 0.5));
        #ifdef LIGHTWARP_IS_LUMINANCE
            // If the lightwarp was grayscale, it won't automatically convert from gamma to linear,
            // so do that here. This is so annoying.
            lwSample.rgb = pow(lwSample.rgb, vec3(2.2));
        #endif
        params.NdotL = 2.0 * lwSample.r;
    #endif // LIGHTWARP
    
    
    #if SHADER_QUALITY == SHADERQUALITY_HIGH
        params.NdotH = clamp(dot(params.N, params.H), 0.0, 1.0);
    #endif
    #if SHADER_QUALITY > SHADERQUALITY_LOW
        params.VdotH = clamp(dot(params.V, params.H), 0.0, 1.0);
    #endif
}

void ComputeLightVectors_Dir(inout LightingParams_t params)
{
    params.L = normalize(params.lDir.xyz);
    
    ComputeLightHAndDots(params);
}

void ComputeLightVectors(inout LightingParams_t params)
{
    params.L = params.lPos.xyz - params.fragPos.xyz;
#ifndef BSP_LIGHTING
    params.L *= params.lPos.w;
#endif
    params.distance = length(params.L);
    params.L = normalize(params.L);
    
    ComputeLightHAndDots(params);
}

float RoughnessToPhongExponent(float roughness)
{
    return (1 - roughness) * 1.5;
}

void AddTotalRadiance(inout LightingParams_t params)
{
    vec3 lightRadiance = params.lColor.rgb * params.attenuation;
    
    #if SHADER_QUALITY == SHADERQUALITY_HIGH
        // Full PBR light contribution with cook-torrance specular
        float G = GeometricOcclusionTerm(params.roughness2, params.NdotL, params.NdotV);
        float D = MicrofacetDistributionTerm(params.roughness2, params.NdotH);
        vec3 F	= Fresnel_Schlick(params.specularColor, params.VdotH);
        vec3 kS = F;
        vec3 kD = vec3(1.0) - kS;
        kD *= 1.0 - params.metallic;
        vec3 diffuse = kD * params.albedo / PI;
        vec3 specular = CookTorrance(F, G, D, params.NdotL, params.NdotV);
        params.totalRadiance += (diffuse + specular) * lightRadiance * params.NdotL;
        
    #elif SHADER_QUALITY == SHADERQUALITY_MEDIUM
        // PBR light contribution with empirical phong specular
        vec3 F	= Fresnel_Schlick(params.specularColor, params.VdotH);
        vec3 kS = F;
        vec3 kD = vec3(1.0) - kS;
        kD *= 1.0 - params.metallic;
        vec3 diffuse = kD * params.albedo / PI;
        
        vec3 lhalf = normalize(params.L - normalize(params.fragPos.xyz));
        float LdotR = clamp(dot(params.N, lhalf), 0, 1);
        vec3 specular = F * pow(LdotR, RoughnessToPhongExponent(params.roughness2));
        
        params.totalRadiance += (diffuse + specular) * lightRadiance * params.NdotL;
        
    #elif SHADER_QUALITY == SHADERQUALITY_LOW
        // Simple light contribution, no specular
        vec3 diffuse = params.albedo / PI;
        params.totalRadiance += diffuse * lightRadiance * params.NdotL;
        
    #endif
}

void GetPointLight(inout LightingParams_t params)
{
    
    ComputeLightVectors(params);
    
#ifdef BSP_LIGHTING
    params.attenuation = GetFalloff(params.lAtten, params.falloff2, params.distance) * HardFalloff(params);
#else
    params.attenuation = 1.0 / (params.lAtten.x + params.lAtten.y*params.distance + params.lAtten.z*params.distance*params.distance);
#endif

    AddTotalRadiance(params);
}

void GetSpotlight(inout LightingParams_t params)
{
    ComputeLightVectors(params);
    
#ifdef BSP_LIGHTING

    float dot2 = clamp(dot(params.L, normalize(-params.lDir.xyz)), 0, 1);
    if (dot2 <= params.falloff2.w)
    {
        // outside light cone
        return;
    }
    
    params.attenuation = GetFalloff(params.lAtten, params.falloff2, params.distance);
    params.attenuation *= dot2;
    
    float mult = HardFalloff(params);
    
    float innerCone = (dot2 - params.falloff2.w) / (params.lAtten.w - params.falloff2.w);
    // since we multiply this with the existing mult,
    // this makes innerCone become 1 if false, or remain the same if true
    innerCone = mul_cmp(innerCone, float(dot2 <= params.lAtten.w));
    mult *= innerCone;
    mult = clamp(mult, 0, 1);
    
    float exp = params.falloff3.x;
    exp = mul_cmp(exp, float(exp != 0.0 && exp != 1.0));
    mult = pow(mult, exp);
    
    params.attenuation *= mult;
    
    //if (hasHardFalloff)
    //{
    //    ApplyHardFalloff(lattenv, falloff2, ldist, vResult.x);
    //}
    
#else
    float langle = clamp(dot(params.lDir.xyz, -params.L), 0, 1);
    
    if (langle > params.spotCosCutoff)
    {
        params.attenuation = 1/(params.lAtten.x + params.lAtten.y*params.distance + params.lAtten.z*params.distance*params.distance);
        params.attenuation *= pow(langle, params.spotExponent);
    }
    else
    {
        return;
    }

    params.attenuation *= float(langle > params.spotCosCutoff);
#endif

    AddTotalRadiance(params);
}

void GetDirectionalLight(inout LightingParams_t params
                         #ifdef HAS_SHADOW_SUNLIGHT
                         , sampler2DArray shadowSampler, vec4 shadowCoords[PSSM_SPLITS]
                         #endif
                         )
{
	ComputeLightVectors_Dir(params);
    
    // Sunlight has constant full intensity
	params.attenuation = 1.0;
    
    #ifdef HAS_SHADOW_SUNLIGHT
        float lshad = 0.0;
        GetSunShadow(lshad, shadowSampler, shadowCoords, params.NdotL);
        params.attenuation *= lshad;
    #endif
    
    AddTotalRadiance(params);
    
}

float Fresnel(vec3 vNormal, vec3 vEyeDir)
{
    float fresnel = 1 - clamp(dot(vNormal, normalize(vEyeDir)), 0, 1);
    return fresnel * fresnel;
}

float Fresnel4(vec3 vNormal, vec3 vEyeDir)
{
    float fresnel = 1 - clamp(dot(vNormal, normalize(vEyeDir)), 0, 1);
    fresnel = fresnel * fresnel;
    return fresnel * fresnel;
}

void DedicatedRimTerm(inout vec3 totalRim, vec3 worldNormal, vec3 worldEyeToVert,
                      vec3 ambientLight, float rimBoost, float rimExponent)
{
    // =================================================
    // Derived from Team Fortress 2's Illustrative Rendering paper
    // https://steamcdn-a.akamaihd.net/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2.pdf
    // =================================================
    
    vec3 up = vec3(0, 0, 1);
    totalRim += ( (ambientLight * rimBoost) * Fresnel(worldNormal, worldEyeToVert) *
                  max(0, dot(worldNormal, up)) );
}

vec3 GetTangentSpaceNormal(sampler2D bumpSampler, vec2 texcoord)
{
	
	vec3 nSample = texture2D(bumpSampler, texcoord).rgb;
	return normalize((nSample * 2.0) - 1.0);
}

void TangentToEye(inout vec3 eyeNormal, vec3 eyeTangent, vec3 eyeBinormal, vec3 tangentNormal)
{
	eyeNormal *= tangentNormal.z;
	eyeNormal += eyeTangent.xyz * tangentNormal.x;
	eyeNormal += eyeBinormal.xyz * tangentNormal.y;
	eyeNormal = normalize(eyeNormal.xyz);
}

void TangentToWorld(inout vec3 worldNormal, mat3 tangentSpaceTranspose, vec3 tangentNormal)
{
	worldNormal = normalize(tangentSpaceTranspose * normalize(tangentNormal));
}

void GetBumpedEyeNormal(inout vec4 finalEyeNormal, sampler2D bumpSampler, vec4 texcoord,
					 vec4 tangent, vec4 binormal)
{
	// Translate tangent-space normal in map to view-space.
	vec3 tsnormal = GetTangentSpaceNormal(bumpSampler, texcoord.xy);
	TangentToEye(finalEyeNormal.xyz, tangent.xyz, binormal.xyz, tsnormal);
}

void GetBumpedWorldNormal(inout vec4 finalWorldNormal, sampler2D bumpSampler, vec4 texcoord,
		          mat3 tangentSpaceTranspose)
{
	vec3 tsnormal = GetTangentSpaceNormal(bumpSampler, texcoord.xy);
	TangentToWorld(finalWorldNormal.xyz, tangentSpaceTranspose, tsnormal);
}

void GetBumpedEyeAndWorldNormal(inout vec4 finalEyeNormal, inout vec4 finalWorldNormal, sampler2D bumpSampler, vec4 texcoord,
				vec4 eyeTangent, vec4 eyeBinormal, mat3 tangentSpaceTranspose)
{
	vec3 tsnormal = GetTangentSpaceNormal(bumpSampler, texcoord.xy);
	TangentToEye(finalEyeNormal.xyz, eyeTangent.xyz, eyeBinormal.xyz, tsnormal);
	TangentToWorld(finalWorldNormal.xyz, tangentSpaceTranspose, tsnormal);
}

vec3 CalcReflectionVectorUnnormalized(vec3 normal, vec3 eyeVector)
{
	return (2.0*(dot( normal, eyeVector ))*normal) - (dot( normal, normal )*eyeVector);
}

vec3 CalcReflectionVectorNormalized(vec3 normal, vec3 eyeVector)
{
	return 2.0 * (dot(normal, eyeVector) / dot(normal, normal)) * normal - eyeVector;
}

vec4 SampleCubeMap(vec3 worldCamToVert, vec4 worldNormal, samplerCube cubeSampler)
{
	vec3 cmR = CalcReflectionVectorUnnormalized(worldNormal.xyz, worldCamToVert);
	return texture(cubeSampler, cmR);
}

const int CUBEMAP_MIPS = 8;

vec4 SampleCubeMapLod(vec3 worldCamToVert, vec4 worldNormal,
					  samplerCube cubeSampler,
                      float roughness)
{
	vec3 cmR = CalcReflectionVectorUnnormalized(worldNormal.xyz, worldCamToVert);
	return textureLod(cubeSampler, cmR,
                      roughness * (CUBEMAP_MIPS - 1));
    //return texture(cubeSampler, cmR);
}

vec4 SampleAlbedo(sampler2D albedoSampler, vec2 texcoord)
{
    vec4 val = texture(albedoSampler, texcoord);
    #ifdef BASETEXTURE_IS_LUMINANCE
        // Temp fix for sRGB luminance textures
        val.rgb = pow(val.rgb, vec3(2.2));
    #endif
	return val;
}

vec3 AmbientCubeLight(vec3 worldNormal, vec3 ambientCube[6])
{
    vec3 linearColor;
    vec3 nSquared = worldNormal * worldNormal;
    vec3 isNegative = vec3(worldNormal.x < 0.0, worldNormal.y < 0.0, worldNormal.z < 0.0);
    vec3 isPositive = 1 - isNegative;
    
    isNegative *= nSquared;
    isPositive *= nSquared;
    
    linearColor = isPositive.x * ambientCube[0] + isNegative.x * ambientCube[1] +
				  isPositive.y * ambientCube[2] + isNegative.y * ambientCube[3] +
				  isPositive.z * ambientCube[4] + isNegative.z * ambientCube[5];
                  
    return linearColor;
}
