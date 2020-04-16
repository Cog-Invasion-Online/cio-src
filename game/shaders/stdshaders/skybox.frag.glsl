#version 330

#pragma include "shaders/stdshaders/common_frag.inc.glsl"

in vec3 l_worldEyeToVert;
uniform samplerCube skyboxSampler;

out vec4 outputColor;

void main()
{
    outputColor = texture(skyboxSampler, normalize(l_worldEyeToVert));
	FinalOutput(outputColor);
}
