#version 460
layout(binding = 0) uniform sampler2D accumulation;
layout(binding = 1) uniform sampler2D revealage;
layout(binding = 2) uniform sampler2D color;

layout(std140, binding = 0) uniform camera_data {  
    mat4 projection;
    mat4 view;
    vec2 window_size;
    vec4 view_vector;
};  

out vec4 frag_color;

void main() {
    vec2 tex_coord = gl_FragCoord.xy/window_size;
    vec4 accum = texture(accumulation, tex_coord);
    float reveal = texture(revealage, tex_coord).r;
    vec4 col = texture(color, tex_coord);
        
    float inv_accum_w = (accum.a > 1e-5) ? 1.0 / accum.a : 0.0;
    vec3 out_color = accum.rgb * inv_accum_w;
    
    // -- final composite
    frag_color = vec4(out_color, 1.0 - reveal);
}