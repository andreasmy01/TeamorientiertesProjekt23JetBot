# Teamorientiertes Projekt 2023: Autonomes Fahren mittels Künstlicher Intelligenz, Technische Hochschule Ulm


## **JetBot Quick Guide**

Ergebnis (Video): https://short.mlandth.de/2BK9eq

Diese Kurzanleitung dient dazu, einen JetBot ohne aufwändige Installation in Betrieb zu nehmen und eine Live-Demo vorzuführen.
### Voraussetzungen:
* jetbot_demo.zip (s. Anlage) oder jetbot_clean.zip (Schritt 7 muss ausgeführt werden!)
* Schnelle microSD-Karte mit mindestens 64 GB Speicherkapazität
* microSD-Kartenleser
* JetBot
* Monitor mit HDMI Anschluss (+Kabel) und kabelgebundene USB-Tastatur
* Rechner / Laptop mit Webbrowser
* Teststrecke
* Straßenschilder

### Vorbereitungen Teststrecke
Der JetBot kann mit den mitgelieferten Models nur auf einer speziellen Teststrecke autonom fahren.
<br><br> **Achtung**: <br>
Die Lichtverhältnisse spielen eine extrem große Rolle bei der Fähigkeit des JetBots, sowohl der Straße zu folgen als auch die Schilder zu erkennen.
Bei Reflektionen kann es passieren, dass der JetBot nicht mehr wie gewünscht reagiert und Schilder missachtet oder der Straße nicht korrekt folgt.
<br><br> **Achtung**: <br>
Damit der JetBot die Schilder zuverlässig erkennen kann, müssen die Schilder auf eine bestimmte Art und Weise auf der Teststrecke platziert werden.
* Straßenschilder werden nur am rechten Fahrbahnrand erkannt
* Straßenschilder sollten direkt an den äußeren Rand der gelben Fahrbahnbegrenzung angrenzend aufgestellt werden.
* Straßenschilder sollten leicht angewinkelt aufgestellt werden, sodass der JetBot durch die Fischaugenperspektive der Kamera die Schilder besser erkennen kann

**Achtung**: <br> 
Die Einstellung des Kamerawinkels wirkt sich direkt auf das Verhalten des JetBots aus.
Dies ist besonders wichtig, da der Winkel nur schlecht über die beiden angebrachten Schrauben fest fixiert werden kann.
Blickt die Kamera zu weit in die Ferne, erkennt der JetBot Schilder sehr gut, fährt aber schlechter.
Blickt die Kamera zu sehr auf den Boden, erkennt der JetBot Schilder schlecht bis kaum, fährt dafür aber besser.
<br>Der ideale Kamerawinkel beträgt ~55°.

### 1. SD-Karte flashen
   Besuchen Sie die Website https://www.balena.io/etcher und laden Sie balenaEtcher herunter.
   Stecken Sie die microSD-Karte des JetBot in einen Computer und öffnen Sie balenaEtcher.
   Klicken Sie nun auf flash from file und wählen Sie die jetbot_demo.zip aus.
   Als nächstes klicken Sie auf select target und wählen die eingesteckte microSD-Karte aus.
   Zuletzt klicken Sie auf flash und warten, bis der Flashvorgang abgeschlossen ist.
   Dies kann je nach Kartenleser zwischen 10 und 60 Minuten dauern.

### 2. JetBot an Monitor anschließen
   Schließen Sie den JetBot mit einem HDMI-Kabel an einen Monitor an.
   Stecken Sie anschließend eine kabelgebundene Tastatur per USB an den JetBot an.

### 3. JetBot vorbereiten
   Der Akku des JetBots sollte zuvor voll aufgeladen sein oder der JetBot ist direkt am Netzteil angeschlossen.
   Anmerkung: Das Netzteil darf nie direkt in das Jetson Nano Board eingesteckt werden, sondern immer in den Anschluss auf dem Akku-Board, da beide Anschlüsse unterschiedliche Spannungsversorgungen erwarten.

