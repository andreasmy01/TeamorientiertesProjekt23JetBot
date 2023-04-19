class DetectableObject:

    def __init__(self, type="Unknown Type", x_min=0, y_min=0, x_max=0, y_max=0, probability=0):
        self.type = type
        self.xMin = x_min
        self.yMin = y_min
        self.xMax = x_max
        self.yMax = y_max
        self.probability = probability

    def get_type(self):
        return self.type

    def get_width(self):
        return self.xMax - self.xMin

    def get_height(self):
        return self.yMax - self.yMin

    def get_probability(self):
        return self.probability

    def get_size(self):
        return self.get_height() * self.get_width()

    def get_xmax(self):
        return self.xmax

    def get_ymax(self):
        return self.ymax