import math

import torch
from torch import Tensor
from torch2trt import TRTModule

from libjetbot.ExtendedRobot import Handle, ReturnData, ReturnCommand, State


class RoadFollowingHandle(Handle):
    def __init__(self, path_to_model):
        self._model = TRTModule()
        self._model.load_state_dict(torch.load(path_to_model))
        self._a = 0.0
        self._is_stopped = False
        self._steer_gain = 0.0
        self._steer_kd_gain = 0.0
        self._steer_bias = 0.0
        self._speed_control = 0.1

    def execute(self, image, tensor: Tensor, previous_values: list, state: State) -> ReturnData:
        x, y = self.get_road_direction(tensor)
        self._speed_control = state.max_limit
        self._a, left, right = self.calculate_speed(self._a, x, y)
        return ReturnData(
            command=ReturnCommand.CONTINUE,
            alpha=self._a,
            left=left,
            right=right
        )

    def get_road_direction(self, tensor) -> (float, float):
        model_xy = self._model(tensor).detach().float().cpu().numpy().flatten()
        return model_xy[0], (0.5 - model_xy[1]) / 2.0

    def calculate_speed(self, last_a: float, x: float, y: float) -> (float, float, float):
        if self._is_stopped:
            return 0.0, 0.0, 0.0
        a = math.atan2(x, y)
        pid = a * self._steer_gain + (a - last_a) * self._steer_kd_gain
        steer_val = pid + self._steer_bias
        left = max(min(self._speed_control + steer_val, 1.0), 0.0)
        right = max(min(self._speed_control - steer_val, 1.0), 0.0)
        return a, left, right
