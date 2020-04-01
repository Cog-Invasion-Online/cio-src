#version 330

#extension GL_ARB_explicit_attrib_location : enable
#extension GL_ARB_gpu_shader5 : enable

/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file vertexLitGeneric_PBR.frag.glsl
 * @author Brian Lach
 * @date March 09, 2019
 * 
 * This is our big boy shader -- used for most models,
 * in particular ones that should be dynamically lit by light sources.
 * 
 * Supports a plethora of material effects:
 * - $basetexture
 * - $bumpmap
 * - $envmap
 * - $phong
 * - $rimlight
 * - $halflambert
 * - $lightwarp
 * - $alpha/$translucent
 * - $selfillum
 * 
 * And these render effects:
 * - Clip planes
 * - Flat colors
 * - Vertex colors
 * - Color scale
 * - Fog
 * - Lighting
 * - Cascaded shadow maps for directional lights
 * - Alpha testing
 * - Output normals/glow to auxiliary buffer
 * 
 * Will eventually support:
 * - $detail (finer detail at close distance)
 *
 */
 
#pragma optionNV(unroll all)

#pragma include "shaders/stdshaders/common_lighting_frag.inc.glsl"
#pragma include "shaders/stdshaders/common_fog_frag.inc.glsl"
#pragma include "shaders/stdshaders/common_frag.inc.glsl"

#ifdef NEED_WORLD_POSITION
    in vec4 l_worldPosition;
#endif

#ifdef NEED_WORLD_NORMAL
    in vec4 l_worldNormal;
    in mat3 l_tangentSpaceTranspose;
#endif

#ifdef NEED_EYE_POSITION
    in vec4 l_eyePosition;
#endif

#ifdef NEED_EYE_NORMAL
    in vec4 l_eyeNormal;
#endif

in vec4 l_texcoord;

#ifdef BASETEXTURE
    uniform sampler2D baseTextureSampler;
#else // BASETEXTURE
    uniform sampler2D p3d_Texture0;
    #define baseTextureSampler p3d_Texture0
#endif

#ifdef ENVMAP
    uniform samplerCube envmapSampler;
    uniform vec3 envmapTint;
#endif

#ifdef ARME
    // =========================
    // AO/Roughness/Metallic/Emissive texture
    // =========================
    uniform sampler2D armeSampler;
#endif

#ifdef SELFILLUM
    uniform vec3 selfillumTint;
#endif

#ifdef NEED_WORLD_VEC
    in vec4 l_worldEyeToVert;
#endif

#ifdef RIMLIGHT
    uniform vec2 rimlightParams;
#endif

#ifdef BUMPMAP
    uniform sampler2D bumpSampler;
#endif

#ifdef NEED_TBN
    in vec4 l_tangent;
    in vec4 l_binormal;
#endif

// Auxilliary bitplanes for deferred passes
#ifdef NEED_AUX_NORMAL
    layout(location = 1) out vec4 o_aux_normal;
#endif
#ifdef NEED_AUX_ARME
    layout(location = 2) out vec4 o_aux_arme;
#endif

in vec4 l_vertexColor;

#if NUM_CLIP_PLANES > 0
uniform vec4 p3d_ClipPlane[NUM_CLIP_PLANES];
#endif

#ifdef LIGHTING

    #ifdef BSP_LIGHTING
    
        uniform int lightTypes[NUM_LIGHTS];
        uniform int lightCount[1];
        uniform mat4 lightData[NUM_LIGHTS];
        uniform mat4 lightData2[NUM_LIGHTS];
        uniform vec3 ambientCube[6];

    #else // BSP_LIGHTING
    
        uniform mat4 p3d_ViewMatrix;

        uniform struct p3d_LightSourceParameters
        {
            vec4 diffuse;
            vec4 position;
            vec3 attenuation;
            
            // Spotlights only
            float spotCosCutoff;
            float spotExponent;
            vec3 spotDirection;
        } p3d_LightSource[NUM_LIGHTS];

        uniform struct
        {
            vec4 ambient;
        } p3d_LightModel;

    #endif // BSP_LIGHTING

    #ifdef HAS_SHADOW_SUNLIGHT
        uniform sampler2DArray pssmSplitSampler;
        in vec4 l_pssmCoords[PSSM_SPLITS];
        uniform vec3 sunVector[1];
    #endif

