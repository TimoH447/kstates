from itertools import product

def simplify_laurent_polynom(polynom):
    simplified_polynom = []
    for summand in polynom:
        if any(term[1] == summand[1] for term in simplified_polynom):
            for term in simplified_polynom:
                if term[1] == summand[1]:
                    term[0] += summand[0]
        else:
            simplified_polynom.append(summand)
    return simplified_polynom

def specialize_monom(monom,specialization):
    specialized_laurent = []
    for spec in product(*specialization):
        power = 0
        coefficient = 1
        for i,factor in enumerate(spec):
            n = factor[1]*monom[i+1]
            power +=  n
            if n!=0:
                coefficient *= factor[0]
        coefficient *= monom[0]
        specialized_laurent.append([coefficient,power])
    return specialized_laurent

def multivariable_to_laurent(polynom, specialization):
    """
    polynom is a list of monomials
    each monomial is a list with the first entry being the coefficient,
    the next entries are the power of each variable. 
    E.g. a polynom in the variables x,y,z looks like:
    [[1,1,0,0],[-1,1,1,1],[1,1,2,0]] = x - xyz + xy^2 

    specialization is a list for each variable of the multivariable polynom
    a laurent polynom of the form [[coefficient,power],...]
    """
    laurent = []
    for monom in polynom:
        specialized = specialize_monom(monom,specialization)
        for term in specialized:
            laurent.append(term)
    return simplify_laurent_polynom(laurent)
