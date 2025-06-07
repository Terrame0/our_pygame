#version 430
// -- TODO remember to change back to a higher value
layout(local_size_x = 64) in;

layout(std430, binding = 0) buffer vertices {
    float vert_array[];
};

layout(std430, binding = 1) buffer indices {
    int idx_array[];
};

layout(std430, binding = 2) buffer result {
    vec4 result_array[];
};

layout(location = 0) uniform vec3 camera_pos;

uint inv_id = gl_GlobalInvocationID.x;


vec3 get_vert(uint offset){
    int idx = idx_array[inv_id*3+offset];
    vec3 vert;
    for(int j = 0; j < 3; j++){vert[j] = vert_array[idx*8+j];}
    return vert;
}

vec3 get_normal(uint offset){
    int idx = idx_array[inv_id*3+offset];
    vec3 vert;
    for(int j = 0; j < 3; j++){vert[j] = vert_array[idx*8+j+3];}
    return vert;
}

vec4 distance_to_segment(vec3 P, vec3 A, vec3 B) {
    vec3 AB = B - A;
    vec3 AP = P - A;
    
    float len_sq = dot(AB, AB);
    if(len_sq < 1e-8) return vec4(distance(P, A),P - A);
    
    float t = dot(AP, AB) / len_sq;
    t = clamp(t, 0.0, 1.0);
    
    vec3 Q = A + t * AB;
    return vec4(distance(P, Q),P - Q); // returns QP
}

vec4 distance_to_triangle(vec3 P, vec3 v0, vec3 v1, vec3 v2) {
    vec3 ab = v1 - v0;
    vec3 ac = v2 - v0;
    vec3 normal = normalize(cross(ab, ac));
    
    vec3 plane_point = P - dot(P - v0, normal) * normal;
    
    vec3 v0p = plane_point - v0;
    float d00 = dot(ab, ab);
    float d01 = dot(ab, ac);
    float d11 = dot(ac, ac);
    float d20 = dot(v0p, ab);
    float d21 = dot(v0p, ac);
    float denom = d00 * d11 - d01 * d01;
    
    if(abs(denom) < 1e-8) {
        vec4 d0 = distance_to_segment(P, v0, v1);
        vec4 d1 = distance_to_segment(P, v1, v2);
        vec4 d2 = distance_to_segment(P, v2, v0);

        return (d0.x < d1.x) ? (d0.x < d2.x ? d0 : d2) : (d1.x < d2.x ? d1 : d2);
    }
    
    float u = (d11 * d20 - d01 * d21) / denom;
    float v = (d00 * d21 - d01 * d20) / denom;
    float w = 1.0 - u - v;
    
    if (u >= 0.0 && v >= 0.0 && w >= 0.0) {
        return vec4(distance(P, plane_point), P - plane_point);
    }
    
    vec4 d0 = distance_to_segment(P, v0, v1);
    vec4 d1 = distance_to_segment(P, v1, v2);
    vec4 d2 = distance_to_segment(P, v2, v0);
    
    return (d0.x < d1.x) ? (d0.x < d2.x ? d0 : d2) : (d1.x < d2.x ? d1 : d2);

}

void main() {
    vec3[3] vertices;
    vec3 face_normal;
    // -- the shader is dispatched for each face, so we have to iterate over 3 vertices
    // -- inv_id is multiplied by 3 for the very same reason
    for(int i = 0; i < 3; i++){
        vertices[i] = get_vert(i);
        face_normal += get_normal(i);
        }
     face_normal /= 3.0;

    result_array[inv_id] = distance_to_triangle(camera_pos,vertices[0],vertices[1],vertices[2]);
}