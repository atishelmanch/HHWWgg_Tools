"""
10 November 2021
Abraham Tishelman-Charny 

The purpose of this module is to parallelize the combination of 4 NLO nodes for HIG-21-014 reweighting, running over 4 NLO nodes (cHHH0, cHHH1, cHHH2p45, cHHH5) and 3 years (2016, 2017, 2018) at once. 

Example usage:

# Combine NLO samples 
python Reweight_NLO_Condor.py --nodes cHHH1 --years 2016
python Reweight_NLO_Condor.py --nodes cHHH0,cHHH1,cHHH2p45,cHHH5 --years 2016,2017,2018
python Reweight_NLO_Condor.py --nodes cHHH0,cHHH2p45,cHHH5 --years 2017

# Reweight combined NLO sample to another node 
python Reweight_NLO_Condor.py --reweightNodes cttHH3,cttHH0p35,3D3 
python Reweight_NLO_Condor.py --reweightNodes cttHH3,cttHH0p35,3D3,8a,1b,2b,3b,4b,5b,6b,7b

# Categorize 
python Reweight_NLO_Condor.py --reweightNodes cttHH3,cttHH0p35,3D3 --categorize

"""

#!/usr/bin/python
from SystematicTreeNames import GetSystLabels
import sys, getopt
import itertools
import argparse
import operator
import os

if __name__ == '__main__':

  parser =  argparse.ArgumentParser()
  parser.add_argument('--nodes',default = "", required=False, type=str, help = "Comma separated list of nodes to run")
  parser.add_argument('--reweightNodes',default = "cttHH3", required=False, type=str, help = "Comma separated list of nodes to reweight to")
  parser.add_argument('--years',default = "2017", required=False, type=str, help = "Comma separated list of years to run")
  parser.add_argument('--NominalOnly',action="store_true",help = "Only run on nominal tree")
  parser.add_argument('--categorize', action="store_true", required=False, help = "Split trees into categories based on DNN score")
  args = parser.parse_args()

  nodes = args.nodes.split(',')
  reweightNodes = args.reweightNodes.split(',')
  years = args.years.split(',')
  categorize = args.categorize

  print("categorize:",categorize)

  scriptName = "condor_job.txt"

  print("nodes:",nodes)
  print("reweightNodes:",reweightNodes)
  print("years:",years)

  local = os.getcwd()
  if not os.path.isdir('error'): os.mkdir('error') 
  if not os.path.isdir('output'): os.mkdir('output') 
  if not os.path.isdir('log'): os.mkdir('log') 
   
  # Prepare condor jobs
  condor = '''executable              = run_script.sh
output                  = output/$(ClusterId).$(ProcId).out
error                   = error/$(ClusterId).$(ProcId).err
log                     = log/$(ClusterId).log
transfer_input_files    = run_script.sh
    
+JobFlavour             = "microcentury"
queue arguments from arguments.txt
'''

  with open(scriptName, "w") as cnd_out:
     cnd_out.write(condor)

  script = '''#!/bin/sh -e

LOCAL=$1
reweightNode=$2
YEAR=$3
SYST=$4
CATEGORIZE=$5

#echo -e "Combining NLO samples for node ${NODE}, year ${YEAR}, systematic ${SYST}..."
#python ${LOCAL}/Reweight_NLO.py --node ${NODE} --year ${YEAR} --syst ${SYST}

#echo -e "Starting with combined NLO samples and reweighting to ${reweightNode}, year ${YEAR}, systematic ${SYST}..."

echo "CATEGORIZE: $CATEGORIZE"

if [ "$CATEGORIZE" = True ]; then 
  echo "Categorizing"
  python ${LOCAL}/Reweight_NLO.py --reweightNode ${reweightNode} --year ${YEAR} --syst ${SYST} --TDirec "" --categorize
else 
  echo "Not categorizing"
  python ${LOCAL}/Reweight_NLO.py --reweightNode ${reweightNode} --year ${YEAR} --syst ${SYST} --TDirec ""
fi  



echo -e "DONE";
'''

  arguments = []
  
  # For combining input NLO files 
  # for year in years:
  #   print("year:",year)
  #   systLabels = GetSystLabels(year)
  #   print("systematic labels:",systLabels)
  #   for node in nodes:
  #     print("node:",node)
  #     for systLabel in systLabels:
  #       arguments.append("{} {} {} {}".format(local, node, year, systLabel))

  # For reweighting already combined file with DNN score 
  for year in years:
    print("year:",year)
    systLabels = GetSystLabels(year)
    print("systematic labels:",systLabels)
    if(args.NominalOnly): systLabels = ["Nominal"]
    for reweightNode in reweightNodes:
      print("reweightNode:",reweightNode)
      for systLabel in systLabels:
        arguments.append("{} {} {} {} {}".format(local, reweightNode, year, systLabel, categorize))

  # Save arguments to text file to be input for condor jobs 
  with open("arguments.txt", "w") as args:
    args.write("\n".join(arguments))

  with open("run_script.sh", "w") as rs:
    rs.write(script) 

  submitCommand = "condor_submit {scriptName}".format(scriptName=scriptName)
  print("$ {submitCommand}".format(submitCommand=submitCommand))
  os.system(submitCommand)
  print("DONE")