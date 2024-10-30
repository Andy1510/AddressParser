from AddressParser import AddressTree as tree
from AddressParser import AddressCleaner as cleaner
from timeit import default_timer as timer
from typing import Callable
import re
import os
module_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(module_dir, 'data')

class Parser:
    def __init__(self, municipal_json_path=f'{data_folder}/municipal_vn_clean.json', street_json_path=f'{data_folder}/street_data.json'):
        self.address_tree = tree.AddressTree(municipal_json_path, street_json_path)

    def parse_home_num(self, address:str):
        # parse home number
        home_num = None
        if re.search(r'CHUNG CU', address) is None: # ko xác định đc số nhà của tòa chung cư vs số nhà của từng căn hộ
            home_num_exclude_words = ['QUAN', 'HUYEN', 'AP', 'PHUONG', 'KHU PHO', 'KHU VUC', 'QUOC LO', 'DUONG', 'TINH LO', 'TO', 'LIEN KHU', 'HEM']
            home_num_exclusion_pattern = ''.join([f"(?<!{word}\\s)(?<!{word}\\sSO\\s)" for word in home_num_exclude_words])
            home_num_pattern = f'^{home_num_exclusion_pattern}((SO|SO NHA)\s)?[\w\/\-]*\d+[\w\/\-]*'
            home_num = re.search(home_num_pattern, address)
            if home_num:
                address = re.sub(home_num.group(0), '', address, count=1)
                home_num = re.search(r'[\w\/\-]*\d+[\w\/\-]*', home_num.group(0)).group(0)
        else:
            address = re.sub(r'((\w+[\/\-])*(\w*\d+\w*[\/\-])+(\w+)*)', r'\1', address)

        return home_num, address


    def parse_country(self, address:str):
        vn = re.search(r'(VIET\s*NAM)', address)
        if vn: 
            address = re.sub(vn.group(0), '', address, count=1)
            return vn.group(0), address
        else:
            return '', address

    def gen_possible_matches(self, address:str, match_func:Callable, **kwargs):
        possible_matches = [{''}, {''}, {''}, {''}]
        various_sized_chunks = cleaner.split_to_chunks(address)
        for chunk in various_sized_chunks:
            possible_matches_per_level = match_func(chunk[0], **kwargs)
            for idx, matches in enumerate(possible_matches_per_level):
                if matches is not None:
                    if isinstance(matches, list):
                        for match in matches: possible_matches[idx].add((match, chunk[1]))
                    else: possible_matches[idx].add((matches, chunk[1]))
        return possible_matches


    def cut_multiple_ranges(self, val:str, ranges):
        words = val.split()
        ranges = sorted(ranges, reverse=True)
        for start, end in ranges:
            del words[start:end+1]
        return ' '.join(words)


    def get_most_probable_match(self, address:str, match_func:Callable, **kwargs):
        best_span = -1
        most_probable_address = []
        most_probable_order = []
        possible_matches = self.gen_possible_matches(address, match_func, **kwargs)
        for lvl1 in possible_matches[0]:
            for lvl2 in possible_matches[1]:
                for lvl3 in possible_matches[2]:
                    for street in possible_matches[3]:
                        possible_address = [x[0] if isinstance(x, tuple) else '' for x in (lvl1, lvl2, lvl3, street)]
                        order = [x[1] for x in (lvl1, lvl2, lvl3, street) if x != '']
                        span = sum([x[1] - x[0] + 1 for x in order])
                        if self.address_tree.is_sequence_valid(possible_address, order) and span > best_span: 
                            most_probable_address = possible_address
                            most_probable_order = order
                            best_span = span
        return most_probable_address, most_probable_order

    def parse_address(self, address:str, **kwargs):
        start = timer()
        cleaned_address = cleaner.clean_acronym(address)
        home_num, cleaned_address = self.parse_home_num(cleaned_address)
        country, cleaned_address = self.parse_country(cleaned_address)

        match_address, match_order = self.get_most_probable_match(cleaned_address, self.address_tree.strict_match)
        remaining_string = self.cut_multiple_ranges(cleaned_address, match_order)
        end = timer()

        if remaining_string != '':
            print(address)
            match_address, match_order = self.get_most_probable_match(cleaned_address, self.address_tree.fuzzy_match, **kwargs)
            remaining_string = self.cut_multiple_ranges(cleaned_address, match_order)
            end = timer()

        try:
            result = {
                'Country': country,
                'Municipal Level 1': match_address[0],
                'Municipal Level 2': match_address[1],
                'Municipal Level 3': match_address[2],
                'Street': match_address[3],
                'House Number': home_num,
                'Unparsed': remaining_string
            }
        except IndexError:
            print(address)
            result = {
                'Country': country,
                'Municipal Level 1': None,
                'Municipal Level 2': None,
                'Municipal Level 3': None,
                'Street': None,
                'House Number': home_num,
                'Unparsed': remaining_string
            }

        return result #, end - start


