#version 330

uniform sampler2D sceneTexture;
uniform mat4 p3d_ModelViewProjectionMatrix;
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
out vec4 posPos;

#define subpixelShift 1.0 / 8.0

void main()
{
	gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
	
	vec2 winSize = textureSize(sceneTexture, 0).xy;
	vec2 rcpFrame = 1.0 / winSize;
	posPos.xy = p3d_MultiTexCoord0.xy;
	posPos.zw = p3d_MultiTexCoord0.xy - (rcpFrame * (0.5 + subpixelShift));
}
