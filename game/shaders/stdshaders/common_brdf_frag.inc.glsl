/**
 * COG INVASION ONLINE
 * Copyright (c) CIO Team. All rights reserved.
 *
 * @file common_brdf_frag.inc.glsl
 * @author Brian Lach
 * @date April 04, 2019
 *
 */

const float PI = 3.14159265359;

// Fresnel term F( v, h )
// Fnone( v, h ) = F(0�) = specularColor
vec3 Fresnel_Schlick( vec3 specularColor, float VdotH )
{
    return specularColor + ( 1.0 - specularColor ) * pow( clamp(1.0 - VdotH, 0, 1), 5.0 );
}

vec3 CookTorrance(vec3 F, float G, float D, float NdotL, float NdotV)
{
    return F * G * D / (4.0 * NdotL * NdotV);
}

float MicrofacetDistributionTerm(float alpha2, float NdotH)
{
    float f = (NdotH * alpha2 - NdotH) * NdotH + 1.0;
    float D = alpha2 / (PI * f * f);
    return D;
}

float GeometricOcclusionTerm(float alpha2, float NdotL, float NdotV)
{
    float attenuationL = 2.0 * NdotL / (NdotL + sqrt(alpha2 + (1.0 - alpha2) * (NdotL * NdotL)));
    float attenuationV = 2.0 * NdotV / (NdotV + sqrt(alpha2 + (1.0 - alpha2) * (NdotV * NdotV)));
    float G = attenuationL * attenuationV;
    return G;
}

// Environment BRDF approximations
// see s2013_pbs_black_ops_2_notes.pdf
float a1vf( float g )
{
	return ( 0.25 * g + 0.75 );
}

float a004( float g, float NdotV )
{
	float t = min( 0.475 * g, exp2( -9.28 * NdotV ) );
	return ( t + 0.0275 ) * g + 0.015;
}

float a0r( float g, float NdotV )
{
	return ( ( a004( g, NdotV ) - a1vf( g ) * 0.04 ) / 0.96 );
}

vec3 EnvironmentBRDF( float g, float NdotV, vec3 rf0 )
{
	vec4 t = vec4( 1.0 / 0.96, 0.475, ( 0.0275 - 0.25 * 0.04 ) / 0.96, 0.25 );
	t *= vec4( g, g, g, g );
	t += vec4( 0.0, 0.0, ( 0.015 - 0.75 * 0.04 ) / 0.96, 0.75 );
	float a0 = t.x * min( t.y, exp2( -9.28 * NdotV ) ) + t.z;
	float a1 = t.w;
	
	return clamp( a0 + rf0 * ( a1 - a0 ), 0, 1 );
}
