#version 330

/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file unlitNoMat.vert.glsl
 * @author Brian Lach
 * @date January 11, 2019
 *
 * This serves as a fallback shader when the RenderState does not contain a material.
 * It supports a single texture (specified through TextureAttrib), flat or vertex colors,
 * and color scale. This shader will most commonly occur in GUI, as GUI elements/models
 * don't have materials on them, or any RenderState that does not contain a BSPMaterialAttrib.
 *
 */
 
#pragma include "shaders/stdshaders/common.inc.glsl"
#pragma include "shaders/stdshaders/common_animation_vert.inc.glsl"
 
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;

#ifdef HAS_TEXTURE
in vec2 p3d_MultiTexCoord0;
out vec2 l_texcoord;
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
    
#ifdef HAS_TEXTURE
    l_texcoord = p3d_MultiTexCoord0;
#endif
    
    vec4 vertexColor = p3d_Color;
    vec4 colorScale = p3d_ColorScale;
    GammaToLinear(vertexColor.rgb);
    GammaToLinear(colorScale.rgb);
    l_vertexColor = vertexColor * colorScale;
}
