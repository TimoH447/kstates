from src.quiver import QuiverPlotter

from itertools import product

def get_identity_matrix(n):
    if n==1:
        return [[1]]
    elif n==0:
        return 0
    identity = []
    for i in range(n):
        row = [0]*n
        row[i]=1
        identity.append(row)
    return identity

def get_matrix(m,n):
    matrix = []
    x = 1 if n>m else 0
    for i in range(n):
        col = [0]*m
        matrix.append(col)
    for j in range(m):
        if x==1:
            matrix[j+1][j] = 1
        else:
            if j<n:
                matrix[j][j]=1
    return matrix

def get_jordan_matrix(n):
    if n==1:
        return 0
    elif n==0:
        return 0
    jordan = []
    jordan.append([0]*n)
    for i in range(n-1):
        row = [0]*n
        row[i]=1
        jordan.append(row)
    return jordan


def exactly_equal_paths(path,other):
    if len(path)!=len(other):
        return False 
    for i,arrow in enumerate(path):
        if arrow!=other[i]:
            return False
    return True

def is_path_in_list(path,path_list):
    """
    path=[(a,b),(b,c),...]
    path_list = [path, path_b,...]
    """
    for other in path_list:
        if exactly_equal_paths(path,other):
            return True

def is_subpath(path, long_path):
    if path == 0:
        return False

    if len(path)>=len(long_path):
        return False
    for start_i in range(len(long_path)-len(path)+1):
        if path==long_path[start_i:start_i+len(path)]:
            return True
    return False
        
def contains_zero_relation(path, zero_relations):
    for zero_relation in zero_relations:
        if zero_relation.can_be_applied(path):
            return True
    return False

def apply_relation(path, relations, previously_applied):
    new_paths = []
    for relation in relations:
        new_equiv = relation.get_possible_equivalent_paths(path,previously_applied)
        if new_equiv==0:
            return 0
        else:
            new_paths = new_paths + new_equiv
    return new_paths

class Relation:
    def __init__(self, path_a,path_b):
        """
        if relation is a cero relation then 
        input path_b=0
        """
        self.path_a = path_a
        self.path_b = path_b

    def __repr__(self):
        return f"{self.path_b}-{self.path_a}"

    def reverse_arrows(self):
        self.path_a = [(arrow[1],arrow[0]) for arrow in self.path_a]
        self.path_a.reverse()
        if self.path_b!=0:
            self.path_b = [(arrow[1],arrow[0]) for arrow in self.path_b]
            self.path_b.reverse()

    def is_arrow_relation(self):
        pass

    def _get_path_qpa(self,path,quiver):
        qpa_string = ""
        for i,arrow in enumerate(path):
            if i==0:
                qpa_string += quiver.get_arrow_label(arrow)
            else:
                qpa_string += f"*{quiver.get_arrow_label(arrow)}"
        return qpa_string
    
    def get_qpa(self,quiver):
        if self.path_b==0:
            return self._get_path_qpa(self.path_a,quiver)
        else:
            return f"{self._get_path_qpa(self.path_b,quiver)}-{self._get_path_qpa(self.path_a,quiver)}"
    
    def can_be_applied(self,path):
        if is_subpath(self.path_a,path) and self.path_a!=0:
            return True
        elif is_subpath(self.path_b,path) and self.path_b!=0:
            return True
        return False

    def  get_possible_equivalent_paths(self,path,previously_applied):
        """
        returns list:
        [[new_path, (self,position_where_relation_was_applied)],[...],....]
        """
        new_paths = []
        # seperate handling for 0 relations
        if self.path_b == 0:
            if is_subpath(self.path_a,path):
                new_path = 0
                return 0
            else:
                return []
        # handling for non 0 relations
        for i in range(len(path)):
            if (self,i)==previously_applied:
                continue
            if path[i:i+len(self.path_b)]==self.path_b:
                new_path = path[0:i]+self.path_a + path[i+len(self.path_b):]
                new_paths.append([new_path, (self,i)])
            if path[i:i+len(self.path_a)]==self.path_a:
                new_path = path[0:i]+self.path_b + path[i+len(self.path_a):]
                new_paths.append([new_path, (self,i)])
        return new_paths


