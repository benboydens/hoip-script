# HOIP logging script

## Prerequisites
- Python 3
- Zabbix agent (added to PATH)

## About

Script that will log all the usefull information from HOIP devices to a zabbix server. Main script file is *Zabbix.py* and depends on *hoip.py* and *command.py*. All these file need to be in the **same directory** for them to work!

A mapping file is used called *mapping_devices.json* to inform the script what the device names and ip adresses are. Without this file the script will not work.

When successfully executing the script all the information gathered by the script will be written to a file called *zabbix_out.txt*. This file is used by the **Zabbix Agent** to send all the information to the zabbix server. When the script ends the file will still be there so you can check what has been send.
