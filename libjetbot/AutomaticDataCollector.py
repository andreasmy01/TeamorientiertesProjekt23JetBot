import os
from uuid import uuid1

from jetbot import bgr8_to_jpeg


class AutomaticDataCollector:

    def __init__(self, camera, wait_time=1):
        self._collection_folder = "dataset"
        self._wait_time = wait_time
        self._camera = camera
        self._fps = self._camera.fps
        self._frame_counter = 0

        try:
            os.makedirs(self._collection_folder)
        except FileExistsError:
            print('Directories not created because they already exist')

    def execute(self, change):
        self._frame_counter += 1
        if (self._frame_counter % (self._fps * self._wait_time)) == 0:
            with open(os.path.join(self._collection_folder, str(uuid1()) + '.jpg'), 'wb') as f:
                f.write(bgr8_to_jpeg(change['new']))
            self._frame_counter = 0

    def start(self):
        self._camera.observe(self.execute, names='value')

    def stop(self):
        self._camera.unobserve(self.execute, names='value')
