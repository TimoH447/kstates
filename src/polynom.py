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
    
class Polynom:
    def __init__(self,polynom):
        self.polynom = polynom

    def __repr__(self):
        return str(self.polynom)

    def to_latex(self):
        pass
    
    def __add__(self, other):
        pass

    def __eq__(self, value):
        pass

class MultivariatePolynom(Polynom):
    def __init__(self,polynom):
        self.polynom = polynom

    def to_latex(self):
        """
        Turn multivariate Polynom to LaTeX format.
        """
        polynomial = self.polynom
        polynomial_latex = "1"
        for summand in polynomial:
            term_latex_string = ""
            if summand[0]==0:
                for i, count in enumerate(summand):
                    if count > 1:
                        term_latex_string += f"y_{{{i}}}^{count}"
                    elif count == 1:
                        term_latex_string += f"y_{{{i}}}"
                polynomial_latex += " + " + term_latex_string
        return polynomial_latex

    def specialize_to_laurent(self,specialization):
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
        for monom in self.polynom:
            specialized = specialize_monom(monom,specialization)
            for term in specialized:
                laurent.append(term)
        return LaurentPolynom(simplify_laurent_polynom(laurent))
        


class LaurentPolynom(Polynom):
    def __init__(self,polynom):
        self.polynom = polynom

    def to_latex(self):
        """
        Turn laurent Polynom to latex
        """
        polynom_latex = ""
        for term in self.polynom:
            if term[0] == 0:
                continue
            sign = "+" if term[0] > 0 else "-"
            coefficient = abs(term[0])
            if term[1] == 0:
                polynom_latex += f" {sign} {coefficient}"
            else:
                if coefficient == 1:
                    coefficient = ""
                elif coefficient == -1:
                    coefficient = ""
                if term[1] == 1:
                    polynom_latex += f" {sign} {coefficient}t"
                else:
                    polynom_latex += f" {sign} {coefficient}t^{{{term[1]}}}"
        polynom_latex = polynom_latex.strip()
        if polynom_latex.startswith("+"):
            polynom_latex = polynom_latex[1:].strip()
        return polynom_latex

if __name__=="__main__":
    polynom = [[1,1],[-1,4],[0,3],[-1,-3]]
    laurent = LaurentPolynom(polynom)
    print(laurent.to_latex())
