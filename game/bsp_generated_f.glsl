#version 430
in vec4 l_world_normal;
in vec4 l_eye_position;
in vec4 l_eye_normal_orig;
in vec4 l_texcoord;
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
in vec3 l_tangent;
in vec3 l_binormal;
uniform struct {
	 vec3 specular;
	 float shininess;
	 vec4 rimColor;
	 float rimWidth;
} p3d_Material;
uniform vec4 p3d_ColorScale;
uniform mat4 p3d_ViewMatrix;
in vec4 l_ambient_term;
uniform int light_count[1];
uniform int light_type[2];
uniform vec3 light_pos[2];
uniform vec4 light_direction[2];
uniform vec4 light_atten[2];
uniform vec3 light_color[2];
const int LIGHTTYPE_SUN = 0;
const int LIGHTTYPE_POINT = 1;
const int LIGHTTYPE_SPOT = 2;
out vec4 o_color;
float half_lambert(float dp)
{
	 float hl = dp * 0.5;
	 hl += 0.5;
	 hl *= hl;
	 return hl;
}
void main() {
	 vec4 l_eye_normal = l_eye_normal_orig;
	 vec4 result;
	 vec4 texcoord0 = l_texcoord;
	 vec4 texcoord1 = l_texcoord;
	 // Fetch all textures.
	 vec4 tex0 = texture2D(p3d_Texture0, texcoord0.xy);
	 vec4 tex1 = texture2D(p3d_Texture1, texcoord1.xy);
	 // Translate tangent-space normal in map to view-space.
	 vec3 tsnormal = (tex1.xyz * 2) - 1;
	 l_eye_normal.xyz *= tsnormal.z;
	 l_eye_normal.xyz += l_tangent * tsnormal.x;
	 l_eye_normal.xyz += l_binormal * tsnormal.y;
	 // Correct the surface normal for interpolation effects
	 l_eye_normal.xyz = normalize(l_eye_normal.xyz);
	 // Begin view-space light calculations
	 float ldist,lattenv,langle,lshad,lintensity;
	 vec4 lcolor,lpoint,latten,ldir,leye;
	 vec3 lvec,lhalf,lspec;
	 vec4 tot_rim = vec4(0, 0, 0, 0);
	 vec4 tot_diffuse = vec4(0, 0, 0, 0);
	 vec3 tot_specular = vec3(0, 0, 0);
	 float shininess = p3d_Material.shininess;
	 tot_diffuse += l_ambient_term;
	 vec3 rim_eye_pos = normalize(-l_eye_position.xyz);
	 float rim_intensity = p3d_Material.rimWidth - max(dot(rim_eye_pos, l_eye_normal.xyz), 0.0);
	 rim_intensity = max(0.0, rim_intensity);
	 tot_rim += vec4(rim_intensity * p3d_Material.rimColor);
	 for (int i = 0; i < light_count[0]; i++) {
	         lcolor = vec4(light_color[i], 1.0);
	         latten = light_atten[i];
	         if (light_type[i] == LIGHTTYPE_POINT) {
	             lpoint = p3d_ViewMatrix * vec4(light_pos[i], 1);
	             lvec = lpoint.xyz - l_eye_position.xyz;
	             ldist = length(lvec);
	             lvec = normalize(lvec);
	             lintensity = dot(l_eye_normal.xyz, lvec);
	     lintensity = half_lambert(lintensity);
	             lattenv = ldist * latten.x;
	             float ratio = lintensity / lattenv;
	             lcolor *= ratio;
	             tot_diffuse += lcolor;
	 lhalf = normalize(lvec - vec3(0, 1, 0));
	     lspec = p3d_Material.specular;
	     lspec *= lattenv;
	     lspec *= pow(clamp(dot(l_eye_normal.xyz, lhalf), 0, 1), shininess);
	     tot_specular += lspec;
	         }
	         else if(light_type[i] == LIGHTTYPE_SUN) {
	             lvec = normalize((p3d_ViewMatrix * light_direction[i]).xyz);
	             lintensity = dot(l_eye_normal.xyz, -lvec);
	     lintensity = half_lambert(lintensity);
	     lcolor *= lintensity;
	             tot_diffuse += lcolor;
	 lhalf = normalize(lvec - vec3(0, 1, 0));
	     lspec = p3d_Material.specular;
	     lspec *= pow(clamp(dot(l_eye_normal.xyz, lhalf), 0, 1), shininess);
	     tot_specular += lspec;
	         }
	         else if (light_type[i] == LIGHTTYPE_SPOT) {
	             lpoint = p3d_ViewMatrix * vec4(light_pos[i], 1);
	             ldir = normalize((p3d_ViewMatrix * light_direction[i]));
	             lvec = lpoint.xyz - l_eye_position.xyz;
	             ldist = length(lvec);
	             lvec = normalize(lvec);
	             lintensity = dot(l_eye_normal.xyz, lvec);
	     lintensity = half_lambert(lintensity);
	             float dot2 = dot(lvec, normalize(-ldir.xyz));
	             if (dot2 <= latten.z) { /* outside light cone */ continue; }
	             float denominator = ldist * latten.x;
	             lattenv = lintensity * dot2 / denominator;
	             if (dot2 <= latten.y) { lattenv *= (dot2 - latten.z) / (latten.y - latten.z); }
	             lcolor *= lattenv;
	             tot_diffuse += lcolor;
	 lhalf = normalize(lvec - vec3(0, 1, 0));
	     lspec = p3d_Material.specular;
	     lspec *= lattenv;
	     lspec *= pow(clamp(dot(l_eye_normal.xyz, lhalf), 0, 1), shininess);
	     tot_specular += lspec;
	         }
	 }
	 // Begin view-space light summation
	 result = vec4(0, 0, 0, 0);
	 result += tot_diffuse;
	 result += tot_rim;
	 // End view-space light summations
	 result *= p3d_ColorScale;
	 result.rgb *= tex0.rgb;
	 result.a = 0.5;
	 tot_specular *= p3d_Material.specular;
	 result.rgb += tot_specular.rgb;
	 o_color = result * 1.000001;
}
rgb;
	 o_color = result * 1.000001;
}
* 1.000001;
}
ult * 1.000001;
}
01;
	 // Shader disables alpha write.
}
	             lcolor *= lattenv;
	     lcolor *= lintensity;
	             tot_diffuse += lcolor;
	 lhalf = normalize(lvec - vec3(0, 1, 0));
	     lspec = p3d_Material.specular;
	     lspec *= lattenv;
	     lspec *= pow(clamp(dot(l_eye_normal.xyz, lhalf), 0, 1), shininess);
	     tot_specular += lspec;
	         }
	 }
	 // Begin view-space light summation
	 result = vec4(0, 0, 0, 0);
	 result += tot_diffuse;
	 result += tot_rim;
	 // End view-space light summations
	 result *= p3d_ColorScale;
	 result.rgb *= tex0.rgb;
	 result.rgb += tex1.rgb;
	 result.rgb += tex3.rgb;
	 tot_specular *= p3d_Material.specular;
	 result.rgb += tot_specular.rgb;
	 o_color = result * 1.000001;
}
rgb;
	 o_color = result * 1.000001;
}
esult * 1.000001;
}
