from itertools import product
from operator import itemgetter

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

    def get_specialization(self,spec):
        """
        return the specialization input for method: specialize_to_laurent
        input list of list: [[],[],...]
        each list is a monom for a variable, ie number of multivariate variables"""
        result = []
        for monom in spec:
            result.append(LaurentPolynom([monom]))
        return result
            

    def specialize_to_laurent(self,specialization):
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

    def __eq__(self, value):
        self.simplify()
        value.simplify()
        if all([monom in value.polynom for monom in self.polynom]) and all([monom in self.polynom for monom in value.polynom]):
            return True
        return False

    def equal_up_to_factor(self,value):
        if not isinstance(value,LaurentPolynom):
            return False
        a = LaurentPolynom(self.polynom)
        b = LaurentPolynom(value.polynom)
        a.simplify()
        b.simplify()
        a.transform_into_polynom()
        b.transform_into_polynom()
        if a==b:
            return True
        return False

            

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
        if simplified_polynom == []:
            simplified_polynom = [[0,0]]
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

    def sort(self):
        self.polynom = sorted(self.polynom,key=itemgetter(1))

    def transform_into_polynom(self):
        lowest_power = self.polynom[0][1]
        for summand in self.polynom:
            if summand[1]<lowest_power:
                lowest_power = summand[1]
        if lowest_power==0:
            return
        x = LaurentPolynom([[1,-lowest_power]])
        transformed = x *self
        self.polynom = transformed.polynom

    def print_normalized_to_latex(self):
        laurent = LaurentPolynom(self.polynom)
        laurent.simplify()
        laurent.transform_into_polynom()
        print(laurent.to_latex())
        

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
