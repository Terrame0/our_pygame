#version 460
#extension GL_ARB_shader_draw_parameters : require
#extension GL_ARB_bindless_texture : require

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texcoord;
layout(location = 2) in vec3 normal;

layout(std140, binding = 0) uniform camera_data {  
    mat4 projection;
    mat4 view;
    vec2 window_size;
    vec4 view_vector;
};  

struct object_data_struct{
    mat4 model_matrix;
    uint texture_id;
};

layout(std430, binding=0) buffer object_data_buffer {
    object_data_struct object_data[];
};

void main() {

    uint object_id = gl_BaseInstanceARB + gl_InstanceID;

    mat4 model = object_data[gl_BaseInstanceARB + gl_InstanceID].model_matrix;

    // -- converting vertices to clip space
    vec4 clip_space = projection*view*model*vec4(position, 1.0);
    gl_Position = clip_space;
}