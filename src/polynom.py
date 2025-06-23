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
    """
    input monom is a list:
    [coefficient,var_a_power,var_b_power, ...]
    specialization is list of length number of variables of the monom (i.e. len(monom)-1)
    containing laurent polynoms
    """
    specialized_laurent = LaurentPolynom([[monom[0],0]])
    for i in range(len(specialization)):
        specialized_laurent = specialized_laurent*(specialization[i]**monom[i+1])
    return specialized_laurent

class Polynom:
    def __init__(self,polynom):
        self.polynom = polynom

    def __repr__(self):
        return "Polynom: " + str(self.polynom)

    def to_latex(self):
        pass
    
    def __add__(self, other):
        pass

    def __eq__(self, value):
        pass

class MultivariatePolynom(Polynom):
    def __init__(self,polynom):
        """
        Multivarate Polynom input is expected to be like:
        [[coefficient, var_a_power, var_b_power,...]]
        """
        self.polynom = polynom

    def to_latex(self):
        """
        Turn multivariate Polynom to LaTeX format.
        """
        polynomial = self.polynom
        polynomial_latex = "1"
        for summand in polynomial:
            term_latex_string = ""
            if any([entry!=0 for entry in summand[1:]]):
                for i, count in enumerate(summand[1:]):
                    if count > 1:
                        term_latex_string += f"y_{{{i+1}}}^{count}"
                    elif count == 1:
                        term_latex_string += f"y_{{{i+1}}}"
                polynomial_latex += " + " + term_latex_string
        return polynomial_latex

    def specialize_to_laurent(self,specialization, spec="mono"):
        """
        polynom is a list of monomials
        each monomial is a list with the first entry being the coefficient,
        the next entries are the power of each variable. 
        E.g. a polynom in the variables x,y,z looks like:
        [[1,1,0,0],[-1,1,1,1],[1,1,2,0]] = x - xyz + xy^2 

        specialization is a LaurentPolynom object for each variable of the multivariable polynom
        i.e.: [LaurentPolynom([[...]]),...]
        """
        laurent = LaurentPolynom([[0,0]])
        for monom in self.polynom:
            specialized_mon = specialize_monom(monom,specialization)
            laurent = laurent + specialized_mon
        laurent.simplify()
        return laurent

def multiply_laurent_monom(term):
    """
    expected input term = [[coefficient_a,power_a], [coefficient_b,power_b]]
    returns [coefficient_a*coefficient_b,power_a+power_b]"""
    result = [term[0][0]*term[1][0],term[0][1]+term[1][1]]
    return result

class LaurentPolynom(Polynom):
    def __init__(self,polynom):
        """
        polynom is a list in the following format: [[coefficient,power],...]
        """
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
                    polynom_latex += f" {sign} {coefficient}t^{{{int(term[1])}}}"
        polynom_latex = polynom_latex.strip()
        if polynom_latex.startswith("+"):
            polynom_latex = polynom_latex[1:].strip()
        return polynom_latex

    def simplify(self):
        simplified_polynom = []
        for summand in self.polynom:
            if any(term[1] == summand[1] for term in simplified_polynom):
                for term in simplified_polynom:
                    if term[1] == summand[1]:
                        term[0] += summand[0]
            else:
                simplified_polynom.append(summand)
        for term in simplified_polynom:
            if term[0]==0:
                simplified_polynom.remove(term)
        self.polynom = simplified_polynom

    def get_specialization(self,specialization):
        """
        Input specialization as LaurentPolynom object
        e.g: LaurentPolynom([[1,1],[-1,2]])

        returns specialized laurent polynom
        """
        specialization = [specialization]
        result = LaurentPolynom([[0,0]])
        for monom in self.polynom:
            result = result + specialize_monom(monom,specialization)
        return result
            


    def __add__(self,other):
        polynom = self.polynom.copy()
        for term in other.polynom:
            polynom.append(term)
        sum = LaurentPolynom(polynom)
        sum.simplify()
        return sum

    def __mul__(self,other):
        if not isinstance(other,LaurentPolynom):
            raise NotImplementedError("Only multiply laurent with other laurent polynoms")
        self.simplify()
        other.simplify()
        polynom_a = self.polynom
        polynom_b = other.polynom
        result = []
        for term in product(polynom_a,polynom_b):
            summand = multiply_laurent_monom(term)
            result.append(summand)
        return LaurentPolynom(result)

    def __pow__(self,power):
        self.simplify()
        if power<0:
            if len(self.polynom)>1:
                raise ValueError("Laurent polynom inverse does not exist")
            else:
                monom = self.polynom[0].copy()
                monom[1]=monom[1]*power
                return LaurentPolynom([monom])
        elif power==0:
            return LaurentPolynom([[1,0]])
        else:
            result = LaurentPolynom([[1,0]])
            for i in range(power):
                result = self*result
            return result
                
        
        

if __name__=="__main__":
    polynom = [[-1,2],[-1,-2],[1,3]]
    polynom_b = [[0,0]]
    laurent = LaurentPolynom(polynom)
    laurent_b  =LaurentPolynom(polynom_b)
    new = laurent+laurent_b
    print(new)
