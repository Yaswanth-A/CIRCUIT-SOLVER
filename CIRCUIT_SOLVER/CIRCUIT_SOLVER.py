"""
        EE2703 Applied Programming Lab - 2022
        Assignment 2
        Name : Allu Yaswanth
        Roll Number : EE20B007
        Date : 11th Feb 2022
"""

#Importing req modules
from pickle import FALSE, TRUE
from sys import argv, exit
import numpy as np
import math

#counting the number of nodes in the circuit
def nodecount(lines):
    cnt=0
    for line in lines:
        tokens = line.split('#')[0].split()
        
        if(tokens[1] != 'GND'):
            if(int(tokens[1]) > cnt):
                cnt = int(tokens[1])
        if(tokens[2] != 'GND'):
            if(int(tokens[2]) > cnt):
                cnt = int(tokens[2])        
    return cnt

#counting the number of voltage sources   
def volcount(lines):
    vol_cnt=0
    for line in lines:
        tokens = line.split('#')[0].split()

        if(tokens[0][0] == "V"):
            vol_cnt += 1
    return vol_cnt

#Defining the class resistor
class Resistor:
    
    def __init__(self, name, node1, node2, value):
        self.name = name
        self.node1 = node1
        self.node2 = node2
        self.value = value

    #MNA entries for resistor
    def MatrixEntries(self, G):
        if(self.node1 != 'GND' and self.node2 != 'GND'):
            a = int(self.node1)-1
            b = int(self.node2)-1
            z = float(self.value)
        
            G[a][a] += 1.0 / z
            G[a][b] += -1.0 / z
            G[b][a] += -1.0 / z
            G[b][b] += 1.0 / z
        
        if(self.node1 == 'GND'):
            b = int(self.node2)-1
            z = float(self.value)
        
            G[b][b] += 1.0 / z

        if(self.node2 == 'GND'):
            a = int(self.node1)-1
            z = float(self.value)
        
            G[a][a] += 1.0 / z    

#Defining class capacitor
class Capacitor:
    def __init__(self, name, node1, node2, value):
        self.name = name
        self.node1 = node1
        self.node2 = node2
        self.value = value

    #MNA entries for capacitor
    def MatrixEntries(self, G):
        if(self.node1 != 'GND' and self.node2 != 'GND'):
            a = int(self.node1)-1
            b = int(self.node2)-1
            z = complex(0,-1/(w*float(self.value)))
        
            G[a][a] += 1.0 / z
            G[a][b] += -1.0 / z
            G[b][a] += -1.0 / z
            G[b][b] += 1.0 / z
        
        if(self.node1 == 'GND'):
            b = int(self.node2)-1
            z = complex(0,-1/(w*float(self.value)))
        
            G[b][b] += 1.0 / z

        if(self.node2 == 'GND'):
            a = int(self.node1)-1
            z = complex(0,-1/(w*float(self.value)))
        
            G[a][a] += 1.0 / z 

#Defining class inductor
class Inductor:
    def __init__(self, name, node1, node2, value):
        self.name = name
        self.node1 = node1
        self.node2 = node2
        self.value = value

    #MNA entries for inductor
    def MatrixEntries(self, G):
        if(self.node1 != 'GND' and self.node2 != 'GND'):
            a = int(self.node1)-1
            b = int(self.node2)-1
            z = complex(0,(w*float(self.value)))
        
            G[a][a] += 1.0 / z
            G[a][b] += -1.0 / z
            G[b][a] += -1.0 / z
            G[b][b] += 1.0 / z
        
        if(self.node1 == 'GND'):
            b = int(self.node2)-1
            z = complex(0,(w*float(self.value)))
        
            G[b][b] += 1.0 / z

        if(self.node2 == 'GND'):
            a = int(self.node1)-1
            z = complex(0,(w*float(self.value)))
        
            G[a][a] += 1.0 / z 

#Defining class voltage source
class voltageSrc:
    def __init__(self, name, node1, node2, value):
        self.name = name
        self.node1 = node1
        self.node2 = node2
        self.value = value
     

    #MNA entries for a independent voltage source
    def MatrixEntries(self,G,I,count,nodecnt):
        count += 1
        vkl = nodecnt + count -1
        if self.node1 != 'GND' and self.node2 != 'GND' :
            a = int(self.node1)-1
            b = int(self.node2)-1
            G[a][vkl] = 1
            G[b][vkl] = -1
            G[vkl][a] = 1
            G[vkl][b] = -1

        elif self.node1 == 'GND' :
            b = int(self.node2)-1
            G[vkl][b] = -1
            G[b][vkl] = -1
        else :
            a = int(self.node1)-1
            G[vkl][a] = -1
            G[a][vkl] = -1
        
        I[vkl][0] = self.value

