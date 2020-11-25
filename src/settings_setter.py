""""
settings_setter.py creates a config file (.ini) that is used in o.a. image_proc
"""

from configparser import ConfigParser

# Get the configparser object
config_object = ConfigParser()

# Each brachytherapy parser has its own section: FESTO, NEEDLE, IMAGEPOS
config_object["FESTO"] = {
    "startpos" : "3"
}

config_object["NEEDLE"] = {
    "startsteps": "200"
}

config_object["IMAGEPOS"] = {
    "lower_threshold": "150",
    "upper_threshold": "220",
    "min_votes": "200",
    "maxLG": "20",
    "minLL": "25",
    "theta_resolution": "180"
}

#Write the above sections to config.ini file
with open('config.ini', 'w') as conf:
    config_object.write(conf)

config_object = ConfigParser()
config_object.read("config.ini")
print(config_object.read("config.ini"))
imagepos = config_object["FESTO"]
print(imagepos["startpos"])