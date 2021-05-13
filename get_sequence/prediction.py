#!/usr/bin/env python3
#(c) Yuan Zhang in Department of Statistic, FSU
# Nov.1, 2018
# This script is used to clean the pdb file data
# Get boxed information with atom been labeled
# Call model for prediction

import sys
import os, glob #I added
import numpy as np
import copy
from .prediction_functions import *      # 05/29/2019 Yang: import functions for data preprocessing and prediction
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logomaker
import pandas as pd


def convAA(aa):    # mode = 'l', 'n', 'f'
    aa = str(aa)
    AA_1 = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']
    AA_3 = ["ALA","CYS","ASP","GLU","PHE","GLY","HIS","ILE","LYS","LEU","MET","ASN","PRO","GLN","ARG","SER","THR","VAL","TRP","TYR"]
    if len(aa)==3:
        return AA_1[AA_3.index(aa)]
    elif len(aa)==1:
        return AA_3[AA_1.index(aa)]

def read_pdb(file_name, target_chain):       # skip alternate position version
    target_atom = ['C', 'CA', 'N', 'O', 'OXT']
    data = []
    count = -1
    residue = 0     # label to track if the residue changed
    resname = []
    chain = []
    #check_protein=1
    resname_flag='UNK'
    with open (file_name) as f:
        for line in f:
            a = line
            if a[0:5]=='MODEL':
                if int(map(str,a.split())[1])==1:
                    continue
                else:
                    break
            if a[0:3]=='TER':
                continue
            if target_chain == 'all' or a[21] == target_chain.upper():   # By Yuan (05/11/2021)keep all the chains or only keep target chain
                count+=1
                x = [a[12:16].strip(),a[16],a[17:20].strip(),a[22:27].strip(),[float(a[30:38]),float(a[38:46]),float(a[46:54])]]
                if count == 0:  # first row of pdb file
                    data.append({})
                    residue = x[3]
                    resname_flag = x[2]
                    resname.append(x[2])
                    chain.append(a[21])
                else:
                    if x[3]!=residue or x[2]!=resname_flag:
                        residue = x[3]
                        resname_flag = x[2]
                        resname.append(x[2])
                        data.append({})
                        chain.append(a[21])
                if x[1] == ' ' or x[1] == 'A':
                    if x[0] in target_atom:
                        data[-1].update({x[0]:np.array(x[4])})
    f.close()
    return data,resname,chain

def add_atom(a1, a2, a3, bond, angle, dih):
    # a1-a2-a3-a4, bond=length of a3-a4, angle = a2-a3-a4, dih = a1-a2-a3-a4
    # angle should be in radian
    a1 = np.array(a1)
    a2 = np.array(a2)
    a3 = np.array(a3)
    A23 = a3 - a2
    A21 = a1 - a2
    # find x, y, z direction
    x = A23/np.linalg.norm(A23)
    Z = np.cross(A23, A21)
    z = Z/np.linalg.norm(Z)
    y = np.cross(z,x)
    # get projection on x,y,z
    px = bond * np.cos(np.pi - angle)
    py = bond * np.sin(np.pi - angle) * np.cos(dih)
    pz = bond * np.sin(np.pi - angle) * np.sin(dih)
    return a3 + px*x + py*y + pz*z
 
def redraw_CB(data):
    Data = copy.deepcopy(data)
    bond = 1.521
    angle = 110.4 * np.pi/180
    dih = 122.55 * np.pi/180
    for i in range (len(data)):
        if 'CA' in data[i] and 'C' in data[i] and 'N' in data[i]:
            CB = add_atom(data[i]['N'], data[i]['C'], data[i]['CA'], bond, angle, dih)
            Data[i].update({'CB':list(CB)})
    return Data

