########################################################################################################################
# Abraham Tishelman-Charny                                                                                             #
# 20 October 2020                                                                                                      #
#                                                                                                                      #
# The purpose of this module is to provide a class and methods for a CheckMC object to be used by the                  #
# CheckMCStatus module.                                                                                                #                                                                                                          
########################################################################################################################

import os 
import pandas as pd 
from matplotlib import pyplot as plt 
import numpy as np 

class CheckMC:

    def __init__(self, primaryDatasetName, secondaryDatasetName, step, instance, outDsets):
        self.primaryDatasetName = primaryDatasetName
        self.secondaryDatasetName = secondaryDatasetName
        self.step = step 
        self.instance = instance
        self.outDsets = outDsets

    def GetDatasetNames(self):
        print"Querying DAS..."
        if(not os.path.exists("Datasets")):
            print"Creating output directory: Datasets"
            os.system('mkdir Datasets')   
        os.system("rm Datasets/%s.txt"%(self.outDsets))
        dasCommand = "dasgoclient --query='/%s/%s/%s instance=%s' >> Datasets/%s.txt"%(self.primaryDatasetName, self.secondaryDatasetName, self.step, self.instance, self.outDsets)
        print"DAS Command:",dasCommand
        os.system(dasCommand)
        print"DAS Command:",dasCommand

    def GetDsetMetaData(self, dsets):
        grepString = "nevents"
        if(not os.path.exists("MetaData")):
            print"Creating output directory: MetaData"
            os.system('mkdir MetaData')
        outFile = "MetaData/%s_MetaData.txt"%(self.outDsets)
        outLabel = "MetaData"
        os.system("rm %s"%(outFile))
        for dset in dsets[0]:
            print"dset:",dset
            dasCommand = "dasgoclient --query 'summary dataset=%s instance=%s' -json | grep %s >> %s"%(dset,self.instance, grepString, outFile)
            os.system(dasCommand)       

    def Plot(self, dsets, ol, Process_):
        nodes, nEvents = GetPlotVals(self.outDsets, dsets, Process_)

        ##-- Set Label Font Size based on number of nodes 
        fontsize = 8 
        if( (len(nodes) >= 6) and len(nodes) <= 13): fontsize = 9
        elif(len(nodes) <= 5): fontsize = 12
        else: fontsize = 5

        print "nodes: ",nodes
        print "nEvents: ",nEvents

        x_pos = [i for i, _ in enumerate(nodes)]
        y_pos = np.arange(len(nodes))
        plt.figure(figsize=(8, 4))
        plt.bar(y_pos, nEvents, align='center', color=(0.052478,0.2303,0.717,0.5), edgecolor='black')
        plt.xticks(y_pos, nodes)
        plt.ylim(ymin=0,ymax=420000)
        plt.ylabel('Nevents')
        if(Process_ != "Resonant"):
            plt.xlabel('Non-Resonant Node')
        else: plt.xlabel('Resonant Mass')
        plt.xticks(fontsize=fontsize)
        plt.title('%s MiniAOD Nevents'%(self.outDsets))
        plt.hlines(400000,-0.5,len(nodes), linestyles='dashed', colors='black')

        plt.savefig("%s/%s-%s_nEvents.png"%(ol,Process_,self.outDsets))
        plt.close()

        # add time stamp to plot 
        # Could also be useful to have three bar plot. One for each year or final state. 

def GetPlotVals(outDsets_, dsets_, Process):
    nodes_, nEvents_ = [], [] 
    MetaData = pd.read_csv('MetaData/%s_MetaData.txt'%(outDsets_), header=None)

    if(Process != "Resonant"):

        datasets = dsets_[0].tolist()
        nodes = [str(fullSt.split('/')[1].split('_')[2]) for fullSt in datasets]
        nEvents = [int(nEvent_str.split(':')[-1]) for nEvent_str in MetaData[12]] ##-- 12: nEvents 
        node_nEvt_pairs = zip(nodes,nEvents)

    else: 
        datasets = dsets_[0].tolist()
        nodes = [str(fullSt.split('/')[1].split('_')[1]) for fullSt in datasets] # M-X
        for i,node in enumerate(nodes): 
            node = node.replace("M-","")
            nodes[i] = node 
        nEvents = [int(nEvent_str.split(':')[-1]) for nEvent_str in MetaData[12]] ##-- 12: nEvents 
        node_nEvt_pairs_unsorted = zip(nodes,nEvents)        
        node_nEvt_pairs = sorted(node_nEvt_pairs_unsorted, key = lambda x: float(x[0]))

    # print "nodes:",nodes
    # print "nEvents:",nEvents
    # print "process:",Process

    if(Process == "GF_LO"):
        for pair in node_nEvt_pairs:
            node, nEvent = pair
            if(not "cHHH" in node):
                nodes_.append(node)
                nEvents_.append(nEvent)
    elif(Process == "GF_NLO"):
        for pair in node_nEvt_pairs:
            node, nEvent = pair
            if("cHHH" in node):
                nodes_.append(node)
                nEvents_.append(nEvent) 
    elif(Process == "VBF_LO"):
        for pair in node_nEvt_pairs:
            node, nEvent = pair
            if("C2V" in node):
                nodes_.append(node)
                nEvents_.append(nEvent) 
    elif(Process == "Resonant"):
        for pair in node_nEvt_pairs:
            node, nEvent = pair
            # if("C2V" in node):
            nodes_.append(node)
            nEvents_.append(nEvent)         
        
                             
    return nodes_, nEvents_  

