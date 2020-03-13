# Resource Allocation

This repository hosts all data for the Machine Learning in Business Process Management Seminar Project by 
Rachel Brabender and Oliver Clasen. In the folder "code" you find all implementations we made (allocators, simulators, 
preprocessing, ...) and the plots we created for our analysis. "Data" contains the original and our preprocessed log. 
Additionally we added slides of our presentations on this project in "documentation".

## Setup Python
We are using some libraries which are not part of the normal python libraries. Therefore, we wrote a setupFile which will install those.
```
cd code
bash installLibraries.sh
```
## Run Allocator
The code below executes the simulation with the Q-Value Allocator.
```
cd code
python3 main.py -q
```
For more information on how to execute the code please use the `--help` command.