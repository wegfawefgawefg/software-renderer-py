import math
from pprint import pprint
import pygame
import glm

pygame.init()

render_resolution = glm.vec2(240, 160)
window_size = render_resolution * 4

texture_path = "./box.png"


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
    denom = d00 * d11 - d01 * d01
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


def mouse_pos():
    return glm.vec2(pygame.mouse.get_pos()) / window_size * render_resolution


def draw(surface, texture):
    mouse = mouse_pos()
    # verts are in screenspace
    verts_a = [
        (100, 0),
        (0, 0),
        (0, 100),
    ]
    tex_coords_a = ((1, 0), (0, 0), (0, 1))

    verts_b = [
        (0, 100),
        # (100, 100),
        # mouse pos
        (mouse.x, mouse.y),
        (100, 0),
    ]
    tex_coords_b = ((0, 1), (1, 1), (1, 0))

    draw_texture_tri(
        surface,
        texture,
        verts_a,
        tex_coords_a,
    )
    draw_texture_tri(
        surface,
        texture,
        verts_b,
        tex_coords_b,
    )

    rect_size = glm.vec2(16, 16)
    center = render_resolution / 2
    rect_pos = center - rect_size / 2 + glm.vec2(32, 32)

    pygame.draw.circle(surface, (0, 255, 0), mouse_pos(), 3)


def main():
    window = pygame.display.set_mode(window_size.to_tuple())
    render_surface = pygame.Surface(render_resolution.to_tuple())

    texture = pygame.image.load(texture_path)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)
            ):
                running = False

        render_surface.fill((0, 0, 0))

        draw(render_surface, texture)

        stretched_surface = pygame.transform.scale(render_surface, window_size)
        window.blit(stretched_surface, (0, 0))
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
