#version 330

#pragma include "shaders/stdshaders/common_brdf_frag.inc.glsl"

in vec2 l_texcoord;

uniform sampler2D colorSampler;
uniform sampler2D depthSampler;
uniform sampler2D normalSampler;
uniform sampler2D armeSampler;

uniform vec3 params;
#define rtMaxLength params.x
#define rtMaxThickness params.y
#define reflectionEnhancer params.z

uniform vec4 wspos_camera;
uniform mat4 trans_clip_of_camera_to_world;
uniform mat4 trans_world_to_clip_of_camera;
uniform float osg_FrameTime;

out vec4 outputColor;

#define RAYTRACE_LOOP_COUNT 50

float noise(vec2 seed)
{
    return fract(sin(dot(seed.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

float ComputeDepth(vec4 clippos)
{
    return 0.5 * (clippos.z / clippos.w) + 0.5;
}

float GetDepth(vec2 uv)
{
    return texture(depthSampler, uv).r;
}

void main()
{
    vec2 texelSize = 1.0 / vec2(textureSize(colorSampler, 0));
    vec2 uv = gl_FragCoord.xy * texelSize;
    
    outputColor = vec4(0.0);
    
    vec4 normal_envmask = texture(normalSampler, uv);
    if (normal_envmask.a == 0)
    {
        return;
    }
    
    float depth = GetDepth(uv);
    if (depth >= 1.0)
    {
        return;
    }
        
    vec2 spos = 2.0 * uv - 1.0;
    vec4 pos = trans_clip_of_camera_to_world * vec4(spos, 2.0 * depth - 1, 1.0);
    pos = pos / pos.w;
    
    vec3 camDir = pos.xyz - wspos_camera.xyz;
    vec3 normal = normalize(normal_envmask.rgb * 2.0 - 1.0);
    vec3 refDir = normalize(reflect(camDir, normal));
    float NdotV = clamp(dot(normal, normalize(camDir)), 0, 1);
    
    vec4 armeParams = texture(armeSampler, uv);
    float roughness = armeParams.y;
    float metalness = armeParams.z;
    vec3 albedo = texture(colorSampler, uv).rgb;
    vec3 specularColor = mix(vec3(0.04), albedo, metalness);
    vec3 F = Fresnel_Schlick(specularColor, NdotV);
    
    int maxRayCount = RAYTRACE_LOOP_COUNT;
    float maxLength = rtMaxLength;
    vec3 step = (maxLength / maxRayCount) * refDir;
    float maxThickness = rtMaxThickness / maxRayCount;
    
    for (int n = 1; n <= maxRayCount; n++)
    {
        vec3 ray = (n + noise(uv + osg_FrameTime)) * step;
        vec3 rayPos = pos.xyz + ray;
        vec4 vpPos = trans_world_to_clip_of_camera * vec4(rayPos, 1.0);
        vec2 rayUv = 0.5 * (vpPos.xy / vpPos.w) + 0.5;

        if (max(abs(rayUv.x - 0.5), abs(rayUv.y - 0.5)) > 0.5)
        {
            break;
        }
            
        float rayDepth = ComputeDepth(vpPos);
        float gbufferDepth = GetDepth(rayUv);
        
        if (rayDepth - gbufferDepth > 0 && rayDepth - gbufferDepth < maxThickness)
        {
            float edgeFactor = 1.0 - pow(2.0 * length(rayUv - 0.5), 2);
            float ssrFactor = pow(min(1.0, (maxLength / 2) / length(ray)), 2.0) * edgeFactor;
            ssrFactor *= pow(length(rayUv - 0.5) / 0.5, 0.5);
            
            vec3 spec = textureLod(colorSampler, rayUv, roughness * 20).rgb;
            spec *= EnvironmentBRDF(roughness, NdotV, F);
            spec *= ssrFactor;
            
            outputColor = vec4(spec, 1.0);
            
            break;
        }
    }
    
}
