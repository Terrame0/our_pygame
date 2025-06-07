#version 430

// -- texture
layout(binding = 0) uniform sampler2D img;

in vec2 frag_texcoord;
in float depth;
out vec4 outColor;

void main() {
	outColor = texture(img,frag_texcoord);
}