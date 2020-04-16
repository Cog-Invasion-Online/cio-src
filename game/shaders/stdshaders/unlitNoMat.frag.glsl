#version 330

/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file unlitNoMat.frag.glsl
 * @author Brian Lach
 * @date January 11, 2019
 *
 * This serves as a fallback shader when the RenderState does not contain a material.
 * It supports a single texture (specified through TextureAttrib), flat or vertex colors,
 * and color scale. This shader will most commonly occur in GUI, as GUI elements/models
 * don't have materials on them, or any RenderState that does not contain a BSPMaterialAttrib.
 *
 */
 
#pragma include "shaders/stdshaders/common_frag.inc.glsl"
#pragma include "shaders/stdshaders/common_lighting_frag.inc.glsl"

#ifdef HAS_TEXTURE
uniform sampler2D p3d_Texture0;
in vec2 l_texcoord;
#endif

in vec4 l_vertexColor;

uniform vec4 p3d_TexAlphaOnly;

out vec4 o_color;

void main()
{
    o_color = vec4(1.0);
    
#ifdef HAS_TEXTURE
    vec4 albedo = SampleAlbedo(p3d_Texture0, l_texcoord);
    o_color *= albedo;
#endif

    o_color += p3d_TexAlphaOnly;

    o_color *= l_vertexColor;
    
#ifdef ALPHA_TEST
    if (!AlphaTest(o_color.a))
    {
        discard;
    }
#endif

	FinalOutput(o_color);
}
