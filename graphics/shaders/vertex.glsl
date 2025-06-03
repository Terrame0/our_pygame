#version 430

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
out float w;

void main() {
	// TODO vertex snapping is broken in perspective !!!
	vec4 clip_space = projection*view*model*vec4(position, 1.0);
	vec2 screen_space = round((clip_space.xy / clip_space.w) * screen_size / 4) / screen_size * 4 * clip_space.w;
	gl_Position = vec4(screen_space,clip_space.zw);
	frag_texcoord = texcoord;
}