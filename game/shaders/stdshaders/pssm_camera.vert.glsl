#version 330

#pragma include "shaders/stdshaders/common_animation_vert.inc.glsl"

uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;

in vec2 texcoord;
out vec2 geo_uv;

void main()
{
    vec4 finalVertex = p3d_Vertex;
    #if HAS_HARDWARE_SKINNING
        vec3 foo = vec3(0);
        DoHardwareAnimation(finalVertex, foo, p3d_Vertex, foo);
    #endif
    
    // move vertex into world space
    // as the geometry shader will multiply the vertex
    // by the world space view projection matrix of each pssm split
    gl_Position = p3d_ModelMatrix * finalVertex;
    
    geo_uv = texcoord;
}
