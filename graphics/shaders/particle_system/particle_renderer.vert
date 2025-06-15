#version 430

layout(location = 0) in vec4 quad_vertex;
layout(location = 1) in vec4 particle_position;
layout(location = 2) in vec4 particle_velocity;
layout(location = 3) in float particle_lifetime;

layout(location = 0) uniform mat4 projection;
layout(location = 1) uniform mat4 view;
layout(location = 2) uniform mat4 model;

out vec4 v_color;
void main() {
    if(particle_lifetime <= 0){
        gl_Position = vec4(2,0,0,1);
    }
    else{
        gl_Position = projection*view*(model*quad_vertex+particle_position);
        v_color = gl_Position;
    }
}