#version 430
layout(binding = 0) uniform sampler2D tex;
out vec4 frag_color;

void main() {
    frag_color = texture(tex,gl_FragCoord.xy/vec2(800,600));
}