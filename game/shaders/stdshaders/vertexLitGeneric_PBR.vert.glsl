#version 330

/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file vertexLitGeneric_PBR.vert.glsl
 * @author Brian Lach
 * @date March 09, 2019
 *
 */
 
#pragma optionNV(unroll all)

#pragma include "shaders/stdshaders/common.inc.glsl"
#pragma include "shaders/stdshaders/common_shadows_vert.inc.glsl"
#pragma include "shaders/stdshaders/common_animation_vert.inc.glsl"

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

#if defined(NEED_TBN) || defined(NEED_EYE_VEC) || defined(NEED_WORLD_NORMAL)
    in vec4 p3d_Tangent;
    in vec4 p3d_Binormal;
    out vec4 l_tangent;
    out vec4 l_binormal;
#endif

uniform vec4 p3d_ColorScale;
in vec4 p3d_Color;
out vec4 l_vertexColor;

#if defined(NEED_WORLD_POSITION) || defined(NEED_WORLD_NORMAL)
    uniform mat4 p3d_ModelMatrix;
#endif

#if defined(NEED_WORLD_POSITION)
    out vec4 l_worldPosition;
#endif

#ifdef NEED_WORLD_NORMAL
    out vec4 l_worldNormal;
    out mat3 l_tangentSpaceTranspose;
#endif

#ifdef NEED_EYE_POSITION
    uniform mat4 p3d_ModelViewMatrix;
    out vec4 l_eyePosition;
#elif defined(NEED_TBN)
    uniform mat4 p3d_ModelViewMatrix;
#endif

#ifdef NEED_EYE_NORMAL
    out vec4 l_eyeNormal;
#endif

#ifdef NEED_WORLD_VEC
    uniform vec4 wspos_view;
    out vec4 l_worldEyeToVert;
#endif

in vec4 texcoord;
out vec4 l_texcoord;

#ifdef HAS_SHADOW_SUNLIGHT
    uniform mat4 pssmMVPs[PSSM_SPLITS];
    uniform vec3 sunVector[1];
    out vec4 l_pssmCoords[PSSM_SPLITS];
#endif

void main()
{
	vec4 finalVertex = p3d_Vertex;
    vec3 finalNormal = p3d_Normal;

    #if HAS_HARDWARE_SKINNING
        DoHardwareAnimation(finalVertex, finalNormal, p3d_Vertex, p3d_Normal);
    #endif

	gl_Position = p3d_ModelViewProjectionMatrix * finalVertex;
    
    // pass through the texcoord input as-is
    l_texcoord = texcoord;

    #if defined(NEED_WORLD_POSITION)
        l_worldPosition = p3d_ModelMatrix * finalVertex;
    #endif

    #ifdef NEED_WORLD_NORMAL
        l_worldNormal = p3d_ModelMatrix * vec4(finalNormal, 0);
        l_tangentSpaceTranspose[0] = mat3(p3d_ModelMatrix) * p3d_Tangent.xyz;
        l_tangentSpaceTranspose[1] = mat3(p3d_ModelMatrix) * -p3d_Binormal.xyz;
        l_tangentSpaceTranspose[2] = l_worldNormal.xyz;
    #endif

    #ifdef NEED_EYE_POSITION
        l_eyePosition = p3d_ModelViewMatrix * finalVertex;
    #endif

    #ifdef NEED_EYE_NORMAL
        l_eyeNormal = vec4(normalize(p3d_NormalMatrix * finalNormal), 0.0);
    #endif

    vec4 colorScale = p3d_ColorScale;
    vec4 vertexColor = p3d_Color;
    GammaToLinear(colorScale.rgb);
    GammaToLinear(vertexColor.rgb);
    l_vertexColor = vertexColor * colorScale;

    #ifdef NEED_TBN
        l_tangent = vec4(normalize(p3d_NormalMatrix * p3d_Tangent.xyz), 0.0);
        l_binormal = vec4(normalize(p3d_NormalMatrix * -p3d_Binormal.xyz), 0.0);
    #endif

    #ifdef NEED_WORLD_VEC
        l_worldEyeToVert = wspos_view - l_worldPosition;
    #endif

    #ifdef HAS_SHADOW_SUNLIGHT
        ComputeShadowPositions(l_worldNormal.xyz, l_worldPosition,
                               sunVector[0], pssmMVPs, l_pssmCoords);
    #endif
}

