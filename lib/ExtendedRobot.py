import math
from enum import Enum

import PIL
import torch
import torchvision.transforms as transforms
from torch import Tensor

from jetbot import Robot, Camera


class State:

    def __init__(self):
        self.max_limit = 1.0

    @property
    def max_limit(self) -> float:
        return self.max_limit

    @max_limit.setter
    def max_limit(self, value: float):
        self.max_limit = value


class ReturnCommand(Enum):
    CONTINUE = 0
    STOP = 1


class ReturnData:
    def __init__(self, command: ReturnCommand, poi: (float, float) = (0, 0)):
        self.command = command
        self.poi = poi

    @property
    def command(self) -> ReturnCommand:
        return self.command

    @command.setter
    def command(self, value):
        self.command = value

    @property
    def poi(self) -> (float, float):
        return self.poi

    @poi.setter
    def poi(self, value):
        self.poi = value


class Handel:
    def execute(self, models: {}, image: any, tensor: Tensor, previous_values: list[ReturnData]) -> ReturnData:
        pass


class ExtendedRobot(Robot):
    camera = None
    models = {}
    handels: list[Handel] = []
    state = None
    device = None
    a = 0
    stop_counter = 0
    stop_limit = 10

    # field properties
    steer_gain = 0
    steer_kd_gain = 0
    steer_bias = 0
    speed_control = 0

    def __init__(self, camera: Camera, models: {}, device=torch.device("cpu"), *args, **kwargs):
        super(Robot, self).__init__(*args, **kwargs)
        self.camera = camera
        self.models = models
        self.device = device

    def start(self):
        if self.camera is not None:
            self.camera.observe(self.execute, names='value')

    def stop(self):
        super(Robot).stop()
        self.camera.unobserve(self.execute, names='value')

    def execute(self, change):
        image = change['new']
        tensor = self.preprocess(image)
        return_values: list[ReturnData] = []
        for handel in self.handels:
            return_data: ReturnData = handel.execute(
                models=self.models,
                image=image,
                tensor=tensor,
                previous_values=return_values
            )
            if return_data.command == ReturnCommand.STOP:
                if self.stop_counter < self.stop_limit:
                    break
                else:
                    self.stop_counter = 0
            list.append(return_data)

        last: ReturnData = list.pop()
        x, y = last.poi
        self.a, left, right = self.calculate_speed(self.a, x, y)
        self.left_motor.value = left
        self.right_motor.value = right

    def register(self, handel: Handel):
        self.handels.append(handel)

    def unregister(self, handel: Handel):
        self.handels.remove(handel)

    mean = torch.Tensor([0.485, 0.456, 0.406]).half().float()
    std = torch.Tensor([0.229, 0.224, 0.225]).half().float()

    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image)
        image.sub_(self.mean[:, None, None]).div_(self.std[:, None, None])
        return image[None, ...]

    def calculate_speed(self, last_a: float, x_in: float, y_in: float) -> (float, float, float):
        a = math.atan2(x_in, y_in)
        pid = a * self.steer_gain + (a - last_a) * self.steer_kd_gain
        steer_val = pid + self.steer_bias
        left = max(min(self.speed_control + steer_val, 1.0), 0.0)
        right = max(min(self.speed_control - steer_val, 1.0), 0.0)
        return a, left, right
