#version 430

// -- texture
layout(binding = 0) uniform sampler2D img;

in float depth;

in vec3 frag_position;
in vec2 frag_texcoord;
in vec3 frag_normal;

out vec4 frag_color;

float pi = acos(0) * 2;

void main() {
	frag_color = texture(img,frag_texcoord);

	
	vec3 view = normalize(frag_position);
	vec3 normal = normalize(frag_normal);





	//frag_color.xyz = mix(frag_color.xyz,vec3(1), depth/100);
}