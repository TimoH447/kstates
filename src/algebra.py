from src.knotdiagram import KnotDiagram

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
        limit = max_dim_at_vertex
        while queue and limit>0:
            limit-=1
            path = queue.pop(0)
            for next_path in self._expand_path(path):
                if not next_path in basis and not self._is_cero_path(next_path,max_path_extending):
                    queue.append(next_path)
                    basis.append(next_path)
        if limit==0:
            self.algebra.vertices_with_incomplete_basis.append(vertex)
            self.warning = f"Overflow of paths starting at vertex {vertex} (more than {max_dim_at_vertex}), the algebra might be infinte dimensional"
            print(self.warning)
        self.algebra.projectives[vertex] = basis
        return basis

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
        outgoing_arrows = self.algebra.get_outgoing_arrows(end_vertex)
        return [path * Path([arrow]) for arrow in outgoing_arrows]

    def get_path_basis(self, max_dim_at_vertex=1000, max_path_extending=4000):
        basis = []
        for vertex in self.algebra.vertices:
            basis_at_vertex = self.get_projective_basis(vertex, max_dim_at_vertex, max_path_extending)
            basis = basis + basis_at_vertex
        basis = [el for el in basis if not el.is_cero()]
        return basis

class JacobianAlgebra:
    def __init__(self,  vertices, arrows, relations):
        """
        vertices= [1,...,2n]
        arrows = [(a,b),(b,c),...]
        relations = [Relation(path_a,path_b),...]
        """
        self.vertices = vertices
        self.arrows = arrows
        self.relations = relations
        self.zero_relations = []
        self.warning = False
        self.basis = None
        self.vertices_with_incomplete_basis = []
        self.projectives = {}
        self.possibly_paths_with_infinite_equivalents = []
    
    @classmethod
    def _from_pd_notation(cls,pd_notation):
        diagram = KnotDiagram(pd_notation)
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
        return cls(vertices,arrows,relations)

    def get_outgoing_arrows(self,vertex):
        outgoing= []
        for arrow in self.arrows:
            if arrow[0]==vertex:
                outgoing.append(arrow)
        if len(outgoing)!=2:
            raise ValueError(f"There should be exactly 2 outgoing arrows but {len(outgoing)} were found in vertex {vertex}")
        return outgoing

    def get_projective_module(self,vertex):
        if not self.projectives.__contains__(vertex):
            basis = BasisBuilder(self).get_projective_basis(vertex,100,100)
        else:
            basis = self.projectives[vertex]
        module = [0]*len(self.vertices)
        for path in basis:
            target = path.target()
            module[target-1] += 1
        return module

    def get_dimension(self):
        if self.basis == None:
            basis = BasisBuilder(self).get_path_basis()
        if len(self.vertices_with_incomplete_basis)>0:
            return "unknown"
        if len(self.possibly_paths_with_infinite_equivalents)>0:
            return f"{len(basis)} (upper bound)"
        return len(basis)

    def __repr__(self):
        return f"Vertices: {self.vertices},\n Arrows: {self.arrows},\n Relations: {len(self.relations)}, \n Zero-Relations: {self.zero_relations}"
        
        