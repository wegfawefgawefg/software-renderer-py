import math
from pprint import pprint
import pygame
import glm

pygame.init()

render_resolution = glm.vec2(240, 160)
cut_factor = 2
render_resolution /= cut_factor
window_size = render_resolution * 4 * cut_factor
texture_path = "./box.png"


def gen_cube_verts():
    # return a list of vertices for a cube
    s = 1.0  # half size
    return [
        glm.vec3(-s, -s, -s),
        glm.vec3(s, -s, -s),
        glm.vec3(s, s, -s),
        glm.vec3(-s, s, -s),
        glm.vec3(-s, -s, s),
        glm.vec3(s, -s, s),
        glm.vec3(s, s, s),
        glm.vec3(-s, s, s),
    ]


def gen_cube_tri_indices():
    # Define the triangles by the indices of their vertices
    return [
        (0, 1, 2),
        (2, 3, 0),  # Front face
        (1, 5, 6),
        (6, 2, 1),  # Right face
        (5, 4, 7),
        (7, 6, 5),  # Back face
        (4, 0, 3),
        (3, 7, 4),  # Left face
        (3, 2, 6),
        (6, 7, 3),  # Top face
        (4, 5, 1),
        (1, 0, 4),  # Bottom face
    ]


def gen_cube_tex_coords():
    # Define texture coordinates for each vertex
    return [
        # front face
        ((0, 0), (1, 0), (1, 1)),
        ((1, 1), (0, 1), (0, 0)),
        # right face
        ((0, 0), (1, 0), (1, 1)),
        ((1, 1), (0, 1), (0, 0)),
        # back face
        ((0, 0), (1, 0), (1, 1)),
        ((1, 1), (0, 1), (0, 0)),
        # left face
        ((0, 0), (1, 0), (1, 1)),
        ((1, 1), (0, 1), (0, 0)),
        # top face
        ((0, 0), (1, 0), (1, 1)),
        ((1, 1), (0, 1), (0, 0)),
        # bottom face
        ((0, 0), (1, 0), (1, 1)),
        ((1, 1), (0, 1), (0, 0)),
    ]


def calc_normals(vertices, tri_indices):
    normals = []
    for tri in tri_indices:
        # Get the vertices of the triangle
        v0 = vertices[tri[0]]
        v1 = vertices[tri[1]]
        v2 = vertices[tri[2]]

        # Calculate two edges of the triangle
        edge1 = v1 - v0
        edge2 = v2 - v0

        # Calculate the cross product of the two edges
        normal = glm.cross(edge1, edge2)

        # Normalize the resulting vector
        normal = glm.normalize(normal)

        normals.append(normal)

    return normals


def transform(verts, tri_indices, pos, rot, scale, cam):
    # Setup the Model matrix
    model = glm.mat4(1)
    model = glm.translate(model, pos)
    model = glm.scale(model, scale)
    model = glm.rotate(model, rot, glm.vec3(0, 1, 0))

    # Setup the View matrix
    view = glm.lookAt(cam.pos, cam.target, glm.vec3(0, -1, 0))

    # Setup the Projection matrix
    aspect_ratio = render_resolution.x / render_resolution.y
    projection = glm.perspective(glm.radians(90.0), aspect_ratio, 0.1, 100.0)

    # Generate the Model-View-Projection (MVP) matrix
    mvp = projection * view * model

    # Apply MVP to each vertex
    transformed_verts = []
    for vert in verts:
        transformed_vert = mvp * glm.vec4(vert, 1.0)
        transformed_vert /= transformed_vert.w  # Perspective division
        transformed_verts.append(glm.vec3(transformed_vert))

    return transformed_verts


def sample_texture(texture, uv):
    uv = glm.vec2(uv[0] % 1, uv[1] % 1)
    tex_y = int(uv.x * texture.get_height())
    tex_x = int(uv.y * texture.get_width())

    # clamp tex_y and tex_x
    tex_y = min(max(tex_y, 0), texture.get_height() - 1)
    tex_x = min(max(tex_x, 0), texture.get_width() - 1)

    return texture.get_at((tex_x, tex_y))


def barycentric(verts, p):
    v0 = glm.vec2(verts[2]) - glm.vec2(verts[0])
    v1 = glm.vec2(verts[1]) - glm.vec2(verts[0])
    v2 = glm.vec2(p) - glm.vec2(verts[0])
    d00 = glm.dot(v0, v0)
    d01 = glm.dot(v0, v1)
    d11 = glm.dot(v1, v1)
    d20 = glm.dot(v2, v0)
    d21 = glm.dot(v2, v1)
    denom = d00 * d11 - d01 * d01 + 0.0001
    u = (d11 * d20 - d01 * d21) / denom
    v = (d00 * d21 - d01 * d20) / denom
    return glm.vec3(u, v, 1 - u - v)


