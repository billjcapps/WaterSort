import sys
import copy
import numpy as np
from operator import itemgetter
import time

def main ():    
    
    ## Define puzzle to solve

    ## Read color file
    colors = {}
    colorsByNum = {}
    colors["blank"] = 0
    colorNum = 1
    colorRows = open("colors.txt", "r").readlines()
    for c in colorRows:
        colors[c.rstrip()] = colorNum
        colorNum = colorNum + 1
    for c in colors:
        colorsByNum[colors[c]] = c

    ## New puzzle or read from file
    decision = ""
    while decision != "F" and decision != "N":
        decision = input("From {f}ile  or  {N}ew puzzle ?").upper()
    puzzle = input("Puzzle name: ")
    coded = []
    if decision == "F":
        with open("puzzles/" + puzzle + ".txt") as pzl:
            vialList = pzl.read().splitlines()
            pzl.close()
        for vial in vialList:
            v = [colors[drop] for drop in vial.split(", ")]
            coded.append(v)
    else:
        thisVial = ""
        readable = []
        vNum = 1
        while thisVial.upper() != "X":
            for key in colors:
                print(fmt(colors[key]) + " - " + key)
            print("   X - Complete")
            thisVial = input("Enter vial " + fmt(vNum) + " separated by spaces: ")
            if thisVial.upper() != "X":
                thisVialCoded = [int(i) for i in thisVial.split(" ")]
                thisVialReadable = [colorsByNum[c] for c in thisVialCoded]
                coded.append(thisVialCoded)
                readable.append(thisVialReadable)
                vNum = vNum + 1
                vn = 1
                print("\n\n")
                for v in readable:
                    print("Vial " + fmt(vn) + ": ", v)
                    vn = vn + 1
        ## output puzzle
        filename = "puzzles/" + puzzle + ".txt"
        with open(filename, "w") as newFile:  
            for t in readable:
                newFile.write(", ".join(t) + "\n")
            newFile.close()
            
    ## initiate tree
    tree = node(0, copy.deepcopy(coded), [])
    
    
    ## Create a default to compare for best and to determine if no solution exists
    best = node(99999, [[99999,99999,99999,99999],[99999,99999,99999,99999]], [])

    ## confirm best solution, original version relied on this instead of pruning
    for contender in tree.winners:
        if contender.depth < best.depth:
            best = contender    

    ## display optimal solution
    print("Optimal solution:")
    print(f"Found the solution in {tree.toc - best.tic:0.4f} seconds")    
    if best.depth == 99999:
        print("This is not a solvable puzzle!")
    else:
        print(str(best.depth) + " steps required")
        step = 1
        for s in best.instructions:
            print("Step " + fmt(step) + ": " + fmt(s[0]+1) + " --> " + fmt(s[1]+1))
            step = step + 1
        print("Solved!!")

        ## step through solve instructions
        if input("\nDo you want to step through instructions? Y/[N]").upper() == "Y":
            print("\n")
            step = 1
            for s in best.instructions:
                input("Step " + fmt(step) + ": " + fmt(s[0]+1) + " --> " + fmt(s[1]+1) + "\t\t...press any key")
                step = step + 1
            print("Solved!!")

    ## save optimal solution
    step = 1
    filename = "solutions/" + puzzle + ".txt"
    with open(filename, "w") as solution:  
        for s in best.instructions:
            solution.write("Step " + fmt(step) + ": " + fmt(s[0]+1) + " --> " + fmt(s[1]+1) + "\n")
            step = step + 1
        solution.close()
    
    ## this is the end of execution
    print("\n\nHave a great day!   :-)")
    return