class Path:
    def __init__(self,path):
        """
        path = [(a,b),(b,c),...] 
        """
        if isinstance(path,int):
            self.path = []
            self.trivial = path
        else:
            self.path = path
            self.trivial = 0
        self.equivalent_paths = [self.path]
        self.is_zero = False

    def __repr__(self):
        if self.is_trivial():
            return f"Path e_{self.start()}"
        path = ""
        for arrow in self.path:
            path = path + f"{arrow[0]},"
        path = path + str(self.path[-1][1])
        return f"Path: {path}"

    def set_equivalent_paths(self,algebra,max_number_of_paths = 1000):
        """
        path = [(a,b),(b,c),...]
        relations = [Relation(...),...]
        returns a list of equivalent paths: [[(a,b),(b,c),...],[...],...]
        """
        path = self.path
        equivalent_paths = [path]
        queue = [(path,None)]
        while queue:
            if len(equivalent_paths)>=max_number_of_paths:
                algebra.possibly_paths_with_infinite_equivalents.append(self)
                break
            current_path, prev_relation = queue.pop(0)
            if contains_zero_relation(current_path, algebra.zero_relations):
                # do handle zero path
                algebra.zero_relations.append(Relation(self.path,0))
                self.is_zero = True
                break
            elif is_subpath(self.path, current_path):
                # infinitely looping handle
                self.is_zero = True
                algebra.zero_relations.append(Relation(self.path,0))
                break
            new_possible_paths = apply_relation( current_path, algebra.relations,prev_relation)
            for new_path,applied_relation in new_possible_paths:
                if not new_path in equivalent_paths:
                    equivalent_paths.append(new_path)
                    queue.append( (new_path, applied_relation) )
        self.equivalent_paths = equivalent_paths

    def is_trivial(self):
        return bool(self.trivial)

    def start(self):
        if self.is_trivial():
            return self.trivial
        return self.path[0][0]

    def is_cero(self):
        """
        set equivalent paths first
        """
        return self.is_zero

    def target(self):
        if self.is_trivial():
            return self.trivial
        return self.path[-1][1]

    def __eq__(self, value):
        if not isinstance(value,Path):
            return False 
        if is_path_in_list(self.path,value.equivalent_paths):
            return True
        if is_path_in_list(value.path, self.equivalent_paths):
            return True
        return False

    def __mul__(self,value):
        if not isinstance(value,Path):
            return NotImplementedError("You can only concatenate two paths.")
        else:
            return Path(self.path + value.path)

class BasisBuilder:
    def __init__(self,algebra):
        self.algebra = algebra
        self.warning = None
    
    def get_projective_basis(self, vertex, max_dim_at_vertex, max_path_extending):
        """
        Computes a basis for the projective module at a given vertex. Enumerating all unique paths starting 
        at that vertex.
        
            Parameters:
                vertex (int): The starting vertex.
                max_dim_at_vertex (int): Maximum number of basis elements before stopping.
                max_path_extending (int): Maximum number of equivalents paths for each path.

            Returns:
                List of Path objects forming the basis.
        """
        basis = [Path(vertex)]
        queue = [Path(vertex)]
        connections = []
        limit = max_dim_at_vertex
        while queue and limit>0:
            limit-=1
            path = queue.pop(0)
            for next_path in self._expand_path(path):
                if not self._is_cero_path(next_path,max_path_extending):
                    connections.append([path,next_path])
                    if not next_path in basis:
                        queue.append(next_path)
                        basis.append(next_path)
        if limit==0:
            self.algebra.vertices_with_incomplete_basis.append(vertex)
            self.warning = f"Overflow of paths starting at vertex {vertex} (more than {max_dim_at_vertex}), the algebra might be infinte dimensional"
            print(self.warning)
        self.algebra.projectives[vertex] = ProjectiveRep(self.algebra.quiver, basis, connections,vertex)
        return ProjectiveRep(self.algebra.quiver, basis, connections,vertex)

    def _is_cero_path(self,new_path,max_path_extending):
        new_path.set_equivalent_paths(self.algebra, max_path_extending)
        return new_path.is_cero()
        
    def _add_zero_relation(self,new_path):
        if new_path.is_infinite() and not new_path.contains_cero():
            self.algebra.zero_relations.append(Relation(new_path.path,0))

    def _expand_path(self, path):
        """
        Returns all possible single-arrow extensions of a path.
        """
        end_vertex = path.target()
        outgoing_arrows = self.algebra.quiver.get_outgoing_arrows(end_vertex)
        return [path * Path([arrow]) for arrow in outgoing_arrows]

    def get_path_basis(self, max_dim_at_vertex=1000, max_path_extending=4000):
        basis = []
        for vertex in self.algebra.quiver.vertices:
            projective = self.get_projective_basis(vertex, max_dim_at_vertex, max_path_extending)
            basis = basis + projective.basis
        basis = [el for el in basis if not el.is_cero()]
        return basis
    
