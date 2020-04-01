#version 330

/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file unlitGeneric.vert.glsl
 * @author Brian Lach
 * @date December 30, 2018
 *
 */
 
#pragma include "shaders/stdshaders/common.inc.glsl"
#pragma include "shaders/stdshaders/common_animation_vert.inc.glsl"
 
uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in vec2 texcoord;

out vec2 l_texcoord;

#ifdef FOG
uniform mat4 p3d_ModelViewMatrix;
out vec4 l_eyePosition;
#endif

in vec4 p3d_Color;
uniform vec4 p3d_ColorScale;
out vec4 l_vertexColor;

void main()
{
    vec4 finalVertex = p3d_Vertex;
    #if HAS_HARDWARE_SKINNING
	vec3 foo = vec3(0);
        DoHardwareAnimation(finalVertex, foo, p3d_Vertex, foo);
    #endif
    
    gl_Position = p3d_ModelViewProjectionMatrix * finalVertex;
    
#ifdef FOG
	l_eyePosition = p3d_ModelViewMatrix * finalVertex;
#endif
    
    l_texcoord = texcoord;
    
    vec4 vertexColor = p3d_Color;
    vec4 colorScale = p3d_ColorScale;
    GammaToLinear(vertexColor.rgb);
    GammaToLinear(colorScale.rgb);
    l_vertexColor = vertexColor * colorScale;
}
