#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec4 texcoord;

out vec2 l_coordTap0;
out vec2 l_coordTap1;
out vec2 l_coordTap2;
out vec2 l_coordTap3;
out vec2 l_coordTap1Neg;
out vec2 l_coordTap2Neg;
out vec2 l_coordTap3Neg;

uniform vec2 vsTapOffsets[3];

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    
    l_coordTap0     = texcoord.xy;
    l_coordTap1     = texcoord.xy + vsTapOffsets[0];
    l_coordTap2     = texcoord.xy + vsTapOffsets[1];
    l_coordTap3     = texcoord.xy + vsTapOffsets[2];
    l_coordTap1Neg  = texcoord.xy - vsTapOffsets[0];
    l_coordTap2Neg  = texcoord.xy - vsTapOffsets[1];
    l_coordTap3Neg  = texcoord.xy - vsTapOffsets[2];
}
