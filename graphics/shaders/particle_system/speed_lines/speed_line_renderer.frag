#version 430

out vec4 frag_color;
in vec4 v_color;
in vec2 v_texcoord;
in vec2 v_quad_coord; 

void main() {
    float alpha = 1-length(v_quad_coord) > 0 ? 1 : 0;
    frag_color = v_color;
    frag_color.a *= alpha;
}