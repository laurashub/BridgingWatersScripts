from sys import argv
import os
import numpy as np
import math
import random
import fileinput

def calculate_grid(f, x, y, z):
	x_min, x_max = _rc(x-5), _rc(x+5)
	y_min, y_max = _rc(y-5), _rc(y+5)
	z_min, z_max = _rc(z-5), _rc(z+5)
	gridpoints = []
	for i in np.arange(x_min, x_max, 0.15):
		for j in np.arange(y_min, y_max, 0.15):
			for k in np.arange(z_min, z_max, 0.15):
				gridpoints.append((_rc(i), _rc(j), _rc(k)))

	occupied = []
	with open(f) as file:
		lines = file.read().splitlines()
		for line in lines:
			if ('HETATM' in line or 'ATOM' in line) and len(line.split()) > 6:
				x_check=float(line[31:39])
				y_check=float(line[39:47])
				z_check=float(line[47:55])
				if x_min <= x_check <= x_max and \
					y_min <= y_check <= y_max and \
					z_min <= z_check <= z_max:
						occupied.append((_rc(x_check), _rc(y_check), _rc(z_check)))
	print(len(gridpoints))
	return [coordinate for coordinate in gridpoints if not check_present(coordinate, occupied)]

def check_present(coordinate, occupied):
	for x, y, z in occupied:
		if math.sqrt(math.pow(coordinate[0]-x,2)+math.pow(coordinate[1]-y,2)+math.pow(coordinate[2]-z,2)) < 0.30:
			return True
		return False

def _rc(i):
	return round((i/0.15)*0.15, 2)

def calculate_ligand_center(f):
	ligand_molecules = []
	natom=0
	nres=0
	x_sum = 0
	y_sum = 0
	z_sum = 0
	total = 0
	last=0
	with open(f) as file:
		lines = file.read().splitlines()
		for i, line in enumerate(lines):
			if len(line)>21 and line[21]=='X': #ligand
				natom=int(line[6:11])
				nres=int(line[23:26])
				x_sum+=float(line[31:39])
				y_sum+=float(line[39:47])
				z_sum+=float(line[47:55])
				last=i
				total+=1
	return(x_sum/total, y_sum/total, z_sum/total, natom, nres, i, last)



def guess_waters(f):
	x, y, z, natom, nres, i, last  = calculate_ligand_center(f)
	print(x)
	print(y)
	print(z)
	print(nres)
	natom+=1
	empty_spaces = calculate_grid(f, x, y, z)
	waters = random.sample(empty_spaces, random.randint(1,5))
	HETATM=""
	new_lines = ""
	new_lines += "TER\n"
	for nwat, water in enumerate(waters):
		start = natom + 3*nwat
		new_lines+=(("HETATM {0}  O   HOH W   {1}      {2:.3f}  {3:.3f}  {4:.3f}  1.00  0.00           O\n"
			).format(start, nres+nwat, water[0],water[1], water[2] ))
		new_lines+=(("HETATM {0}  H1  HOH W   {1}      {2:.3f}  {3:.3f}  {4:.3f}  1.00  0.00           H\n"
			).format(start+1, nres+nwat, water[0]+0.96,water[1], water[2] ))
		new_lines+=(("HETATM {0}  H2  HOH W   {1}      {2:.3f}  {3:.3f}  {4:.3f}  1.00  0.00           H\n"
			).format(start+2, nres+nwat, water[0]-0.24,water[1]+0.93, water[2] ))
		HETATM+=("HETNAM     HOH W   {0}  HOH\n".format(nres+nwat))
	print (new_lines)
	for i, line in enumerate(fileinput.FileInput(f,inplace=1)):
		if i==0:
			line=line.replace(line,line+HETATM)
		if i==last:
			line=line.replace(line,line+new_lines)
		print line,
	


def main():
	guess_waters(argv[1])

if __name__ == '__main__':
	main()