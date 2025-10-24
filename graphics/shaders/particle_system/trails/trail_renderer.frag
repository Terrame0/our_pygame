#version 430

out vec4 frag_color;
in vec4 v_color;
in vec2 v_texcoord;


void main() {
    frag_color = v_color;
}