def label_atom_BBS(resname,atom):
    atom_label={
    'ARG':{'N':17,'CA':18,'C':19,'O':20,'CB':1},
    'HIS':{'N':17,'CA':18,'C':19,'O':20,'CB':2},
    'LYS':{'N':17,'CA':18,'C':19,'O':20,'CB':3},
    'ASP':{'N':17,'CA':18,'C':19,'O':20,'CB':4},
    'GLU':{'N':17,'CA':18,'C':19,'O':20,'CB':5},
    'SER':{'N':17,'CA':18,'C':19,'O':20,'CB':6},
    'THR':{'N':17,'CA':18,'C':19,'O':20,'CB':7},
    'ASN':{'N':17,'CA':18,'C':19,'O':20,'CB':8},
    'GLN':{'N':17,'CA':18,'C':19,'O':20,'CB':9},
    'CYS':{'N':17,'CA':18,'C':19,'O':20,'CB':10},
    'GLY':{'N':17,'CA':18,'C':19,'O':20,'CB':11},
    'PRO':{'N':17,'CA':18,'C':19,'O':20,'CB':12},
    'ALA':{'N':17,'CA':18,'C':19,'O':20,'CB':13},
    'VAL':{'N':17,'CA':18,'C':19,'O':20,'CB':14},
    'ILE':{'N':17,'CA':18,'C':19,'O':20,'CB':15},
    'LEU':{'N':17,'CA':18,'C':19,'O':20,'CB':16},
    'MET':{'N':17,'CA':18,'C':19,'O':20,'CB':22},
    'PHE':{'N':17,'CA':18,'C':19,'O':20,'CB':23},
    'TYR':{'N':17,'CA':18,'C':19,'O':20,'CB':24},
    'TRP':{'N':17,'CA':18,'C':19,'O':20,'CB':25}
    }
    if atom=='OXT':
        return 21       # define the extra oxygen atom OXT on the terminal carboxyl group as 21 instead of 27 (changed on March 19, 2018)
    elif atom in atom_label[resname]:
        return atom_label[resname][atom]
    else:
        return 0

def label_atom_BBO(atom):
    atom_label = {'N':1, 'CA':2, 'C':3, 'O':4, 'OXT':5, 'CB':6}
    if atom in atom_label.keys():
        return atom_label[atom]
    else:
        return 0

def get_norm(v1,v2):    # get norm vector perpendicular with the plain decided by v1 and v2, direction is right hand rule v1 x v2
    v1 = np.array(v1)
    v2 = np.array(v2)
    v = np.cross(v1,v2)
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    else:
        return v/norm

def get_rot_angle(ini,final,n): # get rotaion angle from ini vector to final vecter
    ini = np.array(ini)
    final = np.array(final)
    Dot_result = np.dot(ini,final)
    norm_ini = np.linalg.norm(ini)
    norm_final = np.linalg.norm(final)
    if norm_ini*norm_final == 0:
        angle = np.pi 
    else:
        angle = np.arccos(Dot_result/norm_ini/norm_final)
        if np.dot(np.cross(ini,final),n)>=0:
            angle = angle
        else:
            angle = 2*np.pi - angle
    return angle

def norm_vect(v):
    v = np.array(v)
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    else:
        return v/norm

def rot_matric(C,angle):    # get rotation matrix with C as axis vector and angle in radian
    x,y,z = norm_vect(C)
    s = np.sin(angle)
    c = np.cos(angle)
    R1 = [c+np.power(x,2)*(1-c), x*y*(1-c)-z*s, x*z*(1-c)+y*s]
    R2 = [y*x*(1-c)+z*s, c+np.power(y,2)*(1-c), y*z*(1-c)-x*s]
    R3 = [z*x*(1-c)-y*s, z*y*(1-c)+x*s, c+np.power(z,2)*(1-c)]
    return np.array([R1,R2,R3])

def get_rot_matrix(CA, C, N, O):  #get the rotation matrix where CA-C along -x and CA-N on the x-y plain, O is just in case CA-C-N is on a straight line
    Z=np.array([0,0,1])
    X=np.array([1,0,0])
    CaC=np.array(C)-np.array(CA)
    CaN=np.array(N)-np.array(CA)
    if np.linalg.norm(np.cross(CaC, CaN))==0:    # if CA, C, N on the same line, use O instead N (rear case)
        N=O
        CaN=np.array(N)-np.array(CA)
    # first step: rotate the norm of C-CA-N plain along with Z
    n = get_norm(CaN,CaC)
    axis = get_norm(n,Z)
    if list(axis)==[0,0,0]:
        if np.dot(n,Z)>0:
            R1=np.array([[1,0,0],[0,1,0],[0,0,1]])
        else:
#            print 'On -Z direction'
            R1=np.array([[1,0,0],[0,-1,0],[0,0,-1]])
    else:
        angle = get_rot_angle(n,np.array([0,0,1]),axis)
        R1 = rot_matric(axis,angle)
    # second step: rotate CaC with -X
    ini = np.dot(R1,CaC)
    final = -X
    axis = Z
    angle = get_rot_angle(ini,final,axis)
    R2 = rot_matric(axis,angle)
    return np.dot(R2,R1)

