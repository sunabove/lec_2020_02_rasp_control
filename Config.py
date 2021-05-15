# -*- coding: utf-8 -*-

import configparser, os, io

config = None

def get_config(key=None) :

    configfile_name = "robot.config"

    # Check if there is already a configurtion file
    if not os.path.isfile( configfile_name ):
        # Create the configuration file as it doesn't exist yet
        cfgfile = open( configfile_name, "w" )

        # Add content to the file
        config = configparser.ConfigParser()
        
        section_name = "robot"

        robot = {}
        robot[ "P" ] = "6"
        robot[ "I" ] = "1"
        robot[ "D" ] = "4"

        config[ section_name ] = robot

        config.write(cfgfile)

        cfgfile.close()
    pass

    # Load the configuration file
    with open( configfile_name ) as f:
        sample_config = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.readfp(io.BytesIO(sample_config))

        # List all contents
        print("List all contents")
        for section in config.sections():
            print("Section: %s" % section)
            for options in config.options(section):
                print(
                    "x %s:::%s:::%s"
                    % (options, config.get(section, options), str(type(options)))
                )

        # Print some contents
        print("\nPrint some contents")
        print(config.get("other", "use_anonymous"))  # Just get the value
        print(config.getboolean("other", "use_anonymous"))  # You know the datatype?
    pass
pass

if __name__ == '__main__':
    get_config( "" )
pass