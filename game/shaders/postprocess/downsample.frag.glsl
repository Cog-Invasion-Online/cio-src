#version 330

in vec2 l_coordTap0;
in vec2 l_coordTap1;
in vec2 l_coordTap2;
in vec2 l_coordTap3;

uniform sampler2D fbColorSampler;
uniform vec4 params;

out vec4 outputColor;

vec4 Shape(vec2 uv)
{
    vec4 pixel = texture(fbColorSampler, uv);
    float lum = dot(pixel.xyz, params.xyz);
    pixel.xyz = pow(pixel.xyz, vec3(params.w)) * lum;
    return pixel;
}

void main()
{
    vec4 s0, s1, s2, s3;
    
    // Sample 4 taps
    s0 = Shape(l_coordTap0);
    s1 = Shape(l_coordTap1);
    s2 = Shape(l_coordTap2);
    s3 = Shape(l_coordTap3);
    
    outputColor = (s0 + s1 + s2 + s3) * 0.25;
}
