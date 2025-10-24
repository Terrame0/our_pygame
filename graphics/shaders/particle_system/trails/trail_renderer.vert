#version 430

layout(location = 0) in vec4 quad_vertex;
layout(location = 1) in vec4 particle_position;
layout(location = 2) in vec4 particle_velocity;
layout(location = 3) in float particle_lifetime;
layout(location = 4) in uint particle_renderpass_id;

layout(std430, binding=0) buffer particle_renderpass_ids {
    uint renderpass_ids[];
};

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform uint current_renderpass;

// -=-=-=-=-

uniform vec3 trail_color;

out vec4 v_color;
out vec2 v_texcoord;

float pi = acos(0)*2;

void main() {
    if(particle_lifetime <= 0 || renderpass_ids[gl_InstanceID] != current_renderpass){
        gl_Position = vec4(2,0,0,1);
    }
    else{
        vec4 v_pos = vec4(quad_vertex.xyz/5,1);
        gl_Position = projection*view*(model*v_pos+particle_position);
        float lifetime_fade = cos(clamp(
            0.5 - particle_lifetime,0,1
        )*pi);
        v_color = vec4(trail_color,lifetime_fade);
    }
}