def GetProcessLabel(Process):
    outName_Process_Dict = {
        "*_node_*" : "GF",
        "*CV_*_C2V_*_C3_*_*" : "VBF",
        "*" : "Resonant"
    }    
    return outName_Process_Dict[Process]

def GetFSLabel(fullFS):
    outName_FS_Dict = {
        "GluGluToHHTo2G2Qlnu*": "Semi-Leptonic", 
        "GluGluToHHTo2G4Q*": "Fully-Hadronic", 
        "GluGluToHHTo2G2l2nu*" : "Fully-Leptonic",
        "GluGluToHHTo2G2ZTo2G4Q*" : "ZZ-Fully-Hadronic",

        ##-- GF Spin 0, 2 
        "GluGluToRadionToHHTo2G2Qlnu_M-*" : "GF-Spin-0-Semi-Leptonic",
        "GluGluToBulkGravitonToHHTo2G2Qlnu_M-*" : "GF-Spin-2-Semi-Leptonic",
        "GluGluToRadionToHHTo2G2l2nu_M-*" : "GF-Spin-0-Fully-Leptonic",
        "GluGluToBulkGravitonToHHTo2G2l2nu_M-*" : "GF-Spin-2-Fully-Leptonic",
        "GluGluToRadionToHHTo2G4Q_M-*" : "GF-Spin-0-Fully-Hadronic",
        "GluGluToBulkGravitonToHHTo2G4Q_M-*" : "GF-Spin-2-Fully-Hadronic",   
        "GluGluToRadionToHHTo2G2ZTo2G4Q_M-*" : "GF-Spin-0-ZZgg-Fully-Hadronic",
        "GluGluToBulkGravitonToHHTo2G2ZTo2G4Q_M-*" : "GF-Spin-2-ZZgg-Fully-Hadronic",           

        ##-- VBF Spin 0, 2            
        "VBFToRadionToHHTo2G2Qlnu_M-*" : "VBF-Spin-0-Semi-Leptonic",
        "VBFToBulkGravitonToHHTo2G2Qlnu_M-*" : "VBF-Spin-2-Semi-Leptonic",
        "VBFToRadionToHHTo2G2l2nu_M-*" : "VBF-Spin-0-Fully-Leptonic",
        "VBFToBulkGravitonToHHTo2G2l2nu_M-*" : "VBF-Spin-2-Fully-Leptonic",
        "VBFToRadionToHHTo2G4Q_M-*" : "VBF-Spin-0-Fully-Hadronic",
        "VBFToBulkGravitonToHHTo2G4Q_M-*" : "VBF-Spin-2-Fully-Hadronic",    
        "VBFToRadionToHHTo2G2ZTo2G4Q_M-*" : "VBF-Spin-0-ZZgg-Fully-Hadronic",
        "VBFToBulkGravitonToHHTo2G2ZTo2G4Q_M-*" : "VBF-Spin-2-ZZgg-Fully-Hadronic",                     
    }
    return outName_FS_Dict[fullFS]

def GetYearLabel(fullYear):
    outName_year_Dict = {
        "*RunIISummer16MiniAODv3*": "2016", 
        "*RunIIFall17MiniAODv2*": "2017", 
        "*RunIIAutumn18MiniAOD*" : "2018"
    }   
    return outName_year_Dict[fullYear]    
      
def CheckMakeOutLocation(outLoc_):
    if(not os.path.exists(outLoc_)):
        print"Creating output directory: %s"%(outLoc_)
        beforeOutLoc = "%s/../"%(outLoc_)
        os.system('mkdir %s'%(outLoc_))
        os.system('cp %s/index.php %s'%(beforeOutLoc,outLoc_))  

def GetProcesses(PhysicsType):
    GF_dsetStr = "*_node_*"
    VBF_dsetStr = "*CV_*_C2V_*_C3_*_*"
    


    processDict = {
        "NonResonant" : [GF_dsetStr, VBF_dsetStr],
        "Resonant" : ["*"]
    }   
    return processDict[PhysicsType]     