def boxed_amino(data, resname, pred_range, mode='BBO', cutoff=18.0):
    result = []        # result = [[box for each residue], [],...],  [box for each residue] = [[atom_label, x, y, z], [atom_label, x, y, z], ...]
    numRes = -1
    for j in pred_range:
        if 'CA' in data[j] and 'C' in data[j] and 'N' in data[j] and 'O' in data[j]:
            result.append([])
            numRes += 1
            # translate the system to make CA at origin (0,0,0)
            CA = data[j]['CA']
            for i in range (len(data)):
                for item in data[i].keys():
                    name, coor = item,data[i][item]
                    coor = coor - CA
                    data[i].update({name:coor})    
            # rotate the system to make N, CA, C on x-y plain and CA-C along -x direction
            CA = data[j]['CA']
            N = data[j]['N']
            C = data[j]['C']
            O = data[j]['O']
            R = get_rot_matrix(CA,C,N,O)
            for i in range (len(data)):
                for item in data[i]:
                    name, coor = item,data[i][item]
                    coor = np.dot(R,coor)
                    data[i].update({name:coor})
                    if -cutoff/2<=coor[0]<=cutoff/2 and -cutoff/2<=coor[1]<=cutoff/2 and -cutoff/2<=coor[2]<=cutoff/2:
                        if mode == 'BBO':
                            if label_atom_BBO(name) != 0:
                                result[numRes].append([label_atom_BBO(name), coor[0], coor[1],coor[2]])    
                        elif mode == 'BBS':
                            if i==j and name=='CB':
                                result[numRes].append([26, coor[0], coor[1],coor[2]])            
                            elif label_atom_BBS(resname[i], name) != 0:
                                result[numRes].append([label_atom_BBS(resname[i], name), coor[0], coor[1],coor[2]]) 
    return result

def reform(v, top, c=0.0):
    V = sorted(v, reverse=True)
    flag = V[top-1]
    result = [x if x>=flag else 0.0 for x in v]
    return result

def LOGO(Probability, figure_name, xi_ind=1, top_rank=20, figsize=(10, 2.5)):
    AA_1 = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']
    P1 = [reform(x[0],top_rank) for x in Probability]
    df = pd.DataFrame(data=P1, columns=AA_1)
    ww_logo = logomaker.Logo(df,color_scheme='skylign_protein',vpad=.1,width=.8,fade_probabilities=False, figsize=figsize)
    ww_logo.ax.set_xlim([-1, len(df)])
    #ww_logo.style_xticks(anchor=0, spacing=2)#, rotation=45)
    ww_logo.ax.set_xticks(range(0, len(df), 2))
    ww_logo.ax.set_xticklabels(range (xi_ind,len(df)+xi_ind,2))
    ww_logo.ax.set_yticks([0, 0.5, 1.0])
    ww_logo.ax.set_ylabel('probability')
    ww_logo.fig.savefig('./pred_result/static/pred_result/images/' + figure_name) #setting relative path
    plt.clf()
    plt.cla()

def BBO_figure(Probability, figure_name):
    AA_1 = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y']
    plt.figure(figsize=(10,3))
    x = [i-0.5 for i in range (20)]
    y = Probability[0][0]
    plt.bar(x, y, width=1.0, color='orange', edgecolor='r',tick_label=AA_1, alpha=0.8)
    plt.ylabel('probability')
    plt.xlim([-2,20])
    plt.savefig('./pred_result/static/pred_result/images/' + figure_name)


#if __name__=='__main__': 
def main(pdbfile, target_chain, target_res, mode, pdb_file_name):  
    '''
    pdbfile: the input pdb file name
    data = [{atom:coordinate,...}, {atom:coordinate,...}...]
    resname = [resname1, resname2, ...], len(data) = len(resname)
    '''
    '''
    ARG_VER=sys.argv
    pdbfile=sys.argv[1]
    target_chain=sys.argv[2]
    target_res=sys.argv[3]
    mode = sys.argv[4]
    model = sys.argv[5]      # 05/29/2019 Yang: choose from 30/90, denote id30 or id90 models
    
    if len(ARG_VER) == 7:
        result_file = sys.argv[6]
    else:
        result_file = 'prediction_result'
    '''
    
    result_file = 'prediction_result'