def draw_texture_tri(surface, texture, verts, tex_coords):
    min_x = min(v[0] for v in verts)
    max_x = max(v[0] for v in verts)
    min_y = min(v[1] for v in verts)
    max_y = max(v[1] for v in verts)
    # clamp min and max to surface size
    min_x = max(min_x, 0)
    min_y = max(min_y, 0)
    max_x = min(max_x, surface.get_width() - 1)
    max_y = min(max_y, surface.get_height() - 1)

    for x in range(int(min_x), int(max_x) + 1):
        for y in range(int(min_y), int(max_y) + 1):
            p = glm.vec2(x, y)
            bc = barycentric(verts, p)
            if min(bc.x, bc.y, bc.z) < -0.001:
                continue
            uv = (
                glm.vec3(*tex_coords[0], 0) * bc.x
                + glm.vec3(*tex_coords[1], 0) * bc.y
                + glm.vec3(*tex_coords[2], 0) * bc.z
            )
            color = sample_texture(texture, uv.to_tuple())
            surface.set_at((x, y), color)


def draw_cube(
    surface,
    transformed_verts,
    cube_tex_coords,
    tri_indices,
    normals,
    texture,
):
    # Convert the vertices from normalized device coordinates to window coordinates
    transformed_verts = [
        (render_resolution.x * (v.x + 1) / 2, render_resolution.y * (1 - (v.y + 1) / 2))
        for v in transformed_verts
    ]
    for i in range(len(tri_indices)):
        # Back-face culling: Only draw the triangle if it's facing towards the camera
        if normals[i].z < 0:
            draw_texture_tri(
                surface,
                texture,
                [transformed_verts[idx] for idx in tri_indices[i]],
                cube_tex_coords[i],
            )


def mouse_pos():
    return glm.vec2(pygame.mouse.get_pos()) / window_size * render_resolution


def draw(surface, texture, cam):
    # angle = pygame.time.get_ticks() / 1000.0
    angle = 0
    cube_verts = gen_cube_verts()
    cube_tri_indices = gen_cube_tri_indices()
    cube_tex_coords = gen_cube_tex_coords()

    # draw a bunch of cubes
    for z in range(0, 2):
        for x in range(0, 2):
            pos = glm.vec3(x * 3, 0, z * 3)
            transformed_vertices = transform(
                cube_verts,
                cube_tri_indices,
                # glm.vec3(0, 0, 0),
                pos,
                angle,
                glm.vec3(1, 1, 1),
                cam,
            )
            normals = calc_normals(transformed_vertices, cube_tri_indices)
            draw_cube(
                surface,
                transformed_vertices,
                cube_tex_coords,
                cube_tri_indices,
                normals,
                texture,
            )

    rect_size = glm.vec2(16, 16)
    center = render_resolution / 2
    rect_pos = center - rect_size / 2 + glm.vec2(32, 32)

    pygame.draw.circle(surface, (0, 255, 0), mouse_pos(), 3)


class Camera:
    def __init__(self, pos, target):
        self.pos = pos
        self.target = target


def main():
    window = pygame.display.set_mode(window_size.to_tuple())
    render_surface = pygame.Surface(render_resolution.to_tuple())
    texture = pygame.image.load(texture_path)

    cam = Camera(glm.vec3(0, 0, -3), glm.vec3(0, 0, 0))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE)
            ):
                running = False
            # scrolling should move the cam away from its target
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    cam.pos.z += 0.1
                if event.button == 5:
                    cam.pos.z -= 0.1

        # make cam go up if w pressed, and down if s pressed
        # via keypressed
        pressed = pygame.key.get_pressed()
        speed = 0.1
        if pressed[pygame.K_w]:
            cam.pos.y -= speed
        if pressed[pygame.K_s]:
            cam.pos.y += speed
        if pressed[pygame.K_a]:
            cam.pos.x -= speed
        if pressed[pygame.K_d]:
            cam.pos.x += speed
        # e and q for in and out
        if pressed[pygame.K_e]:
            cam.pos.z += speed
        if pressed[pygame.K_q]:
            cam.pos.z -= speed

        m_n = mouse_pos() / render_resolution * 2 - 1
        cam.target = glm.vec3(
            math.sin(m_n.x * math.pi),
            math.sin(m_n.y * math.pi),
            0,
        )

        render_surface.fill((0, 0, 0))

        draw(render_surface, texture, cam)

        stretched_surface = pygame.transform.scale(render_surface, window_size)
        window.blit(stretched_surface, (0, 0))
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
