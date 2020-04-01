#version 330

in vec2 l_texcoord;

uniform sampler2D sceneColorSampler;
uniform float luminanceMinMax[2];

out vec4 outputColor;

const vec3 luminance_weights = vec3( 0.2125f, 0.7154f, 0.0721f );

void main()
{
    vec3 color = texture(sceneColorSampler, l_texcoord).rgb;
    float luminance = dot(color, luminance_weights);
    
    if (luminance < luminanceMinMax[0] || luminance >= luminanceMinMax[1])
    {
        // Pixel doesn't fall in specified luminance range.
        outputColor = vec4(0, 0, 0, 0);
        discard;
    }
    
    outputColor = vec4(1, 0, 0, 1);
}
