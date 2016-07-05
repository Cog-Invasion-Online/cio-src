filename = raw_input("The file: ")

print "Opening EGG file " + filename + "..."
eggFileR = open(filename, "r")
lines = eggFileR.readlines()
eggFileR.close()

print "Looking for groups with names starting with occluder..."
lastLine = ""
for line in lines:
    if lastLine == line:
        continue
    if "<Group>" in line:
        # This is defining a new group
        if "occluder" in line:
            i = lines.index(line) + 1
            print line
            # This is defining an occluder node, add the scalar occluder
            # stuff, to make it actually an OccluderNode.
            string = "    <Scalar> occluder { 1 }\n"
            lines.insert(i, string)
            lastLine = line

print "Writing to " + filename + "..."
eggFileW = open(filename, "w")
contents = "".join(lines)
eggFileW.write(contents)
eggFileW.flush()
eggFileW.close()

print "Completed!"
