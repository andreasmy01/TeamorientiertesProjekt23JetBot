import math

import torch
from torch import Tensor
from torch2trt import TRTModule

from libjetbot.ExtendedRobot import Handle, ReturnData, ReturnCommand, State


class RoadFollowingHandle(Handle):
    def __init__(self, path_to_model):
        self._model = TRTModule()
        self._model.load_state_dict(torch.load(path_to_model))
        self._angle = 0.0
        self._is_stopped = False
        self._steer_gain = 0.03     # for smooth steering corrections
        self._steer_kd_gain = 0.0   # for harsh steering corrections instead of snake-like movements
        self._steer_bias = 0.0      # bias between left and right motor
        self._speed_control = 0.12  # default starting speed
        self._state = None

    # calculate PoI and set motor speeds accordingly to drive curves
    def execute(self, image, state: State) -> ReturnData:
        self._state = state
        
        x, y = self.get_road_direction(image)
        self._speed_control = self._state.max_speed
        
        self.adapt_thresholds_to_speed()
        
        self._angle, left, right = self.calculate_speed(self._angle, x, y)
        return ReturnData(
            command=None,
            max_speed=None,
            angle=self._angle,
            left=left,
            right=right
        )

    # higher speeds require harder steering
    def adapt_thresholds_to_speed(self):   
        if self._state.max_speed < 0.14:
            self._steer_gain = 0.025
            self._steer_kd_gain = 0.00
        elif self._state.max_speed < 0.15:
            self._steer_gain = 0.03
            self._steer_kd_gain = 0.005
        else:
            self._steer_gain = 0.04
            self._steer_kd_gain = 0.005


    def get_road_direction(self, image_preproc) -> (float, float):
        model_xy = self._model(image_preproc).detach().float().cpu().numpy().flatten()
        return model_xy[0], (0.5 - model_xy[1]) / 2.0

    def calculate_speed(self, last_angle: float, x: float, y: float) -> (float, float, float):
        angle = math.atan2(x, y)
        pid = angle * self._steer_gain + (angle - last_angle) * self._steer_kd_gain
        steer_val = pid + self._steer_bias
        left = max(min(self._speed_control + steer_val, 1.0), 0.0)
        right = max(min(self._speed_control - steer_val, 1.0), 0.0)
        return angle, left, right