### 4. SD-Karte in JetBot einführen und booten
   Stecken Sie die fertige microSD-Karte in den entsprechenden Steckplatz des JetBots.
   Dieser befindet sich auf der oberen Platine direkt unter dem Kühlkörper und dem Lüfter.
   Achten Sie darauf, dass die Kontakte der microSD-Karte nach oben zeigen und die SD-Karte mit einem Klick einrastet.
   Betätigen Sie nun den Ein/Aus-Schalter, der sich auf der untersten Platine auf der Seite der USB-Anschlüsse befindet, und schalten Sie den JetBot ein.
   Sobald auf dem Bildschirm *nano-4gb-jp45 login:* erscheint, geben Sie zweimal jetbot für den Benutzernamen und das Passwort ein.
   ```bash   
   username: jetbot
   password: jetbot
   ```

### 5. Wifi und ssh           	
   Nach erfolgreicher Anmeldung verbinden Sie sich mit dem lokalen Netzwerk. Dazu geben sie folgenden Befehl ein:
   ```bash
   sudo nmcli device wifi connect <SSID> password <PASSWORD>
   ```
Anmerkung: Es wird das QUERTY Layout verwendet. (z.B.: y → z oder ß → -)


Ersetzen Sie <SSID> durch den Namen des Netzwerks und <PASSWORD> durch das für das Netzwerk erforderliche Passwort.
Nachdem Sie den Befehl eingegeben haben, werden Sie erneut nach dem Passwort gefragt.
Geben Sie dazu erneut jetbot ein.
Wenn die Verbindung erfolgreich war, sehen Sie nun auf dem Display des JetBots unter wlan0:
die IP, die dem JetBot zugewiesen wurde.

### 6. Per SSH mit JetBot verbinden
   Sie können jetzt den Bildschirm und die Tastatur vom JetBot trennen und die weitere Konfiguration per SSH auf einem Computer durchführen.
   Öffnen Sie dazu das Terminal und geben Sie folgenden Befehl ein:
   ```bash
   ssh jetbot@<IP>
   ```

Ersetzen Sie <IP> durch die auf dem Display angezeigte IP-Adresse.
Nach Eingabe des Kommandos wird erneut nach dem Passwort gefragt.
Geben Sie dazu wieder jetbot ein.
Sie haben sich nun erfolgreich per ssh mit dem JetBot verbunden.
Anmerkung: Beim initialen Verbinden per SSH werden Sie wahrscheinlich danach gefragt werden, ob die Verbindung vertrauenswürdig ist.
Geben Sie dafür einfach yes ein, sobald Sie danach gefragt werden.

### 7. Partitionierung (Optional)
   Bei den fertigen Images sind standardmäßig nur 42 GB Speicherplatz verfügbar.
   Der Rest der Speicherkapazität ist keiner Partition zugeordnet.
   Um die Partition zu vergrößern, müssen folgende Befehle ausgeführt werden:
   ```bash
   cd ~/jetcard/scripts/
   git pull
   ./jetson_install_nvresizefs_service.sh
   ```
Starten Sie das System mit folgendem Befehl neu:
   ```bash
   sudo reboot
   ```

Ob die Partitionierung erfolgreich war, sehen Sie nach dem Neustart auf dem Display des JetBot. Unter Disk: sollte nun eine Kapazität angezeigt werden, die in etwa der Größe der SD-Karte entspricht.
Alternativ können Sie die Partitionierung auch mit folgendem Befehl überprüfen.
   ```bash
   df -h
   ```

### 8. Dateien kopieren (optional)
   Sollten Sie ein Image (z.B. jetbot_clean.zip) verwendet haben, auf dem die benötigten Projektdateien nicht bereits vorhanden sind, können Sie diese Dateien auf zwei Arten auf dem JetBot hinzufügen.

Option 1:
   ```bash   
   cd ~
   git clone https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot.git
   ```

Option 2: <br>
Kopieren Sie den Ordner TeamorientiertesProjekt23JetBot (Anlage, im Ordner 2_CODE) in das Home-Verzeichnis des JetBots (per sftp oder scp).

### 9. Mit JetBot verbinden
   Öffnen Sie einen Browser und geben Sie die IP des JetBots in die Adresszeile ein.
   Fügen Sie den Port 8888 hinzu und drücken Sie die Eingabetaste.
   Für die IP-Adresse 192.168.1.123 geben Sie z.B. 192.168.1.123:8888 in die Adresszeile ein.
   Geben Sie das Passwort jetbot ein und melden Sie sich an.
   Auf der linken Seite sehen Sie nun alle Ordner, die sich auf dem JetBot befinden.

