# powerplan
power management for windows (through powercfg shell command) via system tray

#### Requirements:
Python 3

pip install pystray, psutil, winsound

#### Install:

1. Edit __powerplan.cfg__ file. Call:```
powercfg -list 
``` in cmd shell or Windows PowerShell. Fill [Plans] section by power schema names: ```short_name_for_find = long_name_for_display_in_menu```.
Fill [Applications] section by: ```application.exe = power_level_index```. Level index is ordered in [Plans].
2. Open cmd shell or  Windows PowerShell. Go to your python3 directory, find __python.exe__ and __pythonw.exe__
3.  First call: 
```C:\Program Files\Python38> python.exe "_path_to_powerplan_dir_\powerplan.py"```.  
Be sure u have no errors, just information output. Find new icon on system tray, choose exit.

4. Next call: 
```C:\Program Files\Python38> pythonw.exe "_path_to_powerplan_dir_\powerplan.py" -hide```.
Be sure your new icon is autonomic.

5. Open windows scheduler, create new task with trigger: logon, and action: start program from previous step 4.

#### Config example:
powercfg -list:
* GUID схемы питания: 381b4222-f694-41f0-9685-ff5bb260df2e  (Сбалансированная) *
* GUID схемы питания: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c  (Высокая производительность)
* GUID схемы питания: a1841308-3541-4fab-bc81-f71556f20b4a  (Экономия энергии)
* GUID схемы питания: e9a42b02-d5df-448d-aa00-03f14749eb61  (Максимальная производительность)

Translated to [Plans] section:
* Экон = Экономный
* Сбал = Сбалансированный
* Высок = Высок.производительность
* Макс = Максимальный

(Экон = Economy, Сбал = Balanced, Высок = HighPerf, Макс = MaxPerf) in russian

#### Issues:
Config file location is set up in line 20 ```config.read(sys.path[0] + '\powerplan.cfg') #```

Font set up in file 'powerplan_image.py', line 51

Beep time set up in file 'powerplan.py', line 138, by default is 0:30