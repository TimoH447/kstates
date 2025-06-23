from src.knotdiagram import KnotDiagram

class Path:
    def __init__(self,path):
        self.path = path

    def __eq__(self, value):
        if not isinstance(value,Path):
            return False
        if len(value.path)!=len(self.path):
            return False
        for i,arrow in enumerate(self.path):
            if arrow!=value.path[i]:
                return False
        return True

    def __add__(self,value):
        if not isinstance(value,Path):
            return NotImplemented
        else:
            return Path(self.path + self.value)
    
    

def apply_relation(path, relations, previously_applied):
    new_paths = []
    for relation in relations:
        for i,arrow in enumerate(path):
            if (relation,i)==previously_applied:
                print("previosly applied!")
                continue
            if path[i:i+len(relation.crossing_path)]==relation.crossing_path:
                new_path = path[0:i]+relation.region_path + path[i+len(relation.crossing_path):]
                new_paths.append([new_path, (relation,i)])
            if path[i:i+len(relation.region_path)]==relation.region_path:
                new_path = path[0:i]+relation.crossing_path + path[i+len(relation.region_path):]
                new_paths.append([new_path, (relation,i)])
    return new_paths

class Relation:
    def __init__(self, region_path,crossing_path):
        self.region_path = region_path
        self.crossing_path = crossing_path

    def __repr__(self):
        return f"{self.crossing_path}-{self.region_path}"

class JacobianAlgebra:
    def __init__(self, diagram, vertices, arrows, relations):
        self.diagram = diagram
        self.vertices = vertices
        self.arrows = arrows
        self.relations = relations

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
                    

        return cls(diagram,vertices,arrows,relations)

    def get_equivalent_paths(self,path,max_number_of_paths = 100):
        equivalent_paths = [path]
        queue = [(path,None)]
        end_i = 0
        while queue:
            end_i+=1
            if end_i>10000:
                print("to much")
                break

            path, previously_applied = queue.pop(0)
            new_paths = apply_relation(path,self.relations,previously_applied)
            
            for new_path in new_paths:
                if new_path[0] in equivalent_paths:
                    continue
                equivalent_paths.append(new_path[0])
                queue.append(new_path)
            if len(equivalent_paths)>max_number_of_paths:
                break
        return equivalent_paths


    def __repr__(self):
        return f"Vertices: {self.vertices},\n Arrows: {self.arrows},\n Relations: {self.relations}"
        
        