class Quiver:
    def __init__(self,vertices,arrows):
        self.vertices = vertices
        self.arrows = arrows
    
    @classmethod
    def from_pd(cls, pd_notation):
        vertices = []
        arrows = []
        for crossing in pd_notation:
            for i,segment in enumerate(crossing):
                if segment not in vertices:
                    vertices.append(segment)
                arrows.append((segment,crossing[(i+3)%4]))
        return cls(vertices,arrows)

    def __repr__(self):
        return f"Q: Vertices: {self.vertices}, Arrows: {self.arrows}"

    def get_outgoing_arrows(self,vertex):
        outgoing= []
        for arrow in self.arrows:
            if arrow[0]==vertex:
                outgoing.append(arrow)
        if len(outgoing)!=2:
            raise ValueError(f"There should be exactly 2 outgoing arrows but {len(outgoing)} were found in vertex {vertex}")
        return outgoing

    def get_quiver_notation_qpa(self):
        number_of_vertices = str(len(self.vertices))
        arrows = str([list(arrow) for arrow in self.arrows])
        return f"Quiver( {number_of_vertices}, {arrows})"

    def get_arrow_label(self, arrow):
        i = self.arrows.index(arrow)
        return f"a{i+1}"

class RepMap:
    """
    arrow is a tuple (source_vertex, target_vertex)
    matrix is given as list containing the columns as list of integers
    """
    def __init__(self,arrow,matrix):
        self.arrow = arrow
        self.matrix = matrix

    def __repr__(self):
        return f"Arrow: {self.arrow}, Matrix: {self.matrix}."

class Representation:
    def __init__(self, quiver, dimension_vector, maps):
        self.quiver = quiver
        self.dimension_vector = dimension_vector
        self.maps = maps

    def get_dimension_vector(self):
        return self.dimension_vector

    def print(self, quiver_plotter):
        quiver_plotter.print_quiver(self.get_dimension_vector())

    def get_map_list_string(self):
        map_list = ""
        for map in self.maps:
            if map.matrix==[] or map.matrix == 0:
                continue
            map_list += str(map)
            map_list += "\n"
        return map_list

    def draw_module(self, quiver_plotter):
        quiver_plotter.draw_module(self)

class ProjectiveRep(Representation):
    def __init__(self, quiver, basis, connections, vertex):
        self.vertex = vertex
        self.quiver = quiver
        self.basis = basis
        self.connections = connections
        super().__init__(quiver, self.get_dimension_vector(), self.get_maps())

    def __repr__(self):
        return f"P({self.vertex})"

    def get_dimension_vector(self):
        dimension_vector = [0]*len(self.quiver.vertices)
        for path in self.basis:
            target = path.target()
            dimension_vector[target-1] += 1
        return dimension_vector

    def _get_map(self, arrow, vs_basis):
        arrow = tuple(arrow)
        source, target = arrow
        source_basis = vs_basis[source-1]
        target_basis = vs_basis[target-1]
        matrix = []
        if len(source_basis)==0 or len(target_basis)==0:
            return RepMap(arrow,matrix)
        for b_i in source_basis:
            c_j = [0]*len(target_basis)
            for connection in self.connections:
                if b_i == connection[0] and connection[1].target()==target:
                    target_i = target_basis.index(connection[1])
                    c_j[target_i]=1
                    break
            matrix.append(c_j)
        return RepMap(arrow,matrix)

    def get_maps(self):
        maps = []
        vs_basis = [[] for i in range(len(self.quiver.vertices))]
        for path in self.basis:
            target= path.target()
            vs_basis[target-1].append(path)
        for arrow in self.quiver.arrows:
            map = self._get_map(arrow,vs_basis)
            maps.append(map)
        return maps

