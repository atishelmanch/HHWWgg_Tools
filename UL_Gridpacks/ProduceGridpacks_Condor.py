# Abraham Tishelman-Charny 
# 11 October 2021 
#
# The purpose of this script is to avoid running this command locally:
# python ProduceGridpacks.py --Prod VBF --Spin 0 --masses 250,260,270,280,300,320,350,400,450,500,550,600,650,700,750,800,850,900,1000,1250,1500,1750,2000,2500,3000 --condor ##-- Run dryrun first to produce cards 
# 
# But rather run a single mass point through its own condor job in order to produce all gridpack mass points in parallel 

# Example usage 
# python ProduceGridpacks_Condor.py --masses 250,260 
# condor_submit condor_job.txt

#!/usr/bin/python
import numpy as n
from ROOT import *
import sys, getopt
from array import array
import itertools
import argparse
import operator
import os

if __name__ == '__main__':

  parser =  argparse.ArgumentParser(description='cat MVA')
  parser.add_argument('--prod', default = "VBF", required=False, type=str, help = "Production mode. ggF, VBF")
  parser.add_argument('--spin', default = "0", required=False, type=str, help = "Spin of resonant particle")
  parser.add_argument('--masses', default = "250,260", required=False, type=str, help = "Comma separated list of mass points")
   
  args = parser.parse_args()
  masses = args.masses.split(',')

  print("masses:",masses)

  scriptName = "condor_job.txt"
  
  local = os.getcwd()
  if not os.path.isdir('error'): os.mkdir('error') 
  if not os.path.isdir('output'): os.mkdir('output') 
  if not os.path.isdir('log'): os.mkdir('log') 
   
  # Prepare condor jobs
  condor = '''executable              = run_script.sh
output                  = output/strips.$(ClusterId).$(ProcId).out
error                   = error/strips.$(ClusterId).$(ProcId).err
log                     = log/strips.$(ClusterId).log
transfer_input_files    = run_script.sh
# on_exit_remove          = (ExitBySignal == False) && (ExitCode == 0)
# periodic_release        = (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > (60*60))
    
+JobFlavour             = "microcentury"
# +AccountingGroup        = "group_u_CMS.CAF.ALCA"
queue arguments from arguments.txt
'''

  with open(scriptName, "w") as cnd_out:
     cnd_out.write(condor)

  script = '''#!/bin/sh -e

LOCAL=$1
PROD=$2
SPIN=$3
MASS=$4

#eval `scramv1 ru -sh` #cmsenv 

echo -e "Producing gridpack for mass point ${MASS} GeV...";
python ${LOCAL}/ProduceGridpacks.py --Prod ${PROD} --Spin ${SPIN} --masses ${MASS} --localDir ${LOCAL}

echo -e "DONE";
'''

  arguments = []
  prod = args.prod 
  spin = args.spin
  
  for mass in masses:
    arguments.append("{} {} {} {}".format(local, prod, spin, mass))

  # Save arguments to text file to be input for condor jobs 
  with open("arguments.txt", "w") as args:
    args.write("\n".join(arguments))

  with open("run_script.sh", "w") as rs:
    rs.write(script) 

  submitCommand = "condor_submit {scriptName}".format(scriptName=scriptName)
  print("$ {submitCommand}".format(submitCommand=submitCommand))
  os.system(submitCommand)
  print("DONE")  