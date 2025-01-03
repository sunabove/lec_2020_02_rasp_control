# -*- coding: utf-8 -*-

import configparser, os, io

config = None
robot_section = None
section_name = "robot"
configfile_name = "/home/pi/robot/robot.config"

def cfg(key, v=None, save=0, debug=0) :
    global robot_section
    global config
    global section_name
    global configfile_name

    key = key.lower()

    if robot_section is None :
        # Check if there is already a configurtion file
        if not os.path.isfile( configfile_name ):
            config = configparser.ConfigParser()
            
            robot_section = {}
            robot_section[ "name" ] = "alphabot"

            config[ section_name ] = robot_section

            cfgfile = open( configfile_name, "w" )
            config.write(cfgfile)
            cfgfile.close()
        else :
            # Load the configuration file
            with open( configfile_name ) as f:
                config = configparser.ConfigParser()
                config.read( configfile_name )

                robot_section = config[ section_name ]
            pass
        pass
    pass

    if robot_section is not None :
        if save :
            debug and print( f"save : {key} = {v}" )

            robot_section[key] = f"{v}"

            config = configparser.ConfigParser()
            config[ section_name ] = robot_section
            
            cfgfile = open( configfile_name, "w" )
            config.write(cfgfile)
            cfgfile.close()
        elif key in robot_section :
            v = robot_section[ key ]

            debug and print( f"{key} = {v}, type={type(v)}" )

            if v.startswith( "[") and v.endswith( "]" ):
                import ast 
                v = ast.literal_eval( v )
            else :
                try : 
                    vf = float( v )
                    vi = int( vf )
                    v = [ vf, vi ][vi == vf]
                except :
                    pass
                pass
            pass
        pass
    pass

    return v
pass

if __name__ == '__main__':
    debug = 1
    v = cfg( 'pid', [6,1,4], debug=debug )

    print( v )

    v = cfg( 'pid', [6,1,5], save=1, debug=debug )
    print( v )

    v = cfg( 'signal_range', [240, 540], save=1, debug=debug )
    print( v )

    v = cfg( 'sum_norm_min', 0.09, save=1, debug=debug )
    print( v )

    v = cfg( 'sum_norm_min', 0.09, debug=debug )
    print( v )    
pass