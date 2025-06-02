#version 460

// -- vertex attributes
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texcoord;
layout(location = 2) in vec3 normal;

// -- constants
layout(location = 0) uniform vec2 screen_size; 

// -- model specific parameters
layout(location = 1) uniform mat4 model;
layout(location = 2) uniform mat4 projection;
layout(location = 3) uniform mat4 view;

// -- outputs to fragment shader 
out vec2 frag_texcoord;

void main() {
	// TODO vertex snapping is broken in perspective !!!
	vec4 screen_space = projection*view*model*vec4(position, 1.0);
	screen_space.xy = round(screen_space.xy * screen_size / 2) / screen_size * 2;
	gl_Position = screen_space;
	frag_texcoord = texcoord;
}