#    pdbfile= '3gfs.pdb'
#    target_chain= 'A'
#    target_res= '1,-1'

    if(target_chain.isalpha()==0):
        target_chain="all"
    
    if (mode != 'BBO') & (mode != 'BBS'):
        mode = 'BBO'
    
    #if (model != '30') & (model != '90'):
    #   model = '90'
    model='90'

        
    
    
    
    cutoff=18.0
    data,resname,chain_info = read_pdb(pdbfile, target_chain)
    Data = redraw_CB(data)
    begin, end = target_res.split(',')
    if end == '-1':
        end = len(Data)
    pred_range = [i for i in range (int(begin)-1, int(end))]
    result = boxed_amino(Data, resname, pred_range, mode=mode, cutoff=18.0)
    
    mode = mode + model      # 05/29/2019 Yang: BBO - > BBO30 this kind of things
    prediction, prediction_prob = test(result, mode)      # 05/29/2019 Yang: perform prediction
    #print prediction
    #print prediction_prob

    # output result
    '''
    original_seq = [convAA(aa) for aa in np.array(resname)[pred_range]]
    item = 'Input sequence:\n'+''.join(original_seq)+'\n'
    predicted_seq = [convAA(aa) for aa in prediction]
    item += '\nPredicted sequence:\n'+''.join(predicted_seq)+'\n'
    output_seq=("%s" %(item))
    print(output_seq)
    '''

    original_seq = [convAA(aa) for aa in np.array(resname)[pred_range]]
    original_seq = ''.join(original_seq)+'\n'
    predicted_seq = [convAA(aa) for aa in prediction]
    predicted_seq = ''.join(predicted_seq)+'\n'
    
    #Removing previous pdb's resultant .txt files
    dir = './pred_result/static/pred_result/result/'
    for file in os.scandir(dir):
        os.remove(file.path)

    #Removing previous pdb's resultant images 
    dir = './pred_result/static/pred_result/images/'
    for file in os.scandir(dir):
        os.remove(file.path)

    ''' #This was required for only showing the predicted sequence file
    s = pdb_file_name + "_seq.txt"
    result_file_path=os.path.join('./pred_result/static/result/',s)

    #f=open("./result_files/"+ result_file)
    print("IN .PY: ",result_file_path)
    f = open(result_file_path, 'w') #It might not be needed as I am not serving the output from here
    f.writelines(item)
    f.close()
    '''
    
    s = pdb_file_name + "_prob.txt"
    prob_file_path=os.path.join('./pred_result/static/pred_result/result/',s)
    head = 'Input_AA\tPred_AA\t\t'+'\t'.join(['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y'])+'\n'
    item = head+'\n'.join([original_seq[i]+'\t\t'+convAA(prediction[i])+'\t\t'+'\t'.join(['%.2f'%(x*100) for x in prediction_prob[i][0]]) for i in range (len(prediction))])+'\n'
    output_prob=("%s" %(item))
    f = open(prob_file_path, 'w') #I wrote
    #f = open(result_file+'_prob.txt', 'w') #Yuan wrote
    f.writelines(item)
    f.close()
    #with open(result_file, 'w') as f:
    #    for item in prediction:
    #        f.write("%s\n" % item)
    #f.close()
    
    # output Logo
    xtick_len = 40
    if mode.startswith('BBO'):
        num_fig = int(np.ceil(len(prediction_prob)/float(xtick_len)))   # every figure shows xtick_len residues, i.e., 40
        for i in range (num_fig):
            if i == num_fig-1:
                Pred_prob = prediction_prob[i*xtick_len:]
                fig_p = len(prediction_prob)%xtick_len/float(xtick_len)
                LOGO(Pred_prob, pdb_file_name+'_'+str(i+1)+'_logo.png', xi_ind=i*xtick_len+1, top_rank=6, figsize=(10*fig_p+1, 2.5))
                # eps format will not show the fade effection
            else:
                Pred_prob = prediction_prob[i*xtick_len : (i+1)*xtick_len]
                LOGO(Pred_prob, pdb_file_name+'_'+str(i+1)+'_logo.png', xi_ind=i*xtick_len+1, top_rank=6, figsize=(10, 2.5))
    
    else:
        BBO_figure(prediction_prob, pdb_file_name+'_logo.png')

    
    #To make a list of all the image names to render it to the template from view
    files = os.listdir(dir)
    image_names=[]
    for f in files:
        print(f)
        image_names.append(f)

    sorted(image_names, key=str.lower)

    #return output_seq, output_prob, image_names
    return original_seq, predicted_seq, output_prob, image_names
