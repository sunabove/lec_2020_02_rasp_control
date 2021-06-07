# coding: utf-8

import os

def check_pkg( pkg ) : 
	try:
		pkg = pkg.split(",")
		import importlib
		mode_name = pkg[0].strip() 
		importlib.import_module( mode_name )
	except ModuleNotFoundError :
		print( '%s is not installed, installing it now ... ' % mode_name )
		
		for lib in pkg[ 1 : ] :
			lib = lib.strip()
			
			if lib.startswith( "lib") :
				os.system( f"sudo apt install -y {lib}" )
			else :
				os.system( f"sudo pip3 install {lib}" )
			pass
		pass
	pass
pass

