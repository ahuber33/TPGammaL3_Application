# TPGammaL3 pour simulations du TP de L3 sur le rayonnement gamma.
[huber@lp2ib.in2p3.fr, huberarnaud@gmail.com]

## INSTRUCTIONS TO USE THE SIMULATION
- Download the VMWare [Geant4.11.2.1](https://heberge.lp2ib.in2p3.fr/G4VM/index.html)

```
git clone https://github.com/ahuber33/TPGammaL3
```

- Go to build Folder and use this command :
```
cmake -DGeant4_DIR=$G4COMP ../
make -j4
```  
then compile it with make

- The executable TPGammaL3Sim will be add to your bin folder

- If you want to have a visualization, launch this command : 
```
./TPGammaL3Sim [name of ROOT file ]"
```  
It will generate 1 particle according to the vis.mac with QT and you will have a ROOT file with the name you gave in response located in the Resultats folder.

- If you want to have statistics without the visualization, use this command :
```
./TPGammaL3Sim [name of ROOT file] [number of events generated] [name of macro] [MultiThreading ON/OFF] [number of threads]
```  
According to the number of threads used if MT is ON, the simulation will create a ROOT file for each thread and at the end of the simulation, all ROOT files will be merged together with a name correspoding to the name given in [name of ROOT file]. The temporaries ROOT files will be removed after the merge.

Note that it's not necessary to indicate a [number of threads] if the condition on MT is OFF. In opposite, you need to put a value if MT is ON.

Personnaly, I used the vrml.mac but you can create another one. Just to remember that you need to write the name of your macro when you launch the simulation.


- An TPGammaL3Sim.cfg file is located in bin directory. All the dimensions necessary are in this file to avoid recompilation when you want to change some parameters. If you add some other dimensions, don't forget to add the variables in Geometry.cc.
```
#----------Common variables----------
Radius_NaI 25.4 mm
Thickness_NaI 50.8 mm
Thickness_Housing 0.508 mm
```

- Some materials are already defined in the simulation. If you need a new one, you must declare it in the TPGammaL3SimGeometry.cc and precisely on the con construction part of interest. If the material is already in the NIST Database, you can copy the declaration and modifiy the declaration to create a new material. If not, it is advice to declare it in the TPGammaL3SimMaterials.cc in order to clarify the code. After that, DO NOT FORGET to add the declaration of your new material in the ConstructMaterialsList() function in TPGammaL3SimGeometry.cc file. It is NECESSARY if you want to have the conversion of your material name given in the configuration file and the link with the G4Material associated.

- Based on G4EmStandardPhysics_option3.

- DO NOT HESITATE TO REPORT BUGS OR ANY IDEAS THAT WILL IMPROVE THE SIMULATION !!!!
