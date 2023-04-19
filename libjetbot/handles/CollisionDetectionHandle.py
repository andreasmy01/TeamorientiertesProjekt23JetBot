import torch
import torch.nn.functional as functional
from torch import Tensor
from torch2trt import TRTModule

from libjetbot.ExtendedRobot import Handle, ReturnData, ReturnCommand


class CollisionDetectionHandle(Handle):

    def __init__(self, path_to_model):
        # models/collision_resnet/collision_model_resnet_19_04_a_trt.pth
        self._model = TRTModule()
        self._model.load_state_dict(torch.load(path_to_model))

    def execute(self, image, tensor: Tensor, previous_values: list) -> ReturnData:
        collision_chance: float = self.get_collision_chance(tensor)
        if collision_chance > 0.8:
            return ReturnData(command=ReturnCommand.STOP, alpha=0.0, left=0.0, right=0.0)
        else:
            return ReturnData(command=ReturnCommand.CONTINUE, alpha=0.0, left=0.0, right=0.0)

    def get_collision_chance(self, tensor) -> float:
        collision = self._model(tensor)
        collision_softmax = functional.softmax(collision, dim=1).flatten()
        return float(collision_softmax[0])