### 10. Live-Demo Starten
   Öffnen Sie das Jupyter Notebook [LiveDemo_object_oriented.ipynb](https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/blob/main/LiveDemo_object_oriented.ipynb).
   Bevor Sie ein Jupyter Notebook starten, ist es ratsam, den Kernel neu zu starten und alle Ausgaben zu löschen:

   Kernel → Restart & Clear Output

   Sie führen eine Zelle aus, indem Sie mit der Maus die entsprechende Zelle mit der linken Maustaste anklicken und dann entweder auf 
   <br> den Button ▶️ Run klicken oder Shift + Enter auf der Tastatur drücken.
   <br><br> Eine Zelle verfügt über 3 unterschiedliche Zustände, welche sich anhand des Symbols in den eckigen Klammer links der jeweiligen Zelle auslesen lassen:
   * \[ ] Kernel wurde neu gestartet & alle Ausgaben wurden gelöscht → In diesem Stand sollten sich alle Zellen befinden, bevor ein Notebook ausgeführt wird.
   * [*] Zelle wird aktuell ausgeführt und die Ausführung ist noch nicht fertiggestellt
   * [3] Zelle wurde erfolgreich ausgeführt → Die Zahl steht für die Reihenfolge, in welcher die einzelnen Zellen ausgeführt wurden

Ob der Kernel gerade Code ausführt, erkennt man oben rechts:
* ist der kleine Kreis nicht ausgefüllt, ist der Kernel bereit und es wird kein Code ausgeführt
* ist der Kreis ausgefüllt, wird gerade Code ausgeführt und der Kernel ist beschäftigt
Führen Sie nun die ersten 4 Code-Zellen des Notebooks aus.

#### 10.1 JetBot initialisieren:
Wurden die ersten 4 Code-Zellen erfolgreich ausgeführt, sehen Sie nun eine Liveübertragung des Kamera Feeds des JetBots.

#### 10.2 JetBot starten:
**ACHTUNG**: Sobald Sie die 5. Code-Zelle (bot.start()) ausführen, wird der JetBot nach wenigen Sekunden losfahren.
Die Liveübertragung der Kamera auf dem Notebook friert hierbei zunächst ein.
<br> Hierbei ist es wichtig, dass der **JetBot einige Sekunden (ca. 20 Sekunden) benötigt**, bis er die Informationen der Kamera verarbeiten kann.
<br> **Er fährt allerdings trotzdem los, obwohl er noch keine Entscheidungen treffen kann!**

*Empfehlung*: Halten Sie den JetBot so lange fest, bis er wieder richtig fährt. Wann ist dies der Fall?
<br> Wird die Liveübertragung der Kamera verzögerungsfrei wiedergegeben, kann der JetBot korrekt fahren.
<br> Am leichtesten ist dies daran zu erkennen, wenn sie eine Hand vor dem JetBot hin- und herbewegen und im Live Feed keine Verzögerungen mehr zu erkennen sind.

#### 10.3 JetBot pausieren:
Führen Sie die 6. Code-Zelle (bot.pause()) aus und der JetBot bleibt stehen.
<br> Soll der JetBot danach wieder weiterfahren, müssen Sie nur wieder die 5. Code-Zelle ausführen.
Hierbei treten keine Verzögerungen wie beim initialen Start auf.

#### 10.4 JetBot stoppen:
Führen Sie die 6. und 7. Code-Zelle aus.
Wollen Sie den JetBot erneut fahren lassen, müssen Sie den gesamten Schritt 8. erneut ausführen.
*Anmerkung*: Für ein bestmögliches Ergebnis starten Sie vor einem erneuten Ausführen von Schritt 8 den JetBot einmal neu. Dies ist allerdings kein Muss, der JetBot fährt trotzdem wie gewohnt weiter, er kann nur für das Laden der Models mehr Zeit benötigen.

  

www.thu.de
![Logo Technische Hochschule Ulm](https://studium.hs-ulm.de/_catalogs/masterpage/HSUlm/images/logo.svg)
  
