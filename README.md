# HOIP logging script

## Prerequisites
- Python 3
- Zabbix agent

## About

Script that will log all the usefull information from HOIP devices to a zabbix server. The *zabbix.py* file depends on the *hoip.py* script. These two files need to be in the **same directory** for them to work! To run the script do:

```console
python src/Zabbix.py
```

A mapping file is used called *mapping_devices.json* to inform the script what the device names and ip adresses are. Without this file the script will not work.

When successfully executing the script all the information gathered by the script will be written to a file called *zabbix.out*. This file is used by the **Zabbix Agent** to send all the information to the zabbix server. When the script ends the file will still be there so you can check what has been send.

## Default

There is also a script called *Default.py*. This script is used to set the channel of all the devices back to the default channel. This could be used at the end of the day to reset all the channels of the devices.
