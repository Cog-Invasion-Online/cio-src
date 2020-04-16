#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec4 texcoord;

out vec2 l_texcoord;

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    l_texcoord = texcoord.xy;
}
