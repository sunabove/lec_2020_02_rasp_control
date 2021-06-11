# coding: utf-8

import os, numpy as np, math

import shapely
from shapely.geometry import LineString, Point

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

	debug = 0 
	
	line1 = LineString( [a1, a2] )
	line2 = LineString( [b1, b2] )

	cross = line1.intersection(line2)
	poi = None

	tp = type( cross )

	debug and print( "type = ", tp )

	if cross is None :
		pass
	elif cross.is_empty :
		pass
		debug and print( "geom empty = ", cross )
	elif tp == Point :
		poi = cross.x, cross.y
	pass

	return poi
pass # -- get_line_intersection

def get_polygon_intersection(a1, a2, polygon):
	# 한직선과 폴리곤의 교점 구하기 
	points = polygon[:,:]

	max_distum = -1
	max_point = None

	b1 = None

	for b in points :
		b2 = b

		if len( b2 ) == 1 :
			b2 = b2[0]
		pass

		if b1 is not None :
			cross = get_line_intersection( a1, a2, b1, b2 )

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