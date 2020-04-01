#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
uniform vec4 wspos_view;
in vec4 p3d_Vertex;

out vec3 l_worldEyeToVert;

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
	
	vec4 worldPosition = p3d_ModelMatrix * p3d_Vertex;
    l_worldEyeToVert = worldPosition.xyz - wspos_view.xyz;
}
