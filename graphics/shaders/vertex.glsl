#version 460

// -- vertex attributes
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texcoord;
layout(location = 2) in vec3 normal;

// -- model specific parameters
layout(location = 1) uniform mat4 model;
layout(location = 2) uniform mat4 projection;

// -- outputs to fragment shader 
out vec2 frag_texcoord;

void main() {
	gl_Position = projection*model*vec4(position, 1.0);
	frag_texcoord = texcoord;
}