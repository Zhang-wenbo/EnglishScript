import json


class Point:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return json.dumps({'x': self.x, 'y': self.y})

    def to_dict(self):
        return {'x': self.x, 'y': self.y}


class Color:
    def __init__(self, color: str):
        self.r = int(color[1:3], 16)
        self.g = int(color[3:5], 16)
        self.b = int(color[5:], 16)

    def to_rgb(self):
        return [self.r, self.g, self.b]


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Point:
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return json.dumps({'x': self.x, 'y': self.y})

    def to_dict(self):
        return {'x': self.x, 'y': self.y}


class OcrRes:
    def __init__(self, text: str = None, confidence: float = None, region_position: list = None):
        self.text = text
        self.confidence = float(confidence)
        self.region_position = region_position
        if self.region_position:
            self.center_x = region_position[2][0] - region_position[0][0]
            self.center_y = region_position[2][1] - region_position[0][1]


    def to_dict(self):
        return {'text': self.text, 'confidence': self.confidence, 'region_position': self.region_position}

    def __str__(self):
        return self.to_dict().__str__()

