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

def get_line_intersecttion_old(a, b, c, d):
	print( "a = ", a )
	print( "b = ", b )
	print( "c = ", c )
	print( "d = ", d )
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
	if abs(det) < 0.0000001 :
		return None
	pass

	# intersect point(x,y)
	x = ((b2*c1) - (b1*c2)) / det
	y = ((a1*c2) - (a2*c1)) / det

	return (x, y)
pass # -- get_line_intersecttion old

def get_line_intersection( pt1, pt2, ptA, ptB ): 
    """ this returns the intersection of Line(pt1,pt2) and Line(ptA,ptB)
        
        returns a tuple: (xi, yi, valid, r, s), where
        (xi, yi) is the intersection
        r is the scalar multiple such that (xi,yi) = pt1 + r*(pt2-pt1)
        s is the scalar multiple such that (xi,yi) = pt1 + s*(ptB-ptA)
            valid == 0 if there are 0 or inf. intersections (invalid)
            valid == 1 if it has a unique intersection ON the segment    """

    DET_TOLERANCE = 0.00000001

    # the first line is pt1 + r*(pt2-pt1)
    # in component form:
    x1, y1 = pt1;   x2, y2 = pt2
    dx1 = x2 - x1;  dy1 = y2 - y1

    # the second line is ptA + s*(ptB-ptA)
    x, y = ptA
	xB, yB = ptB
    dx = xB - x
	dy = yB - y

    # we need to find the (typically unique) values of r and s
    # that will satisfy
    #
    # (x1, y1) + r(dx1, dy1) = (x, y) + s(dx, dy)
    #
    # which is the same as
    #
    #    [ dx1  -dx ][ r ] = [ x-x1 ]
    #    [ dy1  -dy ][ s ] = [ y-y1 ]
    #
    # whose solution is
    #
    #    [ r ] = _1_  [  -dy   dx ] [ x-x1 ]
    #    [ s ] = DET  [ -dy1  dx1 ] [ y-y1 ]
    #
    # where DET = (-dx1 * dy + dy1 * dx)
    #
    # if DET is too small, they're parallel
    #
    DET = (-dx1 * dy + dy1 * dx)

    if math.fabs(DET) < DET_TOLERANCE: 
		return None

    # now, the determinant should be OK
    DETinv = 1.0/DET

    # find the scalar amount along the "self" segment
    r = DETinv * (-dy  * (x-x1) +  dx * (y-y1))

    # find the scalar amount along the input line
    s = DETinv * (-dy1 * (x-x1) + dx1 * (y-y1))

    # return the average of the two descriptions
    xi = (x1 + r*dx1 + x + s*dx)/2.0
    yi = (y1 + r*dy1 + y + s*dy)/2.0

    #return ( xi, yi, 1, r, s )
    return ( xi, yi )
pass

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