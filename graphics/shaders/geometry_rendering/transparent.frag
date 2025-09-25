#version 460
#extension GL_ARB_bindless_texture : require

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

layout(std430, binding=1) buffer texture_handle_buffer {
    sampler2D texture_handles[];
};

flat in uint object_id;
in vec2 frag_texcoord;
in vec3 frag_normal;

layout(location=0) out vec4 accumulation;
layout(location=1) out float revealage;

float pi = acos(0) * 2;

float saturate(float v){
    return clamp(v,0,1);
}

// -- a function that computes the weight of a fragment
// -- based on its alpha and depth values (for WBOIT)
float weight(float alpha) {
    float z = gl_FragCoord.z;
    float z_factor = pow(1.0 - z, 3.0);
    float a_factor = pow(clamp(alpha * 10.0, 0.01, 1.0), 3.0);
    return clamp(z_factor * a_factor * 1e8, 1e-2, 3e2);
}

void main() {
    uint texture_id = object_data[object_id].texture_id;
    vec4 frag_color = texture(texture_handles[texture_id],frag_texcoord);

    // -- writing to the accumulation and revealage targets (for WBOIT)
    float a = frag_color.a * 0.3;
    float w = weight(a);
    accumulation = vec4(frag_color.rgb * a * w, a * w);
    revealage = a;
}