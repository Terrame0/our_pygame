#version 430

void main() {
	gl_Position = vec4(vec2((gl_VertexID << 1) & 2, gl_VertexID & 2) * 2.0f + -1.0f, 0.0f, 1.0f);
}
