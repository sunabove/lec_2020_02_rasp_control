# coding: utf-8

import os, numpy as np, math

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

def get_line_intersection(a1, a2, b1, b2):
	# 두 직선의 교점 구하기 
	
	print( "a1 = ", a1 )
	print( "a2 = ", a2 )
	print( "b1 = ", b1 )
	print( "b2 = ", b2 )
	
	""" returns a (x, y) tuple or None if there is no intersection """
	
	d = (b2[1] - b1[1])*(a2[0] - a1[0]) - (b2[0] - b1[0])*(a2[1] - a1[1])
	
	if d:
		uA = ((b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0])) / d
		uB = ((a2[0] - a1[0]) * (a1[1] - b1[1]) - (a2[1] - a1[1]) * (a1[0] - b1[0])) / d
	else:
		return None
	
	if not(0 <= uA <= 1 and 0 <= uB <= 1):
		return None
	
	x = a1[0] + uA*(a2[0] - a1[0])
	y = a1[1] + uA*(a2[1] - a1[1])

	return [ x, y ]
pass # -- get_line_intersection

def get_polygon_intersection(a1, a2, polygon):
	# 한직선과 폴리곤의 교점 구하기 
	points = polygon[:,:]

	max_distum = -1
	max_point = None

	b1 = None

	for b2 in points :
		b2 = b2[0]

		if b1 is not None :
			cross = get_line_intersection( a1, a2, b1, b2 )

			print( "cross = ", cross )

			if cross is not None :
				dx = a1[0] - cross[0]
				dy = a1[1] - cross[1]

				distum = dx*dx + dy*dy

				if distum >= max_distum :
					max_distum = distum
					max_point = cross
				pass
			pass
		pass

		b1 = b2
	pass

	return max_point
pass # get_polygon_intersection