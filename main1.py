#!/usr/bin/python

# Detecting communities in the Zachary Karate Club data using the label propagation algorithm

import sys
import numpy as np
import gv
from pygraph.classes.graph import graph
from pygraph.readwrite.dot import write
from random import random
import time

# Defining the main function and calling all the other relevant functions 
  
def main(input_file):
    data = input_file
    gr = make_graph(data)
    gr = detect_communities(gr)
    label_graph(gr)
    print_communities(gr)
    plot_graph(gr)


# Function to parse the required nodes and edges from the given data file.
#This function takes a .txt file as its input, parses and adds the nodes and edges to
#the graph and prints the total number of nodes and edges in the graph generated.
def make_graph(data):
    gr = graph()

    with open(data) as f:
        line = f.readline()
        while line != '':
            link = line.split()
            n1 = int(link[0])
            n2 = int(link[1])
            #print n1,n2
            if not gr.has_node(n1): 
                gr.add_node(n1)
                gr.add_node_attribute(n1, ('col', n1))
            if not gr.has_node(n2): 
                gr.add_node(n2)
                gr.add_node_attribute(n2, ('col', n2))

            if not gr.has_edge((n1,n2)): 
                gr.add_edge((n1,n2))
            #s = raw_input()
            line = f.readline()
    f.close()
    print "Graph has %i nodes and %i edges\n" % (len(gr.nodes()), len(gr.edges()) ) 

    return gr


# Function to extract communities by using the label propagation algorithm
# It specifies the termination condition as to stop propagating the labels too.

def detect_communities(gr):
    #iter_nbr = 3 + len(gr.edges()) / len(gr.nodes())
    conv = 0
    iter_nbr = 0

    while conv < 0.99 and iter_nbr<20:
        conv = modify_community(gr)
        iter_nbr += 1
        print "Iteration %i, convergence - %.2f" % (iter_nbr, conv)
        #_ = raw_input()

    return gr

# Function to change the topology of the network randomly and keep checking for the
# the matching labels in the neighbors. Returns the convergence value which is used
# by extract_communities to terminate the algorithm.

def modify_community(gr):
    convergence = 0.0
    nodes = shuffle(gr.nodes())
    
    for node in nodes:
        old_color = dict(gr.node_attributes(node)).get('col')
        #print old_color
        colors = [ dict(gr.node_attributes(n)).get('col') for n in gr.neighbors(node) ]
        #print colors
        color_dict = {c: colors.count(c) for c in set(colors)}
        #print color_dict
        max_val = max(color_dict.values())
        #print max_val
        variants = []
        for c in color_dict:
            if color_dict[c] == max_val:
                variants.append(c)

        new_color = randomly_pick(variants)
        #print new_color
        gr.add_node_attribute(node,('col',new_color))

        if new_color == old_color:
            convergence += 1

    return convergence/len(gr.nodes())


# Helper function for the change_community function that picks up a new label which
# is a new color in this case for every new instance. 

def randomly_pick(variants):
    nbr = len(variants)
    i = 0
    while True:
        if coin(1.0/nbr):
            return variants[i]
        else:
            nbr -= 1
            i += 1


# Helper function to change the topology of the network at certain specified conditions

def shuffle(nodes):
    N = len(nodes)
    for i in range(N):
        el = nodes.pop(int(N*random()))
        nodes.append(el)

    return nodes

# Helper function to select random values based on provided conditions

def coin(p):
    return random() < p


# Function to generate a graph illustrating different communities detected. Each community
# has a particular color specified by this function. 

def label_graph(gr):
    color = []
    for i in range(len(gr.nodes())):
        color.append(i)
    
    colors = [dict(gr.node_attributes(n)).get('col') for n in gr.nodes() ]

    for n in gr.nodes():
        #print "Node: %s, color %s"  % (n, dict(gr.node_attributes(n)).get('color'))
        c = colors.index(dict(gr.node_attributes(n)).get('col'))
        col = color[c%len(color)]
            
        #gr.add_node_attribute(n, ('color', col))
        gr.add_node_attribute(n, ('label',col))
        
# Function to print the total number of communities detected by using the
# label propagation algorithm and the size of each community. 

def print_communities(gr):
    
    colors = [ (n, dict(gr.node_attributes(n)).get('label')) for n in gr.nodes() ]
    #print colors
    
    cluster_dict = {}
    for c in colors:
        if c[1] in cluster_dict:
            cluster_dict[c[1]] += 1
        else:
            cluster_dict[c[1]] = 1
    #print cluster_dict
    print "\n%i communities were detected" % len(cluster_dict.keys())

    stat = {}
    for c in cluster_dict:
        if cluster_dict[c] in stat:
            stat[cluster_dict[c]] += 1
        else:
            stat[cluster_dict[c]] = 1
            
        #print "Cluster %s has %i nodes" % (c, cluster_dict[c])
    
    print "Cluster_size - occurrences"
    for s in stat:
        print "\t%i - %i" % (s, stat[s])

    total_time = time.clock() - start
    print "Time elapsed is %f seconds" %  total_time  

# Function to create a graphical structure of the final detected communities and 
# convert it into a .png file for display

def plot_graph(gr):
    """
    draws the graph to file
    """
    p = 100.0 / (len(gr.nodes())+1)
    gr_ext = graph()

    
    for node in gr.nodes():
        if coin(p):
            if not gr_ext.has_node(node):
                gr_ext.add_node(node,attrs=gr.node_attributes(node))
            for n in [ ed[0] for ed in gr.edges() if ed[1] == node ]:
                if coin(0.3):
                    if not gr_ext.has_node(n):
                        gr_ext.add_node(n,attrs=gr.node_attributes(n))
                    #print "Edges:",gr_ext.edges()
                    if not gr_ext.has_edge((node,n)):
                        gr_ext.add_edge((node,n)) 
    dot = write(gr_ext)
    gvv = gv.readstring(dot)
    gv.layout(gvv,'dot')    
    if args[1]== 'karate.txt':
        gv.render(gvv,'png','community1.png') 
    elif args[1] == 'email.txt':
        gv.render(gvv,'png','community2.png')
    elif args[1] == 'hep-th-citations.txt':
        gv.render(gvv,'png','community3.png')
    elif args[1] == 'amazon1.txt':
        gv.render(gvv,'png','community4.png')
    elif args[1] == 'p2p-Gnutella30.txt':
        gv.render(gvv,'png','community5.png')


# The entry point into the program is through this. THe arguments that need to be passed
# are the .py file that contains all the functions to detect communities and the 
# required dataset. 

if __name__ == '__main__':
    args = sys.argv[:]
    start = time.clock()
    if len(args) == 2:
        main(args[1])
    else:
        print "Usage: <python> <main1.py> <data>"
    
        
