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

def get_line_intersecttion(a, b, c, d):
    # 두 직선의 교점 구하기 
	# a1x + b1y = c1
    a1 = b[1] - a[1]
    b1 = a[0] - b[0]
    c1 = a1*a[0] + b1*a[1]

    # a2x + b2y = c2
    a2 = d[1] - c[1]
    b2 = c[0] - d[0]
    c2 = a2*c[0] + b2*c[1]

    # determinant
    det = a1*b2 - a2*b1

    # parallel line
    if det == 0:
        return None
	pass

    # intersect point(x,y)
    x = ((b2*c1) - (b1*c2)) / det
    y = ((a1*c2) - (a2*c1)) / det

    return (x, y)
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