class StateModule(Representation):
    def __init__(self,sequence,diagram):
        self.sequence = sequence
        self.diagram = diagram
        self.quiver = diagram.get_quiver()
        super().__init__(self.quiver,self.get_dimension_vector(),self.get_maps())

    def get_dimension_vector(self):
        dim_vec = [0]*len(self.quiver.vertices)
        for vertex in self.sequence:
            dim_vec[vertex-1]+=1
        return dim_vec

    def get_map(self,arrow):
        dim_vec = self.get_dimension_vector()
        source, target = arrow
        ds =dim_vec[source-1]
        dt = dim_vec[target-1]
        if ds==0 or dt==0:
            return 0
        elif ds-dt!=0:
            return get_matrix(dt,ds)
        elif ds==dt:
            crossing = self.diagram.get_crossing_from_arrow(arrow)
            if all([dim_vec[vertex-1]==ds for vertex in crossing.segments]):
                if all([self.sequence.index(source)<=self.sequence.index(vertex) for vertex in crossing.segments]):
                    return get_jordan_matrix(ds)
                
            return get_identity_matrix(ds) 

    def get_maps(self):
        maps=[]
        for arrow in self.quiver.arrows:
            matrix = self.get_map(arrow)
            maps.append(RepMap(arrow,matrix))
        return maps

    def get_module_maps_qpa(self):
        qpa_string = "["
        for arrow in self.quiver.arrows:
            map = self.get_map(arrow)
            if map!=0:
                qpa_string += f"[\"{self.quiver.get_arrow_label(arrow)}\", {map}],"
        if len(qpa_string)>1:
            qpa_string = qpa_string[:-1]
        qpa_string += "]"
        return qpa_string

    def get_module_qpa(self):
        qpa_string = f"M := RightModuleOverPathAlgebra(A, {self.get_dimension_vector()}, {self.get_module_maps_qpa()});"
        return qpa_string

class DirectSumModules:
    def __init__(self,modules):
        self.modules = modules

    def __repr__(self):
        return f"Direct sum: {self.modules}"

    def get_dimension_vector(self):
        if len(self.modules)==0:
            return []
        n = len(self.modules[0].get_dimension_vector())
        dim_vec = [0]*n
        for module in self.modules:
            for i,dim in enumerate(module.get_dimension_vector()):
                dim_vec[i]+=dim
        return dim_vec

class DirectSumProjectives(DirectSumModules):
    def __init__(self, modules, projectives):
        self.projectives = projectives # list with the number of times each projective indecomposable is in the sum
        super().__init__(modules)
    
    @classmethod
    def from_projective_list(cls,projectives,algebra):
        modules = []
        for i,mult in enumerate(projectives):
            for j in range(mult):
                modules.append(algebra.get_projective_module(i+1))
        return cls(modules,projectives)
    
    @classmethod
    def from_projective(cls,projective):
        n = len(projective.get_dimension_vector())
        list_of_projectives = [0]*n
        list_of_projectives[projective.vertex-1]=1
        return cls([projective],list_of_projectives)

    @classmethod
    def from_projectives(cls,projectives):
        list_of_projectives = [0]*len(projectives[0].get_dimension_vector())
        for projective in projectives:
            list_of_projectives[projective.vertex-1]+=1
        return cls(projectives,list_of_projectives)

    def add_projective(self,projective,algebra):
        projectives = self.projectives.copy()
        projectives[projective.vertex-1] += 1
        return DirectSumProjectives.from_projective_list(projectives,algebra)

    def __eq__(self, value):
        if not isinstance(value,DirectSumProjectives):
            return False
        for i in range(len(self.projectives)):
            if self.projectives[i]!=value.projectives[i]:
                return False
        return True



def get_reduced_vector(dim_vec_projective, dim_vec_cover):
    dim_vec_reduced = []
    for i in range(len(dim_vec_projective)):
        dim_vec_reduced.append(dim_vec_cover[i]-dim_vec_projective[i])
    return dim_vec_reduced

    
def is_cover(dim_vec_reduced,dim_vec_module):
    if not len(dim_vec_reduced)==len(dim_vec_module):
        raise ValueError(f"dimension vectos: {dim_vec_reduced} and {dim_vec_module} have to have the same length")
    for i in range(len(dim_vec_module)):
        if dim_vec_reduced[i] < dim_vec_module[i]:
            return False
    return True
    
def is_reduced_cover(cover,algebra,module):
    projectives = algebra.get_projectives()
    dim_vec_cover = cover.get_dimension_vector()
    dim_vec_module = module.get_dimension_vector()
    if not is_cover(dim_vec_cover,dim_vec_module):
        return False 
    for projective in cover.modules:
        dim_vec_reduced = get_reduced_vector(projective.get_dimension_vector(), dim_vec_cover)
        if is_cover(dim_vec_reduced,dim_vec_module):
            return False
    return True

def get_kernel(cover,module):
    dim_vec_cover = cover.get_dimension_vector()
    dim_vec_module = module.get_dimension_vector()
    kernel = []
    for i in range(len(dim_vec_cover)):
        kernel.append(dim_vec_cover[i]-dim_vec_module[i])
    return kernel

