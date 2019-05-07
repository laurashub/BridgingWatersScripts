#!/sb/apps/Linux/bin/python

import os.path
import sys
import pymol

pymol.pymol_argv = ['pymol','-c'] 
pymol.finish_launching()
pymol.cmd.feedback('disable', 'all', 'actions')
pymol.cmd.feedback('disable', 'all', 'results')

from sys import exit
def has_interface_water_contacts(water_resi, dist, tight):

    distance_cutoff=dist # 3.0 for 'loose' and 'tight', 2.5 for 'extra_tight'
    ligand_contacts=pymol.cmd.find_pairs('prot AND resn HOH AND resi '+water_resi, 'ligand AND chain X AND (NOT hydro)', cutoff=distance_cutoff)
    protein_contacts= pymol.cmd.find_pairs('prot AND resn HOH AND resi '+water_resi, 'prot AND (NOT resn HOH) AND (NOT hydro)', cutoff=distance_cutoff)

    if len(ligand_contacts) > 0 and len(protein_contacts) > 0:
        return len(ligand_contacts) + len(protein_contacts) # for 'loose_waters.pdb'
    else:
        return 0

def has_cofactor_contacts():
    cofactor_contacts=pymol.cmd.find_pairs('prot AND hetatm AND (NOT resn HOH)', 'ligand AND chain X', cutoff=5.0)
    return len(cofactor_contacts) > 0


def rank_waters(protein, ligand, cutoff):
    
    pdb = "../input_files/my_cleaned/" + protein + "_cleaned_water_unique_resi.pdb"
    lig = "../input_files/my_cleaned/" + protein + "_" + ligand + ".xchain.pdb"
    print("PDB " + pdb +" + LIG " + lig)
    if not os.path.isfile(pdb) or not os.path.isfile(lig):
        pymol.cmd.quit()
        sys.exit("Unable to find one or more input files.")
            
    pymol.cmd.load(pdb, 'prot')
    pymol.cmd.load(lig, 'ligand')

    #get all the waters in the native structure
    myspace={'water_resis': []}
    pymol.cmd.iterate('prot AND resn HOH', 'water_resis.append(resi)', space=myspace)

    num_waters = 0
    waters = {}


    cofactors = has_cofactor_contacts()

    if not cofactors:
        for water_resi in myspace['water_resis']: 
            water_contacts = has_interface_water_contacts(water_resi, cutoff, False)
            if water_contacts > 0:
                if water_resi not in waters.keys():
                    num_waters += 1
                    waters[water_resi] = water_contacts
                else:
                    print("Duplicate water_resi: {0}".format(water_resi) )
            else:
                pymol.cmd.remove('prot AND resn HOH AND resi '+water_resi)    
    if num_waters > 0 and num_waters < 6:
        pymol.cmd.save("../native/"+protein+"_"+ligand+"_pruned_h2o.pdb", 'prot') 
        with open ("../water_counts.txt", "a") as f:
            f.write("{0}_{1} {2}\n".format(protein, ligand, num_waters))
            for water_resi in waters.keys():
                f.write("{0} {1}\n".format(water_resi, waters[water_resi]))
    pymol.cmd.quit()

from sys import argv
def main():
    args=argv[1:]

    rank_waters(args[0], args[1], 3.0)
   
if __name__ == '__main__':
	main()