class node:
    ## class for possible state, used to build

    ## define class variables
    tic = time.perf_counter()
    winners = []
    prune = {}
    shortestDepth = 99999
    initialSolve = False

    def __init__(self,depth, data, instructions):
        ## initialize node instance and then build subtree

        ## inherit traits and set defaults
        self.state = data
        k = copy.deepcopy(data)
        k.sort()
        k2 = []
        for i1 in k:
            for i2 in i1:
                k2.append(i2)
        self.key = tuple(k2)
        self.vials = len(data)
        self.children = []
        self.instructions = copy.deepcopy(instructions)
        self.depth = depth
        self.looping = False
        if depth == 0:
            self.type = "Root"
            node.tic = time.perf_counter()
        else:
            self.type = "Internal"

        ## prune or build and update dictionary
        if self.key not in self.prune:
            self.prune[self.key] = self.depth
            self.build()
        else:
            if self.prune[self.key] > self.depth:
                self.prune[self.key] = self.depth
                self.build()
            else:
                self.type = "Pruned"

        ## determine node status
        if len(self.children) == 0:
            self.type = "Leaf"
        if self.looping:
            self.type = "Infinite"
        for v in self.state:
            if (v[0] != v[1] or v[0] != v[2] or v[0] != v[3]):
                self.type = "Loser"
        if self.type == "Leaf":
            self.winners.append(self)
            node.shortestDepth = self.depth
        self.toc = time.perf_counter()

        ## output initial solution
        if ((node.initialSolve == False) and (self.type == "Leaf")):     
            node.initialSolve = True
            print("Initial solution:")
            print(f"Found the solution in {self.toc - node.tic:0.4f} seconds")    
            print(str(self.depth) + " steps required")
            step = 1
            for s in self.instructions:
                print("Step " + fmt(step)+ ": " + fmt(s[0]+1) + " --> " + fmt(s[1]+1))
                step = step + 1
            print("Solved!!\n")

        ## save results if requested
        return
        
    def canPour(self, vial1, vial2):
        ## apply logic to determine if a step is valid
        test = True

        ## prevent solved vials from filling an empty vial
        if(vial1[0] == vial1[1] and vial1[0] == vial1[2] and vial1[0] == vial1[3]):
            test = False

        ## prevent a full vial from being poured into
        if vial2[0] != 0:
            test = False

        ## prevent an empty vial from attempting to pour 
        if vial1[3] == 0:
            test = False

        ## confirm that the top color of the vials match or that the receiving vial is empty 
        if (vial1[3] > 0 and vial2[3] > 0 and vial1[np.nonzero(vial1)[0][0]] != vial2[np.nonzero(vial2)[0][0]]):
            test = False
        return test

    def pour(self, temp,  v1, v2):
        ## generate the state after the pour is complete

        ## determine what is being poured
        itemFrom = np.nonzero(temp[v1])[0][0]
        if temp[v2][3] == 0:
            itemTo = 3
        else:
            itemTo = np.nonzero(temp[v2])[0][0] - 1

        ## complete single unit pour
        color = temp[v1][itemFrom]
        temp[v1][itemFrom] = 0
        temp[v2][itemTo] = color

        ## pour additional units if possible
        if ((itemFrom < 3) and (temp[v1][itemFrom + 1] == color) and temp[v2][0] == 0):
            result = copy.deepcopy(self.pour(temp, v1, v2))
        else:
            result = copy.deepcopy(temp)
        return result
    
    def build(self):
        ## build subtree

        ## iterate through possible pours
        for v1 in range(0, self.vials):
            for v2 in range(0, self.vials):

                ## pour if possible
                if ((self.canPour(self.state[v1],self.state[v2])) and (v1 != v2)):
                    temp = copy.deepcopy(self.state)
                    afterPour = self.pour(temp, v1, v2)    

                    ## prune non-optimal branches or generate a child
                    if (self.depth < node.shortestDepth):
                        newInstructions = copy.deepcopy(self.instructions)
                        newInstructions.append([v1,v2])
                        self.children.append(node(self.depth + 1, afterPour, newInstructions ))                        
        return

def fmt(st):
    ## format integers for right-justified output
    return ("    " + str(st))[-4:]

## begin code execution    
main()
