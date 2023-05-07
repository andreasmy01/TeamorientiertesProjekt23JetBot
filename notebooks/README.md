
Dieses Verzeichnis enthält sämtliche Jupyter Notebooks und Python Skripte, die nicht direkt für die Ausführung der Live-Demo notwendig sind.

### collision_and_road
[collision_and_road_trt.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/collision_and_road/collision_and_road_trt.ipynb)
<br>Notebook für Autonomes Fahren mit Road Following und Collision Detection, aber ohne Sign Handling.

### tools
[AutomaticDataCollector.py](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/tools/AutomaticDataCollector.py)
<br> Skript, welches alle n Frames Bilder aufnimmt und abspeichert.

[JetBotTinder.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/tools/JetBotTinder.ipynb)
<br> Notebook, welches für die Klassifizierung von "free" und "blocked" mit vorher aufgenommenen Bildern verwendet werden kann.

[POI-Clicker.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/tools/POI-Clicker.ipynb)
<br> Notebook, mit dem der Point of Interest für das Road Following auf vorher aufgenommenen Bildern manuell gesetzt werden kann.

### training
#### collision_avoidance
[collision_avoidance_build_resnet18_trt.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/training/collision_avoidance/collision_avoidance_build_resnet18_trt.ipynb)
<br> Notebook, welches ein Collision Avoidance Resnet18 Model auf PyTorch Basis in ein TensorRT Model umwandelt.

[collision_avoidance_data_collection.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/training/collision_avoidance/collision_avoidance_data_collection.ipynb)
<br> Notebook, welches Live-Bilder in "free" und "blocked" kategorisiert. 

[collision_avoidance_train_resnet18.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/training/collision_avoidance/collision_avoidance_train_resnet18.ipynb)
<br> Notebook, welches ein Collision Avoidance Resnet18 Model auf PyTorch Basis trainiert.

#### road_following  
[road_following_build_resnet18_trt.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/training/road_following/road_following_build_resnet18_trt.ipynb)
<br> Notebook, welches ein Road Following Resnet18 Model auf PyTorch Basis in ein TensorRT Model umwandelt.

[road_following_train_resnet18.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/training/road_following/road_following_train_resnet18.ipynb)
<br> Notebook, welches ein Road Following Resnet18 Model auf PyTorch Basis trainiert.

### other
Diese Notebooks werden nicht zwingend benötigt, sondern bieten optionale Zusatzfunktionen an.

[calculate_batch_size.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/other/calculate_batch_size.ipynb)
<br>
Notebook für das Berechnen der idealen Batch Size, z.B. für das Training des Road Following Models.

[drive_logic.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/other/drive_logic.ipynb)
<br> Rudimentäres Notebook, welches die Handles für Road Following und Collision Detection zusammenfasst.

[lane_detection_classification.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/93bcfc1d97f3a86780e6e2f0ba248f16b1a10c3d/notebooks/other/lane_detection_classification.ipynb)
<br> Notebook, welches für die Klassifizierung von Straßentypen mit vorher aufgenommen Bildern verwendet werden kann. ("straight", "curve", etc)
