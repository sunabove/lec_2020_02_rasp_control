# coding: utf-8

import os, numpy as np

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

def get_line_intersecttion(a1, a2, b1, b2):
    	# 두 직선의 교점 구하기 
	""" 
	Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
	a1: [x, y] a point on the first line
	a2: [x, y] another point on the first line
	b1: [x, y] a point on the second line
	b2: [x, y] another point on the second line
	"""
	s = np.vstack([a1,a2,b1,b2])        # s for stacked
	h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
	l1 = np.cross(h[0], h[1])           # get first line
	l2 = np.cross(h[2], h[3])           # get second line
	x, y, z = np.cross(l1, l2)          # point of intersection
	
	if z == 0:                          # lines are parallel
		return None
	else :
		return (x/z, y/z)
	pass
pass # -- get_line_intersecttion

def get_polygon_intersection(a1, a2, polygon):
	# 한직선과 폴리곤의 교점 구하기 
	points = polygon[:,:]

	max_distum = -1
	max_point = None

	b1 = None

	for b2 in points :
		if b1 is not None :
			cross = get_line_intersecttion( a1, a2, b1, b2 )

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