pointfile = open("factory_sneak_guard_walk_points.py", "r")
newfile = open("factory_sneak_guard_walk_points_list.py", "a")
newfile.write("{")
index = 1
for line in pointfile.readlines():
	x, y, z = line.split(' ')
	newfile.write("\n'" + str(index) + "': Point3(" + str(x) + ", " + str(y) + ", " + str(z) + "),")
	index += 1
newfile.write("\n}")
newfile.flush()
newfile.close()
pointfile.close()
