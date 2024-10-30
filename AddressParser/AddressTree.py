import json
from rapidfuzz import process, fuzz, utils

class MunicipalNode:
    def __init__(self, name, full_name, parent=None):
        self.name = name
        self.full_name = full_name
        self.parent = parent
        self.children = {}  


    def add_child(self, child_node):
        self.children[child_node.full_name] = child_node
        self.children[child_node.name] = child_node
    

    def check_parent(self, key:str):
        if self.parent is not None: 
            return key in (self.parent.name, self.parent.full_name)
        return False
    

    def check_grandparent(self, key:str):
        if self.parent is not None:
            return self.parent.check_parent(key)
        return False
        

    def check_child(self, key:str):
        return self.children.get(key) is not None



class AddressTree:
    def __init__(self, municipal_json_path, street_json_path, root_name="VIET NAM", root_full_name="VIET NAM"):
        self.root = MunicipalNode(root_name, root_full_name)
        self.municipal_dict = [{}, {}, {}]
        self.municipal_collisions = [{}, {}, {}]

        self.value_by_len_dict = [{}, {}, {}, {}]

        self.street_dict = self.load_street_data(street_json_path)
        with open(municipal_json_path, 'r') as f:
            json_data = json.load(f)
        self.load_municipal(json_data)


    def load_municipal(self, json_data):
        """Build the tree from a JSON structure and collect nodes by level."""
        def gen_unique_key(key, level_dict, collision_dict) -> str:
            if key in collision_dict:
                collision_dict[key] += 1
            else:
                collision_dict[key] = 1  
            
            # Ensure the key is unique by adding '+' if needed
            while key in level_dict:
                key += '+'
            return key

        def build_node(data, level:int, parent_node=None) -> MunicipalNode:
            current_node = MunicipalNode(data['Name'], data['FullName'], parent_node)
            full_name_key = gen_unique_key(data['FullName'], self.municipal_dict[level-1], self.municipal_collisions[level-1])
            name_key = gen_unique_key(data['Name'], self.municipal_dict[level-1], self.municipal_collisions[level-1])
            self.municipal_dict[level-1][full_name_key] = current_node
            self.municipal_dict[level-1][name_key] = current_node

            if len(data['Name']) in self.value_by_len_dict[level-1]:
                self.value_by_len_dict[level-1][len(data['Name'])].add(data['Name'])
            else:
                self.value_by_len_dict[level-1][len(data['Name'])] = {data['Name']}

            if len(data['FullName']) in self.value_by_len_dict[level-1]:
                self.value_by_len_dict[level-1][len(data['FullName'])].add(data['FullName'])
            else:
                self.value_by_len_dict[level-1][len(data['FullName'])] = {data['FullName']}

            if parent_node:
                parent_node.add_child(current_node)

            children = []
            children_with_offspring = [key for key in data.keys() if isinstance(data[key], list)]
            if children_with_offspring:
                children = data[children_with_offspring[0]]

            if children and level < 3:
                for child in children:
                    build_node(child, level+1, current_node)

            return current_node

        for element in json_data:
            build_node(element, 1, self.root)


    def load_street_data(self, street_json_path):
        complete_address_json_file = street_json_path
        with open(complete_address_json_file, 'r', encoding='utf-8') as file:
            street_data = json.load(file)

        all_streets = []
        for city in street_data:
            all_streets.extend(street_data[city])
        street_data["ALL"] = all_streets

        def to_sets(o):
            if isinstance(o, list):
                return {to_sets(v) for v in o}
            elif isinstance(o, dict):
                return {k: to_sets(v) for k, v in o.items()}
            return o
        
        street_data = to_sets(street_data)

        for value in street_data['ALL']:
            if len(value) in self.value_by_len_dict[3]:
                self.value_by_len_dict[3][len(value)].add(value)
            else:
                self.value_by_len_dict[3][len(value)] = {value}

        return street_data


    def check_node(self, key:str) -> bool:
        lvl_1_result = self.municipal_dict[0].__contains__(key) 
        lvl_2_result = self.municipal_dict[1].__contains__(key) 
        lvl_3_result = self.municipal_dict[2].__contains__(key) 
        return lvl_1_result or lvl_2_result or lvl_3_result


    def get_nodes(self, key:str, level:int) -> list:
        """Returns all nodes at a certain level that share the same key"""
        level_dict = self.municipal_dict[level-1]
        collision_dict = self.municipal_collisions[level-1]

        collision_count = collision_dict.get(key, 0)
        nodes = []
        for i in range(collision_count):
            adjusted_key = key + '+' * i
            if adjusted_key in level_dict:
                nodes.append(level_dict[adjusted_key])
        return nodes
    

    def get_nodes_full_name(self, key:str, level:int) -> list:
        """Returns all nodes at a certain level that share the same key"""
        level_dict = self.municipal_dict[level-1]
        collision_dict = self.municipal_collisions[level-1]

        collision_count = collision_dict.get(key, 0)
        nodes = []
        for i in range(collision_count):
            adjusted_key = key + '+' * i
            if adjusted_key in level_dict:
                nodes.append(level_dict[adjusted_key].full_name)
        return nodes
    

    def check_street(self, val:str, node:MunicipalNode, level:int) -> bool:
        lvl_1_node = None
        if level == 3:
            lvl_1_node = node.parent.parent
        elif level == 2:
            lvl_1_node = node.parent
        elif level == 1:
            lvl_1_node = node
        else:
            return False
        
        if val == '':
            return True
        elif val != '' and val in self.street_dict[lvl_1_node.name]:
            return True
        else: 
            return False
    

    def valid_check_no_missing_municipal(self, sequence: tuple[str]) -> bool:
        lvl_2_nodes = self.get_nodes(sequence[1], 2)
        for node in lvl_2_nodes:
            if node.check_parent(sequence[0]) and node.check_child(sequence[2]):
                return self.check_street(sequence[3], node, 2)
        return False


    def valid_check_one_missing_municipal(self, sequence: tuple[str], missing_idx:int) -> bool:
        if missing_idx == 0:
            lvl_2_nodes = self.get_nodes(sequence[1], 2)
            for node in lvl_2_nodes:
                if node.check_child(sequence[2]): 
                    return self.check_street(sequence[3], node, 2)
        elif missing_idx == 1:
            lvl_3_nodes = self.get_nodes(sequence[2], 3)
            for node in lvl_3_nodes:
                if node.check_grandparent(sequence[0]): 
                    return self.check_street(sequence[3], node, 3)
        elif missing_idx == 2:
            lvl_2_nodes = self.get_nodes(sequence[1], 2)
            for node in lvl_2_nodes:
                if node.check_parent(sequence[0]): 
                    return self.check_street(sequence[3], node, 2)
        return False
    

    def valid_check_two_missing_municipal(self, sequence: tuple[str]) -> bool:
        for i in range(3):
            if sequence[i] != '':
                nodes = self.get_nodes(sequence[i], i+1)
                for node in nodes:
                    if self.check_street(sequence[3], node, i+1): return True
            # else:
            #     return self.check_node(sequence[i])
        return False


    def valid_check_three_missing_municipal(self, sequence: tuple[str]) -> bool:
        return sequence[3] in self.street_dict['ALL']


    def is_sequence_valid(self, sequence: tuple[str], order:list[tuple]) -> bool:
        order = sorted(order, key=lambda x: x[0])
        for i in range(1, len(order)):
            if order[i-1][1] >= order[i][0]: return False

        missing_count = 0
        missing_idx = -1
        for idx, dict in enumerate(self.municipal_dict):
            if sequence[idx] == '': 
                missing_count += 1
                missing_idx = idx
            if dict.get(sequence[idx]) is None and sequence[idx] != '': return False

        if missing_count == 0:
            return self.valid_check_no_missing_municipal(sequence)
        elif missing_count == 1:
            return self.valid_check_one_missing_municipal(sequence, missing_idx)
        elif missing_count == 2:
            return self.valid_check_two_missing_municipal(sequence)
        elif missing_count == 3:
            return self.valid_check_three_missing_municipal(sequence)

        return False


    def fuzzy_match(self, val:str, threshold=95, len_range=0) -> list[list]:
        matches = [None, None, None, None]
        for i in range(3):
            municipal_candidates = [item for key, value in self.value_by_len_dict[i].items() if key - len_range <= key <= key + len_range for item in value]
            result = process.extractOne(val, 
                                        municipal_candidates, 
                                        scorer=fuzz.ratio, 
                                        score_cutoff=threshold,
                                        processor=utils.default_process)
            if result is not None: matches[i] = [x.full_name for x in self.get_nodes(result[0], i+1)]
        street_candidates = [item for key, value in self.value_by_len_dict[3].items() if key - len_range <= key <= key + len_range for item in value]
        street_result = process.extract(val, 
                                        street_candidates, 
                                        scorer=fuzz.ratio, 
                                        score_cutoff=threshold,
                                        processor=utils.default_process)
        if len(street_result) != 0: 
            matches[3] = []
            for match in street_result:
                matches[3].append(match[0])
        return matches
    

    def strict_match(self, val:str) -> list[list]:
        matches = [None, None, None, None]
        for i in range(3):
            result = self.get_nodes_full_name(val, i+1)
            if len(result) != 0: matches[i] = result
        if val in self.street_dict['ALL']: matches[3] = val 
        return matches