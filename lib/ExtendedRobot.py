import math
import time
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
    def execute(self, models: {}, image, tensor: Tensor, previous_values: list) -> ReturnData:
        pass


class ExtendedRobot(Robot):
    camera = None
    models = {}
    handels: list = []
    state = None
    device = None
    a = 0
    stop_counter = 0
    stop_limit = 10

    # field properties
    steer_gain = 0
    steer_kd_gain = 0
    steer_bias = 0
    speed_control = 0.1

    # global const vars
    mean = None
    std = None

    def __init__(self, camera: Camera, models: {}, device=torch.device("cpu"), *args, **kwargs):
        super(ExtendedRobot, self).__init__(*args, **kwargs)
        self.camera = camera
        self.models = models
        self.device = device
        self.mean = torch.Tensor([0.485, 0.456, 0.406]).half().float().to(device)
        self.std = torch.Tensor([0.229, 0.224, 0.225]).half().float().to(device)

    def start(self):
        self.camera.observe(self.execute, names='value')

    def stop(self):
        self.camera.unobserve(self.execute, names='value')
        time.sleep(0.1)
        super().stop()

    def destroy(self):
        self.camera.stop()

    def execute(self, change):
        image = change['new']
        tensor = self.preprocess(image).to(self.device)
        return_values: list = []
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
            return_values.append(return_data)

        last: ReturnData = return_values.pop()
        x, y = last.poi
        self.a, left, right = self.calculate_speed(self.a, x, y)
        self.left_motor.value = left
        self.right_motor.value = right

    def register(self, handel: Handel):
        self.handels.append(handel)

    def unregister(self, handel: Handel):
        self.handels.remove(handel)

    def preprocess(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.to_tensor(image).to(self.device)
        image.sub_(self.mean[:, None, None]).div_(self.std[:, None, None])
        return image[None, ...]

    def calculate_speed(self, last_a: float, x_in: float, y_in: float) -> (float, float, float):
        a: float = math.atan2(x_in, y_in)
        pid: float = a * self.steer_gain + (a - last_a) * self.steer_kd_gain
        steer_val: float = pid + self.steer_bias
        left: float = max(min(self.speed_control + steer_val, 1.0), 0.0)
        right: float = max(min(self.speed_control - steer_val, 1.0), 0.0)
        # TODO: apply speed limit here
        return a, left, right
