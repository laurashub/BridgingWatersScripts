# A Novel Algorithm to Predict Bridging Water Locations During Computational Ligand Docking
  
### Last updated: 5/7/2019

----
### XMLs
* timing\_low\_res\_pw.xml 

   XML script used to generate low-resolution trials and the PlaceWaters trials. If you only want to generate the low-resolution trials _without_ PlaceWaters mover, remove the  
"<Add mover\_name="pack\_rotamers\_mover"/>" and "<Add mover\_name="place\_waters"/>" lines. This XML also contains the timing metrics used to collect information on the duration of each mover, which can be removed.

* timing\_high\_res.xml

   XML script for the high-resolution and final minimization steps, intended to go after the PlaceWaters mover. Requires that the ligand is on chain "X" and the waters are on chain "W".

### Python scripts
* rank\_native\_waters.py
   
   Used to determine which waters in the PDB were "bridging waters", defined as being within 3 of both the ligand and protein. Produces a "pruned" pdb file with only the bridging waters.

* tune\_params.py

   Script used to train the parameters on the training set. Contains the loss function as well as the range of each variable tested.

* random\_waters.py

   Used in place of the PlaceWaters in the random water placement trials. Randomly places between 1 and 5 waters around the ligand.

* fix\_chains.py

   Moves waters to chain "W" and updates the atom numbers and residue numbers accordingly. Also removes unnecessary "TERM" lines. 
