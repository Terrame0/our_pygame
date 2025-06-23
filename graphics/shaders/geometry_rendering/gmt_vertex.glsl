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

// -- camera rotation
layout(location = 4) uniform mat4 camera_rotation;

// -- outputs to fragment shader 
out float depth;
out float w;

out vec3 frag_position;
out vec2 frag_texcoord;
out vec3 frag_normal;

void main() {
	// -- converting normals to clip space
	frag_normal = mat3(model) * normal;

	// -- converting vertices to clip space
	vec4 clip_space = projection*view*model*vec4(position, 1.0);
	depth = clip_space.z;

	// -- vertex jittering
	vec2 screen_space = round((clip_space.xy / clip_space.w) * screen_size / 4) / screen_size * 4 * clip_space.w;
	gl_Position = vec4(screen_space,clip_space.zw);
	frag_position = vec3(screen_space.xy,clip_space.z);
	frag_texcoord = texcoord;
}