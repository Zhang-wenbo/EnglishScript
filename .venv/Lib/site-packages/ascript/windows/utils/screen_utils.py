from PIL.Image import Image

from ascript.windows.daos.screen import Point, Color


def find_colors(colors: str, sim: float, max_points: int, ore: int, img: Image, space: int) -> list:
    sim_space = 255 * (1 - sim)
    cs = colors.split('|')
    points = [None] * len(cs)
    for i in range(len(cs)):
        c = cs[i].split(',')
        if i == 0:
            points[i] = {'x': int(c[0]), 'y': int(c[1]), 'color': Color(c[2]).to_rgb()}
        else:
            points[i] = {'x': int(c[0]) - points[0]['x'], 'y': int(c[1]) - points[0]['y'],
                         'color': Color(c[2]).to_rgb()}

    return native_find_colors(sim_space, max_points, ore, img, points, space)


def compare_colors(colors: str, sim: float, img: Image):
    sim_space = 255 * (1 - sim)
    cs = colors.split('|')
    points = [None] * len(cs)
    for i in range(len(cs)):
        c = cs[i].split(',')
        points[i] = {'x': int(c[0]), 'y': int(c[1]), 'color': Color(c[2]).to_rgb()}

    for p in points:
        color = img.getpixel([p['x'], p['y']])
        if not compare_color(color, p['color'], sim_space):
            return False

    return True


def native_find_colors(sim: float, max_points: int, ore: int, img: Image, points: list, space: int) -> list:
    width = img.width
    height = img.height
    pixs = list(img.getdata())

    # print(len(pixs), width, height)

    fcs = []

    # print(ore)

    if ore == 1:
        for w in range(width):
            for h in range(height):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    if ore == 2:
        for h in range(height):
            for w in range(width):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    if ore == 3:
        for h in range(height):
            for w in reversed(range(width)):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    if ore == 4:
        for w in reversed(range(width)):
            for h in range(height):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    if ore == 5:
        for w in reversed(range(width)):
            for h in reversed(range(height)):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    if ore == 6:
        for h in reversed(range(height)):
            for w in reversed(range(width)):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    if ore == 7:
        for h in reversed(range(height)):
            for w in range(width):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    if ore == 8:
        for w in range(width):
            for h in reversed(range(height)):
                if check_color(width, height, pixs, w, h, points, sim):
                    fcs.append(Point(w, h))
                    if len(fcs) >= max_points != -1:
                        return fcs
                    space_image(pixs, space, width, height, w, h)

    return fcs


def space_image(pixs, space, width, height, w, h):
    x = w - space
    while x < w + space:
        x = x + 1
        if -1 < x < width:
            y = h - space
            while y < h + space:
                y = y + 1
                if x > -1 and y < height:
                    pixs[get_pix_forxy(width, x, y)] = [-1, -1, -1]


def check_color(width, height, pixs, x, y, points, sim):
    if compare_color(pixs[get_pix_forxy(width, x, y)], points[0]['color'], sim):

        i = 1
        while i < len(points):
            nx = points[i]['x'] + x
            ny = points[i]['y'] + y

            if nx < 0 or ny < 0 or nx >= width or ny >= height:
                return False

            if not (compare_color(pixs[get_pix_forxy(width, nx, ny)], points[i]['color'], sim)):
                return False

            i = i + 1

        return True

    return False


def get_pix_forxy(width, x, y):
    return width * y + x


def compare_color(c1, c2, sim):
    if c1[0] == -1:
        return False

    # print(c1,c2)

    if abs(c1[0] - c2[0]) <= sim and abs(c1[1] - c2[1]) <= sim and abs(c1[2] - c2[2]) <= sim:
        return True

    return False
