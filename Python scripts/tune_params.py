from hyperopt import fmin, tpe, hp
import hyperopt.pyll.stochastic
import os, random, subprocess
import sys
import math
from operator import itemgetter

tsi = 0
associations = []
flags=["-mistakes\n",
    "    -restore_pre_talaris_2013_behavior true\n", 
    "-overwrite\n", 
    "-mute core.io;\n"]

my_space = { 'r': hp.uniform('r', 0.1, 0.5), 
    'c': hp.uniform('c', 1.0, 3.0),
    'gc': hp.uniform('gc', 2.5, 5.0),
	'mc': hp.uniform('mc', 1.0, 5.0),
	'nho': hp.uniform('nho', 3.0, 6.0),
	'nhi': hp.uniform('nhi', 0.0, 3.0)
    }
failed_runs = []
bests = []

def score_waters(pdb, lig):    

    water_resis = {} 
    with open("/Volumes/Verbatim/PlaceWaters/native/"+pdb+"_"+lig+"_pruned_h2o.pdb", "r") as f:
        i = 1
        lines = f.read().splitlines()
        for line in lines:
            if line[17:20] == "HOH" and line[77:78] == "O": #only count the oxygen
            	water_resis[i] = (float(line[31:38]), float(line[38:46]), float(line[46:54]))
            	i+=1
    my_wat = {}
    with open("/Volumes/Verbatim/PlaceWaters/runs/native/"+pdb+"_"+lig+"_native_nw_0001.pdb", "r") as f:
        i = 1
        lines = f.read().splitlines()
        for line in lines:
            if line[17:20] == "HOH" and line[77:78] == "O": #only count the oxygen
                my_wat[i] = (float(line[31:38]), float(line[38:46]), float(line[46:54]))
                i+=1

    print(water_resis)
    print(my_wat)
    #calculate distances
    all_dists = {}
    for wat in my_wat.keys():
        all_dists[wat] = []
        for nwat in water_resis.keys():
            cur_dist = get_vector_distance( water_resis[nwat][0], water_resis[nwat][1], water_resis[nwat][2], my_wat[wat][0], my_wat[wat][1], my_wat[wat][2] )
            all_dists[wat].append((nwat, cur_dist))
            all_dists[wat].sort(key=lambda tup: tup[1]) 

    pairings = []
    free_wat = list(my_wat.keys())
    while len(free_wat) > max(len(my_wat.keys())-len(water_resis.keys()), 0):
        wat_to_check = list(free_wat)
        for wat in wat_to_check:
            for nwat, dist in all_dists[wat]:
                try: #check if current val is in list
                    i=[x[1] for x in pairings].index(nwat)
                    (current, nwat2, curdist) = pairings[i]
                    if float(dist) < float(curdist): #this is closer than the current pair, replace
                        pairings.append((wat, nwat, dist))
                        del pairings[i] #remove pairing
                        free_wat.append(current)
                        free_wat.remove(wat)
                        break
                except ValueError: #not in current pairings, just add
                    pairings.append((wat, nwat, dist))
                    free_wat.remove(wat)
                    break
               
    final_distances = {}
    for awat, nwat, dist in pairings:
        final_distances[awat] = (nwat, dist)
    print(final_distances)

    rmsd_total = 0
    recap = 0
    total = 0

    for key in final_distances.keys():
        dist = final_distances[key][1]
        if dist != 0:
            total += 1
            rmsd_total += float(dist)

    normalized_rmsd = 0
    if final_distances.keys():
        normalized_rmsd = float(rmsd_total)/total
    if len(my_wat) == 0:
        return 50 #force adding some waters
    if len(water_resis) > len(my_wat):
        normalized_rmsd += 5*abs(len(water_resis)-len(my_wat)) 
    else:
        normalized_rmsd += 5*abs(len(water_resis)-len(my_wat)) 
  
    print("Final score: " + str(normalized_rmsd))
    return normalized_rmsd

def get_vector_distance(nx, ny, nz, ax, ay, az):
    x_dist = nx - ax
    y_dist = ny - ay
    z_dist = nz - az

    return math.sqrt((x_dist * x_dist) + (y_dist * y_dist) + (z_dist * z_dist))

def generate_flag_file(r, c, gc, mc, nhi, nho):
    print("generating flags: res={0} cutoff={1} group={2} merge={3} nho={4} nhi={5}".format(r, c, gc, mc, nho, nhi))
    with open("/Users/Rose/PlaceWaters/testing_flags.txt", "w+") as f:
	   f.writelines(flags)
	   f.write("-parser:script_vars res={0} cutoff={1} group={2} merge={3} nho={4} nhi={5}".format(r, c, gc, mc, nho, nhi))


def run_trial(args):
    global tsi

    r, c, gc, mc, nhi, nho = args['r'], args['c'],args['gc'], \
        args['mc'],args['nhi'],args['nho']

    if tsi==0:
        random.shuffle(associations)

    pdb, lig = associations[tsi]

    tsi+=1
    tsi%=len(associations)
    """
    trial = random.randint(1,200)
    fixed_t = '{:04}'.format(trial)

    trial = fixed_t
    """
    flags = generate_flag_file(r, c, gc, mc, nhi, nho)
    try:
    	subprocess.check_call("./place_waters.sh %s %s" % (str(pdb), str(lig)),   shell=True)
    except:
    	print("SUBPROCESS FAILED! {0} {1} - exiting".format(pdb, lig))
        failed_runs.append((pdb, lig))
        return 250
    return score_waters(pdb, lig)

#print best

for directory in os.listdir("/Volumes/Verbatim/PlaceWaters/low_res/"):
		associations.append((directory.split("_")[0], directory.split("_")[1]))

for num_run in range(5):
    best = fmin(run_trial, my_space, 
	   algo=tpe.suggest,
        max_evals=5*len(associations))

    with open("best_runs.txt", 'a') as f:
        f.write(str(num_run) + "\n")
        f.write(str(best))
        f.write("\n\n")

print(failed_runs)

