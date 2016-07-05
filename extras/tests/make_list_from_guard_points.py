pointfile = open("factory_sneak_guard_guard_points.py", "r")
newfile = open("factory_sneak_guard_guard_points_list.py", "a")
newfile.write("{")
index = 1
for line in pointfile.readlines():
	pos, hpr = line.split('|')
	x, y, z = pos.split(' ')
	h, p, r = hpr.split(' ')
	newfile.write("\n'" + str(index) + "': [Point3(" + str(x) + ", " + str(y) + ", " + str(z) + "),\nVec3(" + str(h) + ", " + str(p) + ", " + str(r) + ")],")
	index += 1
newfile.write("\n}")
newfile.flush()
newfile.close()
pointfile.close()