def get_sum_of_projectives(multiplicities,algebra):
    modules = []
    for i,multiplicity in enumerate(multiplicities):
        for j in range(multiplicity):
            modules.append(algebra.get_projective_module(i+1))
    return DirectSumModules(modules)
        
def has_equal_dim_vec(dim_vec_a, dim_vec_b):
    for i in range(len(dim_vec_a)):
        if dim_vec_a[i]!=dim_vec_b[i]:
            return False
    return True

def has_smaller_dim_vec(dim_vec_a,dim_vec_b):
    for i in range(len(dim_vec_a)):
        if dim_vec_a[i]>dim_vec_b[i]:
            return False
    return True
    
def is_projective(kernel,algebra):
    possibilities = product([0,1],repeat=len(kernel))
    for cover in possibilities:
        if any(cover):
            sum = get_sum_of_projectives(cover,algebra)
            dim_vec_sum = sum.get_dimension_vector()
            if has_equal_dim_vec(dim_vec_sum,kernel):
                return sum
    return False

def is_projective_v2(kernel, algebra):
    projectives = algebra.get_projectives()
    possible_projectives = [DirectSumProjectives.from_projective(projective) for projective in projectives]
    while len(possible_projectives)!=0:
        possible  = possible_projectives.pop(0)
        possible_dim_vec  = possible.get_dimension_vector()
        if has_equal_dim_vec(possible_dim_vec, kernel):
            return possible
        if has_smaller_dim_vec(possible_dim_vec,kernel):
            new_options = []
            for projective in projectives:
                next_option = possible.add_projective(projective,algebra)
                if next_option not in possible_projectives:
                    new_options.append(next_option)
            possible_projectives.extend(new_options)
    return False
        
        
def get_standard_cover(module,algebra):
    cover_module = []
    for i,proj in enumerate(module.get_dimension_vector()):
        if proj == 1:
            cover_module.append(algebra.get_projective_module(i+1))
    cover_module = DirectSumModules(cover_module)
    return cover_module

def get_custom_cover(module,algebra):
    return [
        DirectSumProjectives.from_projective_list([0,2,0,1,0,0,0,1,0,1,0,0,0,2,0,0,0,0],algebra),
        ]

def get_covers_by_length(module, algebra, length):
    covers = product(algebra.quiver.vertices, repeat=length)
    cover_list = []
    for cover in covers:
        modules = []
        for vertex in cover:
            modules.append(algebra.get_projective_module(vertex))
        cover_list.append(DirectSumProjectives.from_projectives(modules))
    return cover_list
        
    

        

def compute_projective_covers(algebra,module):
    n = len(module.get_dimension_vector())
    possible_covers = product([0,1], repeat=n)
    proj_covers = []
    for cover in possible_covers:
        if any(cover):
            cover_module  = []
            for i,proj in enumerate(cover):
                if proj == 1:
                    cover_module.append(algebra.get_projective_module(i+1))
            cover_module = DirectSumModules(cover_module)
            if is_reduced_cover(cover_module,algebra,module):
                proj_covers.append(cover_module)
    return proj_covers

def compute_projective_resolution(algebra,module):
    resoultions = []
    covers = compute_projective_covers(algebra,module)
    #covers = get_custom_cover(module,algebra)
    print(covers)
    for cover in covers:
        print(cover)
        kernel = get_kernel(cover,module)
        print(f"Kernel: {kernel}")
        if not any(kernel):
            resoultions.append([module,cover])
        proj = is_projective_v2(kernel,algebra)
        print(f"Is projective: {proj}")
        if proj:
            resoultions.append([module, cover, proj])
    if resoultions ==[]:
        raise ValueError("This module has no projective resolution of dimension 1.")
    return resoultions
            

