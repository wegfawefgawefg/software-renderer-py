import math
from pprint import pprint
import pygame
import glm

pygame.init()

render_resolution = glm.vec2(240, 160)
window_size = render_resolution * 4


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


def transform(verts, tri_indices, pos, rot, scale, cam_pos, cam_rot):
    # Setup the Model matrix
    model = glm.mat4(1)
    model = glm.translate(model, pos)
    model = glm.scale(model, scale)
    model = glm.rotate(model, rot, glm.vec3(0, 1, 0))

    # Setup the View matrix
    view = glm.lookAt(cam_pos, glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))

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


def draw_cube(
    surface,
    transformed_verts,
    tri_indices,
    normals,
    color,
):
    # Convert the vertices from normalized device coordinates to window coordinates
    transformed_verts = [
        (render_resolution.x * (v.x + 1) / 2, render_resolution.y * (1 - (v.y + 1) / 2))
        for v in transformed_verts
    ]
    pprint(transformed_verts)
    for i in range(len(tri_indices)):
        # Back-face culling: Only draw the triangle if it's facing towards the camera
        if normals[i].z < 0:
            pygame.draw.polygon(
                surface, color, [transformed_verts[idx] for idx in tri_indices[i]], 1
            )  # 1 for wireframe
            # draw_tri(
            #     surface,
            #     texture,
            #     [transformed_verts[idx] for idx in tri_indices[i]],
            #     tri_tex_coords[i],
            # )


def draw_tri(surface, texture, tri_verts, tri_tex_coords):
    pass


def mouse_pos():
    return glm.vec2(pygame.mouse.get_pos()) / window_size * render_resolution


def draw(surface):
    angle = pygame.time.get_ticks() / 1000.0
    cube_verts = gen_cube_verts()
    cube_tri_indices = gen_cube_tri_indices()
    transformed_vertices = transform(
        cube_verts,
        cube_tri_indices,
        glm.vec3(0, 0, 0),
        angle,
        glm.vec3(1, 1, 1),
        glm.vec3(0, 0, -3),
        glm.vec3(0, 0, 0),
    )
    normals = calc_normals(transformed_vertices, cube_tri_indices)
    draw_cube(surface, transformed_vertices, cube_tri_indices, normals, (255, 255, 255))

    rect_size = glm.vec2(16, 16)
    center = render_resolution / 2
    rect_pos = center - rect_size / 2 + glm.vec2(32, 32)

    pygame.draw.circle(surface, (0, 255, 0), mouse_pos(), 3)


def main():
    window = pygame.display.set_mode(window_size.to_tuple())
    render_surface = pygame.Surface(render_resolution.to_tuple())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)
            ):
                running = False

        render_surface.fill((0, 0, 0))

        draw(render_surface)

        stretched_surface = pygame.transform.scale(render_surface, window_size)
        window.blit(stretched_surface, (0, 0))
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
