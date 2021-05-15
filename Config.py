# -*- coding: utf-8 -*-

import configparser, os

config = None

def get_config(key=None) :

    configfile_name = "robot.config"

    # Check if there is already a configurtion file
    if not os.path.isfile(configfile_name):
        # Create the configuration file as it doesn't exist yet
        cfgfile = open(configfile_name, "w")

        # Add content to the file
        config = configparser.ConfigParser()
        
        section_name = "robot"

        robot = config[ section_name ] = {}
        robot[ "P" ] = "6"
        robot[ "I" ] = "1"
        robot[ "I" ] = "4"

        config.write(cfgfile)

        cfgfile.close()
    pass
pass

if __name__ == '__main__':
    get_config( "" )
pass