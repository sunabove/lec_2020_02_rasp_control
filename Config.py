# -*- coding: utf-8 -*-

import configparser, os, io

config = None
robot_section = None
section_name = "robot"
configfile_name = "robot.config"

def cfg(key, v=None, debug=0) :

    global robot_section
    global config

    if robot_section is None :
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
        else :
            # Load the configuration file
            with open( configfile_name ) as f:
                config = configparser.ConfigParser()
                config.read( configfile_name )

                robot_section = config[ section_name ]

                if 0 :
                    for key in robot_section :
                        v = robot_section[ key ]
                        t = f"{key} : {v}"
                        print( t )
                    pass
                pass
            pass
        pass
    pass

    if robot_section is not None :
        if key in robot_section :
            v = robot_section[ key ]
        elif v is not None :
            debug and print( f"save ...{key} = {v}" )

            robot_section[key] = v

            cfgfile = open( configfile_name, "w" )
            config[ section_name ] = robot_section
            config.write(cfgfile)
            cfgfile.close()
        pass
    pass

    return v
pass

if __name__ == '__main__':
    v = cfg( "pid", [6,1,4], debug=1 )
    print( v )
pass