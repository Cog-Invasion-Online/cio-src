#version 330

const int NUM_SPLITS = 3;

uniform mat4 split_mvps[NUM_SPLITS];

layout(triangles) in;
layout(triangle_strip, max_vertices = 9) out; // NUM_SPLITS * 3

in vec2 geo_uv[];
out vec2 l_uv;

void main()
{
	// for each CSM split
	for (int i = 0; i < NUM_SPLITS; i++)
	{
		gl_Layer = i;
		for (int j = 0; j < 3; j++)
		{
			// project this vertex into clip space of this cascade camera
			gl_Position = split_mvps[i] * gl_in[j].gl_Position;
			l_uv = geo_uv[j];
			EmitVertex();
		}
		EndPrimitive();
	}
}
