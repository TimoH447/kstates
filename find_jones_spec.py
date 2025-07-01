import os 
import pickle
import signal
import sys
from random import randint
from itertools import product
from src.two_bridge_knots import TwoBridgeDiagram


def handle_interrupt(sig,frame):
    print("\n Interrupted! Saving memo...")
    save_memo(knot_name,memo)
    sys.exit(0)

signal.signal(signal.SIGINT, handle_interrupt)

def get_memo_filename(knot_name):
    return f"memo_{knot_name}.pkl"

def load_memo(knot_name):
    filename = get_memo_filename(knot_name)
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            print(f"Loading memo from {filename}")
            return pickle.load(f)
    else:
        print("No existing memo for this knot yet.")
        return {}

def save_memo(knot_name,memo):
    filename= get_memo_filename(knot_name)
    with open(filename, "wb") as f:
        pickle.dump(memo,f)
    print(f"Memo saved to {filename}")

    
def get_key(fixed_segment,specialization):
    key = f"i{fixed_segment}_"
    for variable in specialization:
        key += str(variable[0])
        key += str(variable[1])
    return key
    
def evaluate(jones,lattice,specialization,positives):
    fixed_segment = lattice.fixed_segment
    key = get_key(fixed_segment,specialization)
    if key in memo:
        result = memo[key]
    else:
        result = test_jones_specialization(jones,lattice, specialization)
        memo[key] = result
    if result==True:
        positives.append(key)
        print(f"Found candidate: {fixed_segment}, {specialization}.")

def test_jones_specialization(jones,lattice,specialization):
    f_pol = lattice.get_f_polynomial()
    specialization = f_pol.get_specialization(specialization)
    specialized_pol = f_pol.specialize_to_laurent(specialization)
    if specialized_pol.equal_up_to_factor(jones):
        specialized_pol.print_normalized_to_latex()
        return True
    else:
        return False

def get_random_input():
    coefficient = randint(-2,2)
    if coefficient==0:
        return [0,0]
    else:
        return [coefficient,randint(-2,2)]

def get_random_specialization(lattice):
    specialization = [[0,0]]*lattice.diagram.number_of_segments
    transposed_segments = lattice.transposed_segments
    for transposed in transposed_segments:
        specialization[transposed-1] = get_random_input()
    return specialization

def get_specialization_iter(lattice):
    transposed_segments  =lattice.transposed_segments
    spec_iter = product([-2,-1,0,1,2],repeat=2*len(transposed_segments))
    return spec_iter

def embed_input(lattice,input):
    specialization = [[0,0]]*lattice.diagram.number_of_segments
    transposed_segments = lattice.transposed_segments
    for i,transposed in enumerate(transposed_segments):
        specialization[transposed-1] = [input[2*i],input[2*i+1]] 
    for monom in specialization:
        if monom[0]==0:
            monom[1]=0
    return specialization

def bruteforce_spec(jones,lattice,results):
    spec_iter = get_specialization_iter(lattice)
    i=0
    for spec in spec_iter:
        i+=1
        if i%100000==0:
            print(f"{i} iterations")
        specialization = embed_input(lattice, spec)
        evaluate(jones,lattice,specialization,results)
        
tests = [
    {"knot_name": "k1_1_2", "fixed_segment":2, "normalform": [1,1,2]},

    {"knot_name": "k3_2", "fixed_segment": 6, "normalform": [3,2]},
    {"knot_name": "k3_2", "fixed_segment": 9, "normalform": [3,2]},

    {"knot_name": "k2_3", "fixed_segment": 3, "normalform": [2,3]},
    {"knot_name": "k2_3", "fixed_segment": 8, "normalform": [2,3]},
    {"knot_name": "k2_3", "fixed_segment": 6, "normalform": [2,3]},


    {"knot_name": "k4_2", "fixed_segment": 5, "normalform": [4,2]},
    {"knot_name": "k4_2", "fixed_segment": 11, "normalform": [4,2]},

    {"knot_name": "k2_4", "fixed_segment": 3, "normalform": [2,4]},
    {"knot_name": "k2_4", "fixed_segment": 7, "normalform": [2,4]},
    {"knot_name": "k2_4", "fixed_segment": 9, "normalform": [2,4]},

    {"knot_name": "k2_1_1_1", "fixed_segment": 3, "normalform": [2,1,1,1]},
    {"knot_name": "k2_1_1_1", "fixed_segment": 3, "normalform": [2,1,1,2]},
         ]

for test in tests:
    knot_name = test["knot_name"]
    fixed_segment = test["fixed_segment"]
    knot = TwoBridgeDiagram(test["normalform"])
    jones = knot.get_jones_polynom()
    jones.print_normalized_to_latex()
    lattice = knot.get_lattice(fixed_segment)
    print(f"number of combinations to check: {5**(2*len(lattice.transposed_segments))}")
    memo = load_memo(knot_name)
    results = []
    bruteforce_spec(jones,lattice,results)
    with open("results.txt","a") as f:
        f.write(f"\n Results Knot {knot_name} and segment {fixed_segment}: \n")
        f.write(f"Found combinations: \n")
        for result in results:
            f.write(str(result)+"\n")
    print(results)
    save_memo(knot_name,memo)    