#Defining class for independent current source
class CurrentSource:
    def __init__(self, name, node1, node2, value):
        self.name = name
        self.node1 = node1
        self.node2 = node2
        self.value = value

    #MNA entries for independent current source
    def fillMatrix(self,name, node1, node2,I, value):
        if node1 != 'GND' and node2 != 'GND' :
            a = int(node1)-1
            b = int(node2)-1
            I[a] = -value
            I[b] = value 

        if node1 == "GND":
            b = int(node2)-1
            I[b] = value
        if node2 == 'GND':
            a = int(node1) -1 
            I[a] = -value
        

        
#Declaring constant variables for better readability
SPICE_START = '.circuit'
SPICE_END = '.end'
SPICE_AC = '.ac'
pi = 3.1415
ac_identified = FALSE
#initialising a list called tokens with null
tokens = [] 
count =0 # To count the index of voltage source

"""
Checking whether the number of arguments given are 2
if not through a error message and exit the program
"""

if len(argv) != 2:
    print('Please make sure that number of arguments must be 2')
    exit()

"""
Making sure to drop an error message if wrong file was given as an input using try-catch
"""
try:
    with open(argv[1]) as f:
        lines = f.readlines()
        f.close() # closing the file after reading
        start = -1; end = -2

        for line in lines:              # extracting circuit definition start and end lines
            if  SPICE_START== line[:len(SPICE_START)]:
                start = lines.index(line)
               
            elif SPICE_END== line[:len(SPICE_END)]:
                end = lines.index(line)

            elif SPICE_AC == line[:len(SPICE_AC)]:
                ac = lines.index(line)  
                ac_tokens = line.split()
                ac_identified = TRUE
                w=2*pi*float(ac_tokens[-1]) #angular frequency of the ac circuit

#validating circuit block,i.e. '.circuit' should always ahead of '.end'
        if start >= end:
            print("Invalid circuit definition")
            exit()
        else :
            for i in range(start+1, end):
                temp = ((lines[i].split('#')[0].split()))
                tokens.append(temp)
               

        m = nodecount(lines[start+1 : end]) #m = no. of nodes in circuit
        n = volcount(lines[start+1 : end])  #n = no. of voltage sources in the circuit
        dimension = m+n # m+n gives the order of the G matrix

        G = np.zeros((dimension,dimension), dtype="complex")  # Conductance matrix
        V = np.zeros((dimension,1), dtype="complex")  # Variable vector
        I = np.zeros((dimension,1), dtype="complex")  # Vector of independent sources

        for line in tokens:
            #Resistor 
            if(line[0][0] == 'R'):
                object = Resistor(line[0],line[1],line[2],line[3])
                object.MatrixEntries( G)
            #Capacitor    
            if(line[0][0] == 'C' and ac_identified == TRUE):
                object = Capacitor(line[0],line[1],line[2],line[3])
                object.MatrixEntries( G)
            #Inductor
            if(line[0][0] == 'L' and ac_identified == TRUE):
                object = Inductor(line[0],line[1],line[2],line[3])
                object.MatrixEntries( G)
            #Ind Voltage source
            if(line[0][0] == 'V'):
                if(line[3] == 'ac'):
                    realPart = float(line[-2])*math.cos(float(line[-1]))
                    imgPart = float(line[-2])*math.sin(float(line[-1]))
                    line[4] = complex(realPart/2,imgPart/2)
                    object = voltageSrc(line[0],line[1],line[2],line[4])
                    object.MatrixEntries(G,I,count, m)
                else:
                    line[3] = float(line[3])
                    object = voltageSrc(line[0],line[1],line[2],line[3])
                    object.MatrixEntries(G,I,count, m)
            #Ind current source
            if(line[0][0] == 'I'):
                if(line[3] == 'ac'):
                    realPart = float(line[-2])*math.cos(float(line[-1]))
                    imgPart = float(line[-2])*math.sin(float(line[-1]))
                    line[4] = complex(realPart/2,imgPart/2)
                    object = voltageSrc(line[0],line[1],line[2],line[4])
                    object.MatrixEntries(line[0],line[1],line[2],line[4],I)
                else:
                    object = voltageSrc(line[0],line[1],line[2],line[3])
                    object.MatrixEntries(line[0],line[1],line[2],line[3],I)
                    
        #Solving for V matrix GV = I; V = inv(G)I
        V = np.linalg.solve(G, I)

        print('The G_matrix is :')
        print(G)
        print('The I_matrix is :')
        print(I)

        print("Taking 'GND as reference node i.e. V(GND) = 0 + 0j")
        print('The V_matrix is :')
        print(V)

except IOError:
    print('Invalid file. Make sure you entered correct file name')
    exit()               
        