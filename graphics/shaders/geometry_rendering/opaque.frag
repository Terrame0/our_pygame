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

layout(location=2) out vec4 color;

float pi = acos(0) * 2;

float saturate(float v){
    return clamp(v,0,1);
}

void main() {
    uint texture_id = object_data[object_id].texture_id;
    vec4 frag_color = texture(texture_handles[texture_id],frag_texcoord);
    
    // -- diffuse intensity calculation
    vec3 normal = normalize(frag_normal);
    vec3 sun = normalize(vec3(1,1,0));
    float diffuse_intensity = dot(sun,normal);

    
    // -- specular intensity calculation
    vec3 h = normalize(-view_vector.xyz + sun); // -- halfway vector
    float cosine = dot(h,frag_normal);
    float specular_intensity = pow(saturate(cosine),20);
    
    // -- cel shading application
    if(diffuse_intensity < -0.5) frag_color.rgb *= 0.4;
    else if(diffuse_intensity < 0) frag_color.rgb *= 0.6;
    else if(diffuse_intensity < 0.5) frag_color.rgb *= 0.8;
    else frag_color.rgb *= 1;

    // -- opaque color
    color = frag_color;
}