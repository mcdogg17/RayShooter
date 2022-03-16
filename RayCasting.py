from math import atan2, cos, sin, sqrt
from numba import njit


@njit(fastmath=True)
def ray_cycle(player_x, player_y, view_angle, obstacles, tile_w, tile_h, map_w, map_h, fov):
    rounded_x = (player_x // tile_w) * tile_w
    rounded_y = (player_y // tile_h) * tile_h
    coords = []

    for alpha in range(-fov, fov + 1):  # Цикл по углу обзора
        alpha = view_angle + alpha / 100
        sin_a = sin(alpha) if sin(alpha) else 0.000001
        cos_a = cos(alpha) if cos(alpha) else 0.000001
        ray_x, ray_y = player_x, player_y

        # Пересечение по вертикали
        ray_x, dx = (rounded_x + tile_w, 1) if cos_a >= 0 else (rounded_x, -1)
        found = False
        for _ in range(0, map_w * tile_w, tile_w):
            length_v = (ray_x - player_x) / cos_a
            ray_y = player_y + length_v * sin_a

            for ox, oy, map_w, map_h in obstacles:
                if ox <= ray_x <= ox + map_w and oy <= ray_y <= oy + map_h:
                    found = True
                    break
            if found:
                break
            ray_x += tile_w * dx
        res_v = (int(ray_x), int(ray_y), length_v)

        # Пересечение по горизонтали
        ray_y, dy = (rounded_y + tile_h, 1) if sin_a >= 0 else (rounded_y, -1)
        found = False
        for _ in range(0, map_h * tile_h, tile_h):
            length_h = (ray_y - player_y) / sin_a
            ray_x = player_x + length_h * cos_a

            for ox, oy, map_w, map_h in obstacles:
                if ox <= ray_x <= ox + map_w and oy <= ray_y <= oy + map_h:
                    found = True
                    break
            if found:
                break
            ray_y += tile_h * dy
        res_h = (int(ray_x), int(ray_y), length_h)

        res = (res_v[0], res_v[1]) if res_v[2] <= res_h[2] else (res_h[0], res_h[1])

        if (len(coords) > 1 and (coords[-1][0] == res[0] and coords[-2][0] == res[0] or
                                 coords[-1][1] == res[1] and coords[-2][1] == res[1])):
            coords[-1] = res
        else:
            coords.append(res)
    return coords


@njit(fastmath=True)
def in_view(x1, y1, x2, y2, obstacles):
    # Рейкаст, но с 1-ой линией, для проверки нахождения объекта в зоне видимости
    phi = atan2(y2 - y1, x2 - x1)
    cos_phi = cos(phi)
    sin_phi = sin(phi)
    distance = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    length = 0
    while distance > 1:
        ray_x = x1 + length * cos_phi
        ray_y = y1 + length * sin_phi
        distance = sqrt((ray_x - x2) ** 2 + (ray_y - y2) ** 2)

        for ox, oy, map_w, map_h in obstacles:
            if ox < ray_x < ox + map_w and oy < ray_y < oy + map_h:
                return False
        length += 1

    return True
