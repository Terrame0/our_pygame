#version 430
layout(local_size_x = 16, local_size_y = 16) in;

layout(binding = 0) uniform sampler2D depth;
layout(rgba32f, binding = 0) uniform image2D img_in;
layout(rgba32f, binding = 1) uniform image2D img_out;

layout(location = 0) uniform mat4 projection;
layout(location = 1) uniform mat4 view;
layout(location = 2) uniform float near_plane;
layout(location = 3) uniform float far_plane;


vec4 load(ivec2 coord) {
    return imageLoad(img_in, coord);
}

void store(ivec2 coord, vec4 data) {
    imageStore(img_out, coord, data);
}

vec3 world_to_screen(vec3 world_pos) {
    vec4 clip_pos = projection * view * vec4(world_pos, 1.0);
    if (clip_pos.w <= 0.0) return vec3(-1.0);
    clip_pos.xyz /= clip_pos.w;
    return vec3((clip_pos.xyz + 1.0) * 0.5);
}

float linearize_depth(float depth) {
    return (2.0 * near_plane) / (far_plane + near_plane - depth * (far_plane - near_plane));
}

ivec2 inv_id = ivec2(gl_GlobalInvocationID.xy);

void main() {
    vec4 current_color = load(inv_id);
    vec2 screen_coord = vec2(inv_id) / vec2(800.0, 600.0);
    
    // Get particle position in screen space [0,1]
    vec3 particle_screen = world_to_screen(vec3(0.0, 3.0, 0.0));
    
    // Skip if particle is behind camera
    if (particle_screen.x < 0.0) {
        store(inv_id, current_color);
        return;
    }
    
    // Calculate distance in screen space
    float dist = distance(particle_screen.xy, screen_coord)*linearize_depth(particle_screen.z);
    
    // Create glow effect
    float glow = exp(-dist*1000); // Exponential falloff
    vec4 glow_color = vec4(1.0, 1.0, 0.0, 1.0) * glow;
    
    // Sample depth and check if particle is visible
    float depth_value = texture(depth, screen_coord).r;
    float particle_depth = particle_screen.z;
    
    // Only add glow if particle is in front of scene geometry
    if (particle_screen.z >= depth_value) {
        glow_color = vec4(0.0);
    }
    
    //store(inv_id,  vec4(particle_screen.z,depth_value,0,1));
    store(inv_id,  glow_color);
}