class JacobianAlgebra:
    def __init__(self,  vertices, arrows, relations, max_unique = 200 ,max_extension = 1000):
        """
        vertices= [1,...,2n]
        arrows = [(a,b),(b,c),...]
        relations = [Relation(path_a,path_b),...]
        """
        self.quiver = Quiver(vertices,arrows)
        self.relations = relations
        self.zero_relations = []
        self.warning = False
        self.basis = None
        self.vertices_with_incomplete_basis = []
        self.projectives = {}
        self.possibly_paths_with_infinite_equivalents = []

        self.max_unique = max_unique
        self.max_extension = max_extension
    
    @classmethod
    def _from_diagram(cls,diagram, max_unique=200, max_extension=1000):
        pd_notation = diagram.get_pd_notation()
        vertices = []
        arrows = []
        relations = []
        for crossing_id,crossing in enumerate(pd_notation):
            for i,segment in enumerate(crossing):
                if segment not in vertices:
                    vertices.append(segment)
                arrows.append((segment,crossing[(i+3)%4]))
                region = diagram.get_region(crossing_id,i)
                region = list(region.bounding_segments)
                region.reverse()
                region_path = []
                for j,reg_segment in enumerate(region):
                    region_path.append((region[j-1],reg_segment))
                region_path.pop(-1)
                crossing_path = [(segment,crossing[(i-1)%4]),(crossing[(i-1)%4],crossing[(i-2)%4]),(crossing[(i-2)%4],crossing[(i-3)%4])]
                relations.append(Relation(region_path,crossing_path))
        return cls(vertices,arrows,relations, max_unique, max_extension)

    def reverse_arrows(self):
        reversed_arrows = [(arrow[1],arrow[0])   for arrow in self.quiver.arrows]
        self.quiver = Quiver(self.quiver.vertices,reversed_arrows)
        for relation in self.relations:
            relation.reverse_arrows()
        for relation in self.zero_relations:
            relation.reverse_arrows()
        self.basis = None
        self.warning = False
        self.projectives={}
        self.possibly_paths_with_infinite_equivalents = []
        self.vertices_with_incomplete_basis = []

    def remove_duplicate_arrows(self):
        """
        If the algebra contains a relation (arrow - path) then we remove this arrow from the quiver
        this does not change the algebra.
        """
        for relation in self.relations:
            if relation.is_arrow_relation():
                if len(relation.path_a)==1:
                    arrow = relation.path_a[0]
                else:
                    arrow = relation.path_b[0]
                #self.quiver.arrows.remove
                #update.relations

    def get_projective_module(self,vertex):
        max_unique, max_extension = self.max_unique, self.max_extension
        if not self.projectives.__contains__(vertex):
            projective = BasisBuilder(self).get_projective_basis(vertex,max_unique,max_extension)
        else:
            projective = self.projectives[vertex]
        return projective
    
    def get_projectives(self):
        projectives = []
        for vertex in self.quiver.vertices:
            if not self.projectives.__contains__(vertex):
                projectives.append(BasisBuilder(self).get_projective_basis(vertex,self.max_unique,self.max_extension))
            else:
                projectives.append( self.projectives[vertex])
        return projectives
            
        

    def get_dimension(self):
        if self.basis == None:
            self.basis = BasisBuilder(self).get_path_basis(self.max_unique, self.max_extension)
        if len(self.vertices_with_incomplete_basis)>0:
            return "unknown"
        if len(self.possibly_paths_with_infinite_equivalents)>0:
            return f"{len(self.basis)} (upper bound)"
        return len(self.basis)

    def __repr__(self):
        return f"Vertices: {self.quiver.vertices},\n Arrows: {self.quiver.arrows},\n Relations: {len(self.relations)}, \n Zero-Relations: {self.zero_relations}"

    def get_quiver_qpa(self):
        return f"Q:= {self.quiver.get_quiver_notation_qpa()}; "

    def get_generators_qpa(self):
        qpa_string = "gens := GeneratorsOfAlgebra(kQ); "
        for i in range(len(self.quiver.vertices)):
            qpa_string += f"v{i+1} := gens[{i+1}]; "
        x = len(self.quiver.vertices)
        for i,arrow in enumerate(self.quiver.arrows):
            qpa_string += f"{self.quiver.get_arrow_label(arrow)} := gens[{x+i+1}]; "
        return qpa_string

    def get_relations_qpa(self):
        qpa_string = "relations := ["
        for i,relation in enumerate(self.relations):
            if i==0:
                qpa_string += relation.get_qpa(self.quiver)
            else:
                qpa_string += f", {relation.get_qpa(self.quiver)}"
        for relation in self.zero_relations:
            qpa_string += f", {relation.get_qpa(self.quiver)}"
        qpa_string += "];"
        return qpa_string

    def get_qpa_input(self):
        """
        Generate input to work with this algebra in GAP QPA.
            
            Returns: 
                (String): qpa_string 
        """
        qpa_string = self.get_quiver_qpa()
        qpa_string += "kQ := PathAlgebra(Rationals, Q);"
        qpa_string += self.get_generators_qpa()
        qpa_string +=  self.get_relations_qpa()
        qpa_string += "I:=Ideal(kQ,relations); A:=kQ/I;"
        return qpa_string
        
        
        
        
        