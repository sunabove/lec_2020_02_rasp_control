# -*- coding: utf-8 -*-

import configparser, os, io

config = None
robot_section = {}
section_name = "robot"
configfile_name = "robot.config"

def cfg(key, v=None) :

    # Check if there is already a configurtion file
    if not os.path.isfile( configfile_name ):
        # Create the configuration file as it doesn't exist yet
        cfgfile = open( configfile_name, "w" )

        # Add content to the file
        config = configparser.ConfigParser()
        
        robot_section = {}
        robot_section[ "name" ] = "alphabot"

        config[ section_name ] = robot_section

        config.write(cfgfile)

        cfgfile.close()
    pass

    # Load the configuration file
    with open( configfile_name ) as f:
        sample_config = f.read()
        config = configparser.ConfigParser()
        config.read( configfile_name )

        robot_section = config[ section_name ]

        for key in robot_section :
            v = robot_section[ key ]
            t = f"{key} : {v}"
            print( t )
        pass
    pass
pass

if __name__ == '__main__':
    cfg( "", "" )
pass