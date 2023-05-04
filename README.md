# Teamorientiertes Projekt 2023: Autonomes Fahren mittels Künstlicher Intelligenz, Technische Hochschule Ulm


## **JetBot Quick Guide**

Ergebnis (Video): https://youtu.be/cvG-0tl-bGQ 

Diese Kurzanleitung dient dazu, einen JetBot ohne kompliziertere Installationen in Betrieb zu nehmen. 
Wenn Sie bereits eine fertige SD-Karte haben, überspringen Sie die Schritte 1-5. Wenn Sie einen 
Datenträger mit allen anderen benötigten Daten haben, können Sie die Aufforderung zum 
Herunterladen von Programmen und Dateien ebenfalls überspringen und die Daten auf dem 
vorhandenen Datenträger verwenden.

1. JetBot Image downloaden
  Besuchen Sie die Website https://jetbot.org/master/software_setup/sd_card.html und laden Sie die 
  .zip-Datei mit einer Größe von 12,7 GB für Modelle mit 4 GB RAM herunter.
  
2. SD-Karte flashen 
  Besuchen Sie die Website https://www.balena.io/etcher und laden Sie balenaEtcher herunter. Stecken 
  Sie die SD-Karte des JetBot in einen Computer und öffnen Sie balenaEtcher. Klicken Sie nun auf „Flash 
  from file“ und wählen Sie die zuvor heruntergeladene .zip-Datei aus. Als nächstes klicken sie auf 
  „select target“ und wählen die eingesteckte SD-Karte aus. Zuletzt klicken sie auf „flash“ und warten bis 
  der Flashvorgang abgeschlossen ist. Dies kann zwischen 30 und 60 Minuten in Anspruch nehmen.
  
3. SD-Karte in JetBot einführen und booten 
  Stecken Sie die fertige SD-Karte in den entsprechenden Steckplatz des JetBot. Dieser befindet sich auf 
  der oberen Platine direkt unter dem Kühlkörper und dem Lüfter. Achten Sie darauf, dass die Kontakte 
  der SD-Karte nach oben zeigen und die SD-Karte mit einem Klicken einrastet. Schließen Sie nun den 
  JetBot an das mitgelieferte Netzteil an. Der Anschluss befindet sich auf der untersten Platine neben 
  dem Display auf der Rückseite des JetBot.
  Als nächstes verbinden sie den JetBot mit einem Bildschirm per HDMI-Kabel und stecken eine Tastatur 
  in einen der Verfügbaren USB-Slots. Betätigen sie nun den An-/Ausschalter, der sich auf der untersten 
  Platine auf Seite der USB-Anschlüsse befindet und schalten sie den JetBot ein. Sobald auf dem 
  Bildschirm „nano-4gb-jp45 login:“ erscheint, geben sie zwei Mal „jetbot“ für den Benutzernamen und 
  das Passwort ein.
  
    username: jetbot
    password: jetbot
 
4. Wifi und ssh 
   Nachdem sie sich erfolgreich angemeldet haben, verbinden sie sich mit dem lokalen Netzwerk. Dazu 
   geben sie folgenden Befehl ein
  
   `sudo nmcli device wifi connect <SSID> password <PASSWORD>`
  
   Ersetzen Sie <SSID> durch den Namen des Netzwerks und <PASSWORD> durch das für das Netzwerk 
   erforderliche Passwort. Nach Eingabe des Befehls werden Sie erneut nach dem Passwort gefragt. 
   Geben Sie dazu erneut „jetbot“ ein. Wenn die Verbindung erfolgreich war, sehen sie nun auf dem 
   Display des JetBots unter „wlan0:“ die IP, die dem JetBot zugewiesen wurde.
   Sie können den Bildschirm und die Tastatur vom JetBot trennen und die weitere Konfiguration auf 
   einem Computer durchführen. Öffnen Sie dazu das Terminal und geben Sie folgenden Befehl ein
  
   `$ ssh jetbot@<IP>`
    
   Ersetzen Sie <IP> durch die auf dem Display angezeigte IP-Adresse. Nach Eingabe des Kommandos 
   wird erneut nach dem Passwort gefragt. Geben Sie dazu wieder „jetbot“ ein. Sie haben sich nun 
   erfolgreich per ssh mit dem JetBot verbunden.
  
5. Partitionierung
   Obwohl die SD-Karte eine Kapazität von 64 GB (oder 128 GB) hat, werden standardmäßig nur 24 GB 
   verwendet. Der Rest ist keiner Partition zugeordnet. Um die Partition zu vergrößern, müssen folgende 
   Befehle ausgeführt werden
   ```
    cd ~/jetcard/scripts/
    git pull
    ./jetson_install_nvresizefs_service.sh
    ``` 
   Starten Sie das System mit folgendem Befehl neu:
  
    `sudo reboot`
    
   Ob die Partitionierung funktioniert hat, sehen Sie nach dem Neustart auf dem Display des JetBots. 
   Unter „Disk:“ sollte nun die Kapazität angezeigt werden, die in etwa der Größe der SD-Karte 
   entspricht. Alternativ können sie die Partitionierung mit folgendem Befehl überprüfen
  
    `sudo fdisk -l` 
 
6. Dateien kopieren 
  Kopieren Sie den Ordner <Name des fertigen Projekts> von einem der verfügbaren Datenträger auf 
  die SD-Karte oder klonen Sie das GitHub-Repository mit folgendem Befehl
  
    `git clone
    https://github.com/andreasmy01/TeamorientiertesProjekt23JetBot/tree/main`
    
7. Jetbot starten 
  Öffnen Sie einen Browser und geben Sie die IP des JetBots in die Adresszeile ein. Fügen Sie :8888 hinzu 
  und drücken Sie Enter. Für die IP-Adresse 192.168.1.145 würden sie z.B. „192.168.1.145:888“ in die 
  Adresszeile eingeben.
  Geben Sie das Passwort „jetbot“ ein und melden Sie sich an. Auf der linken Seite sehen Sie nun alle 
  Ordner, die sich auf dem JetBot befinden. Öffnen Sie die Datei <NameNotebook>, die sich unter 
  "<NameProjektOrdner>/NameNotebook" befindet. Stellen Sie den JetBot auf die Fahrbahn und folgen 
  Sie den Anweisungen in der geöffneten Datei
  

  www.thu.de
  ![Logo Technische Hochschule Ulm](https://studium.hs-ulm.de/_catalogs/masterpage/HSUlm/images/logo.svg)
  