#endif // LIGHTING

layout(location = 0) out vec4 outputColor;

void main()
{
    // Clipping first!
    #if NUM_CLIP_PLANES > 0
        for (int i = 0; i < NUM_CLIP_PLANES; i++)
        {
            if (!ClipPlaneTest(l_eyePosition, p3d_ClipPlane[i])) 
            {
                // pixel outside of clip plane interiors
                discard;
            }
        }
    #endif

	#ifdef BASETEXTURE
        vec4 albedo = SampleAlbedo(baseTextureSampler, l_texcoord.xy);
    #else
        vec4 albedo = vec4(0.0, 0.0, 0.0, 1.0);
    #endif
    // Modulate albedo with vertex/flat colors
    albedo *= l_vertexColor;
    // Explicit alpha value from material.
    #ifdef ALPHA
        albedo.a *= ALPHA;
    #endif

    #ifdef ALPHA_TEST
        if (!AlphaTest(albedo.a))
        {
            discard;
        }
    #endif

    #ifdef NEED_EYE_NORMAL
        vec4 finalEyeNormal = normalize(l_eyeNormal);
    #else
        vec4 finalEyeNormal = vec4(0.0);
    #endif
	
    #ifdef NEED_WORLD_NORMAL
        vec4 finalWorldNormal = normalize(l_worldNormal);
        mat3 tangentSpaceTranspose = l_tangentSpaceTranspose;
        tangentSpaceTranspose[2] = finalWorldNormal.xyz;
    #else
        vec4 finalWorldNormal = vec4(0.0);
    #endif

    #ifdef BUMPMAP
        #if defined(NEED_EYE_NORMAL)
            GetBumpedEyeNormal(finalEyeNormal, bumpSampler, l_texcoord,
                            l_tangent, l_binormal);
        #endif
        #if defined(NEED_WORLD_NORMAL)
            GetBumpedWorldNormal(finalWorldNormal, bumpSampler, l_texcoord,
                            tangentSpaceTranspose);
        #endif
    #endif
    
    #ifdef NEED_WORLD_NORMAL
        float NdotV = clamp(abs(dot(finalWorldNormal.xyz, normalize(l_worldEyeToVert.xyz))), 0, 1);
    #else
        float NdotV = 1.0;
    #endif
    
    // AO/Roughness/Metallic/Emissive properties
    #ifdef ARME
        vec4 armeParams = texture(armeSampler, l_texcoord.xy);
    #else
        vec4 armeParams = vec4(AO, ROUGHNESS, METALLIC, EMISSIVE);
    #endif
    
    /////////////////////////////////////////////////////
    // Aux bitplane outputs
    #ifdef NEED_AUX_NORMAL
        #ifdef ENVMAP
            int hasEnvmap = 1;
        #else
            int hasEnvmap = 0;
        #endif
        o_aux_normal = vec4((finalWorldNormal.xyz * 0.5) + 0.5, hasEnvmap);
    #endif
    #ifdef NEED_AUX_ARME
        o_aux_arme = armeParams;
    #endif
    /////////////////////////////////////////////////////
    
    vec3 specularColor = mix(vec3(0.04), albedo.rgb, armeParams.z);

    #ifdef LIGHTING
    
        // Initialize our lighting parameters
        LightingParams_t params = newLightingParams_t(
            l_worldPosition,
            normalize(l_worldEyeToVert.xyz),
            normalize(finalWorldNormal.xyz),
            NdotV,
            armeParams.y,
            armeParams.z,
            specularColor,
            albedo.rgb
            );
        
        vec3 ambientDiffuse = vec3(0, 0, 0);
        #ifdef BSP_LIGHTING
            ambientDiffuse += AmbientCubeLight(finalWorldNormal.xyz, ambientCube);
        #else
            ambientDiffuse += p3d_LightModel.ambient.rgb;
        #endif
        
        #ifdef RIMLIGHT
            // Dedicated rim lighting for this pixel,
            // adds onto final lighting, uses ambient light as basis
            DedicatedRimTerm(params.totalRadiance, l_worldNormal.xyz,
                             l_worldEyeToVert.xyz, ambientDiffuse,
                             rimlightParams.x, rimlightParams.y);
        #endif
        
        // Now factor in local light sources
        #ifdef BSP_LIGHTING
            int lightType;
            for (int i = 0; i < lightCount[0]; i++)
        #else
            for (int i = 0; i < NUM_LIGHTS; i++)
        #endif
        {
            #ifdef BSP_LIGHTING
                params.lPos = lightData[i][0];
                params.lDir = lightData[i][1];
                params.lAtten = lightData[i][2];
                params.lColor = lightData[i][3];
                params.falloff2 = lightData2[i][0];
                params.falloff3 = lightData2[i][1];
                lightType = lightTypes[i];
            #else
                params.lColor = p3d_LightSource[i].diffuse;
                params.lDir = p3d_ViewMatrix * p3d_LightSource[i].position;
                params.lPos = params.lDir;
                params.lAtten = vec4(p3d_LightSource[i].attenuation, 0.0);
                params.falloff2 = vec4(0);
                params.falloff3 = vec4(0);
                bool isDirectional = params.lPos[3] == 0.0;
            #endif // BSP_LIGHTING
            
            #ifdef BSP_LIGHTING
                if (lightType == LIGHTTYPE_DIRECTIONAL)
            #else
                if (isDirectional)
            #endif
            {
                GetDirectionalLight(params
                                    #ifdef HAS_SHADOW_SUNLIGHT
                                        , pssmSplitSampler, l_pssmCoords
                                    #endif // HAS_SHADOW_SUNLIGHT
                );
            }
            #ifdef BSP_LIGHTING
                else if (lightType == LIGHTTYPE_POINT)
            #else
                else if (p3d_LightSource[i].spotExponent == 0.0)
            #endif
            {
                GetPointLight(params);
            }
            #ifdef BSP_LIGHTING
                else if (lightType == LIGHTTYPE_SPOT)
            #else
                else
            #endif
            {
                #ifndef BSP_LIGHTING
                    params.lDir = p3d_ViewMatrix * vec4(p3d_LightSource[i].spotDirection, 0);
                    params.spotCosCutoff = p3d_LightSource[i].spotCosCutoff;
                    params.spotExponent = p3d_LightSource[i].spotExponent;
                #endif
                
                GetSpotlight(params);
            }
        }
        
        vec3 totalRadiance = params.totalRadiance;
        
    #else // LIGHTING
    
        // No lighting, pixel starts fullbright.
        vec3 ambientDiffuse = vec3(1.0);
        vec3 totalRadiance = vec3(0);
        
    #endif // LIGHTING
    
    // Modulate with albedo  
    ambientDiffuse.rgb *= albedo.rgb;
    ambientDiffuse.rgb *= armeParams.x;

	#ifndef LIGHTING
		vec3 kD = vec3(1.0);
	#else
		vec3 F = Fresnel_Schlick(specularColor, NdotV);
	#endif

    vec3 specularLighting = vec3(0);

    #ifdef LIGHTING        
        #ifdef ENVMAP

            vec3 spec = SampleCubeMapLod(l_worldEyeToVert.xyz,
                                         finalWorldNormal,
                                         envmapSampler, armeParams.y).rgb;
                                         
            // TODO: use a BRDF lookup texture in SHADERQUALITY_MEDIUM
            #if SHADER_QUALITY > SHADERQUALITY_LOW
                vec3 iblspec = spec * EnvironmentBRDF(armeParams.y, NdotV, F);
            #else
                vec3 iblspec = spec * F * specularColor;
            #endif
            
            specularLighting += iblspec;
        
        #endif
    #endif

	vec3 totalAmbient = ambientDiffuse;
    vec3 color = totalAmbient + totalRadiance + specularLighting;
    
    #ifdef SELFILLUM
        float selfillumMask = armeParams.w;
        color = mix(color, selfillumTint * albedo.rgb, selfillumMask);
    #endif
    
    outputColor = vec4(color, albedo.a);

    #ifdef FOG
		ApplyFog(outputColor, l_eyePosition);
    #endif

    // Done!
	FinalOutput(outputColor);
}
