#version 330

in vec2 l_coordTap0;
in vec2 l_coordTap1;
in vec2 l_coordTap2;
in vec2 l_coordTap3;
in vec2 l_coordTap1Neg;
in vec2 l_coordTap2Neg;
in vec2 l_coordTap3Neg;

uniform sampler2D texSampler;
uniform vec2 psTapOffsets[3];
uniform vec3 scaleFactor;

out vec4 outputColor;

void main()
{
    vec4 s0, s1, s2, s3, s4, s5, s6, color;

	// Sample taps with coordinates from VS
	s0 = texture( texSampler, l_coordTap0 );
	s1 = texture( texSampler, l_coordTap1 );
	s2 = texture( texSampler, l_coordTap2 );
	s3 = texture( texSampler, l_coordTap3 );
	s4 = texture( texSampler, l_coordTap1Neg );
	s5 = texture( texSampler, l_coordTap2Neg );
	s6 = texture( texSampler, l_coordTap3Neg );

	color = s0 * 0.2013f;
	color += ( s1 + s4 ) * 0.2185f;
	color += ( s2 + s5 ) * 0.0821f;
	color += ( s3 + s6 ) * 0.0461f;

	// Compute tex coords for other taps
	vec2 coordTap4 = l_coordTap0 + psTapOffsets[0];
	vec2 coordTap5 = l_coordTap0 + psTapOffsets[1];
	vec2 coordTap6 = l_coordTap0 + psTapOffsets[2];
	vec2 coordTap4Neg = l_coordTap0 - psTapOffsets[0];
	vec2 coordTap5Neg = l_coordTap0 - psTapOffsets[1];
	vec2 coordTap6Neg = l_coordTap0 - psTapOffsets[2];

	// Sample the taps
	s1 = texture( texSampler, coordTap4 );
	s2 = texture( texSampler, coordTap5 );
	s3 = texture( texSampler, coordTap6 );
	s4 = texture( texSampler, coordTap4Neg );
	s5 = texture( texSampler, coordTap5Neg );
	s6 = texture( texSampler, coordTap6Neg );

	color += ( s1 + s4 ) * 0.0262f;
	color += ( s2 + s5 ) * 0.0162f;
	color += ( s3 + s6 ) * 0.0102f;
	color.xyz *= scaleFactor.xyz;

	outputColor = color;
}
