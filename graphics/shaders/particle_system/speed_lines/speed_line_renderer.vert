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

uniform vec4 player_velocity;
uniform uvec2 screen_size;

out vec4 v_color;
out vec2 v_texcoord;
out vec2 v_quad_coord;

float pi = acos(0)*2;

void main() {
    if(particle_lifetime <= 0 || renderpass_ids[gl_InstanceID] != current_renderpass){
        gl_Position = vec4(0,0,0,1);
    }
    else{
        // -- coordinates relative to quad
        v_quad_coord = quad_vertex.xy;

        // -- vertex position
        vec4 v_pos = vec4(quad_vertex.xyz/80,1);
        gl_Position = projection*view*(model*v_pos+particle_position);

        // -- color calculation
        float lifetime_fade = sin(clamp(
            particle_lifetime,0,1
        )*pi);
        float velocity_fade = clamp(
            length(player_velocity.xyz/6),0,1
        );
        v_color = vec4(vec3(1),lifetime_fade*velocity_fade);
    }
}