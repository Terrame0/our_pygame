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

layout(location=2) out vec4 out_color;

float pi = acos(0) * 2;

float saturate(float v){
    return clamp(v,0,1);
}

float cdot(vec3 v1, vec3 v2){
    return max(dot(v1, v2), 0.f);
}

vec3 delinearize(vec3 color) {return pow(color, vec3(2.2));}

vec3 linearize(vec3 color) {return pow(color, vec3(1.0/2.2));}

void main() {
    uint texture_id = object_data[object_id].texture_id;

    float lightIntensity = 2;
    float metallic = 0.0;
    float roughness = 0.3;

    vec3 lightColor = vec3(1.f,1.f,1.f) * lightIntensity;
    vec3 objectColor = texture(texture_handles[texture_id],frag_texcoord).rgb;
    //objectColor = vec3(1,0,0);

    vec3 viewVec = -normalize(view_vector.xyz);
    vec3 sunVec = normalize(vec3(1,1,1));
    vec3 normalVec = normalize(frag_normal);
    vec3 halfwayVec = normalize(viewVec + sunVec);
    
    //indices of refraction 
    float n_air = 1.000293f;
    float n2 = 1.5f;

    //specular contribution with schlick's approximation
    float R0 = pow((n_air-n2)/(n_air+n2),2);

    float specularContribution = R0 + (1 - R0) * pow(1-cdot(sunVec, normalVec),5);
    
    //diffuse with lambertian model
    vec3 diffuse = objectColor;

    //normal distribution
    float a = pow(roughness,2);
    float a_sqr = pow(a,2);
    float D = a_sqr / max(pi * pow((pow(cdot(normalVec,halfwayVec),2) * (a_sqr - 1) + 1),2),0.001f);

    //geometry shading
    float k = a/2;
    float G = (cdot(normalVec,viewVec) / max((cdot(normalVec,viewVec) * (1 - k) + k),0.001f))
            * (cdot(normalVec,sunVec) / max((cdot(normalVec,sunVec) * (1 - k) + k),0.001f));

    //specular with cook-torrance model
    float specular = (D * G * specularContribution) / max(4 * cdot(viewVec,normalVec)*cdot(sunVec,normalVec),0.001f);

    //output color
    vec3 color = (vec3(saturate(specular))+clamp(diffuse*(1-specularContribution)*(1-metallic),0,1))*cdot(sunVec,normalVec);

    out_color = vec4(color,1.f);
}