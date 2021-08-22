import os
import os.path

def get_new_files():
	out = []

	tree = os.walk("root")
	first = True

	for base, dirs, files in tree:

		if first:
			first = False
			continue
		elif not files:
			continue
		elif ".meta" in files:
			continue

		for file in files:
			out.append(base+"/"+file)

	return out


def get_old_files():
	count = 0
	size = 0

	tree = os.walk("root")
	first = True

	for base, dirs, files in tree:

		if first:
			first = False
			continue
		elif not files:
			continue
		elif ".meta" not in files:
			continue

		for file in files:
			size += os.path.getsize(base+"/"+file)
			if file != ".meta":
				count += 1

	size /= 1024**3
	precision = 3
	while round(size, precision) == 0:
		precision += 1

	print(round(size, precision))

	size = round(size, precision)

	return count, size
