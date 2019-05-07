#!/sb/apps/Linux/bin/python

def fix_water_naming(pdb, lig):

    lines = []
    num_wat_hetnam = 0
    num_wat_natatm = 0
    num_wat = 0
    ter_to_remove = []
    with open( "/Users/Rose/PlaceWaters/timing/low_res/"+pdb+"_cleaned_"+lig+"_0001.pdb") as f:
        lines = f.read().splitlines()

    #find TER in between ligand and waters
    for i, line in enumerate(lines):
        if "HETNAM" in line and "HOH" in line:
            ter_to_remove.append(i)
        if "HETNAM" in line and lig in line:
            new_line = line[0:15] + "X" + line[16:]
            lines[i] = new_line
            #print (line)
        if "HETATM" in line and "HOH" in line:
            if line[77] == "O":
                num_wat += 1
            new_line = line[0:17] + "HOH W" + "%4d"%(num_wat) + line[26:]
            lines[i] = new_line
            #print (line)
        if "HETATM" in line and lig in line:
            new_line = line[0:21] + "X" + line[22:]
            lines[i] = new_line
            #print (line)
        if "TER" in line:
            if ('WAT' in lines[i-1] or lig in lines[i-1]) and ('WAT' in lines[i+1]):
                ter_to_remove.append(i);
            
    
    with open ("/Users/Rose/PlaceWaters/timing/waters_fixed/"+pdb+"_"+lig+".pdb", "a") as f:
        for j in range(0, num_wat):
            f.write("HETNAM     HOH W" + "%4d"%(j+1) + "  HOH\n")
        
        for i, line in enumerate(lines):
            if i not in ter_to_remove:
                f.write(line + "\n")
        

from sys import argv
def main():
    with open("../test_set.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            tokens = line.split()
            fix_water_naming(tokens[0], tokens[1])

if __name__ == '__main__':
	main()
