#version 460
#extension GL_ARB_shader_draw_parameters : require

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

flat out uint object_id;
out vec2 frag_texcoord;
out vec3 frag_normal;

void main() {

    object_id = gl_BaseInstanceARB + gl_InstanceID;

    mat4 model = object_data[gl_BaseInstanceARB + gl_InstanceID].model_matrix;
    // -- converting normals to clip space
    frag_normal = normalize(mat3(model) * normal);

    // -- converting vertices to clip space
    vec4 clip_space = projection*view*model*vec4(position, 1.0);

    // -- vertex jittering
    //vec2 screen_space = round((clip_space.xy / clip_space.w) * window_size / 2) / window_size * 2 * clip_space.w;
    // gl_Position = vec4(screen_space,clip_space.zw);
    gl_Position = clip_space;

    frag_texcoord = texcoord;
}