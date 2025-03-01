
# Standard Library

# Pip3 Library
import yaml

# QTI Package Maker
# none allowed here!!

#==========================
#==========================
#==========================
# special loader with duplicate key checking
class UniqueKeyLoader(yaml.SafeLoader):
	def construct_mapping(self, node, deep=False):
		mapping = {}
		for key_node, value_node in node.value:
			key = self.construct_object(key_node, deep=deep)
			if isinstance(key, str):
				if mapping.get(key) is True:
					print("DUPLICATE KEY: ", key)
					raise AssertionError("DUPLICATE KEY: ", key)
				mapping[key] = True
			else:
				raise NotImplementedError
		return super().construct_mapping(node, deep)

#=======================
def readYamlFile(yaml_file):
	print("Processing file: ", yaml_file)
	yaml.allow_duplicate_keys = False
	yaml_file_pointer = open(yaml_file, 'r')
	#data = UniqueKeyLoader(yaml_pointer)
	#help(data)
	yaml_text = yaml_file_pointer.read()
	data = yaml.load(yaml_text, Loader=UniqueKeyLoader)
	#data = yaml.safe_load(yaml_pointer)
	yaml_file_pointer.close()
	return data

#=======================
base_replacement_rule_dict = {
	' not ': ' <strong>NOT</strong> ', #BOLD BLACK
	' Not ': ' <strong>NOT</strong> ', #BOLD BLACK
	' NOT ': ' <strong>NOT</strong> ', #BOLD BLACK
	' false ': ' <span style="color: #ba372a;"><strong>FALSE</strong></span> ', #BOLD RED
	' False ': ' <span style="color: #ba372a;"><strong>FALSE</strong></span> ', #BOLD RED
	' FALSE ': ' <span style="color: #ba372a;"><strong>FALSE</strong></span> ', #BOLD RED
	' true ': ' <span style="color: #169179;"><strong>TRUE</strong></span> ', #BOLD GREEN
	' True ': ' <span style="color: #169179;"><strong>TRUE</strong></span> ', #BOLD GREEN
	' TRUE ': ' <span style="color: #169179;"><strong>TRUE</strong></span> ', #BOLD GREEN
	'  ': ' ',
}

#=======================
def append_clear_font_space_to_text(string_text):
	return f'<span style="font-family: sans-serif; letter-spacing: 1px;">{string_text}</span>'

#=======================
def append_clear_font_space_to_list(list_of_text_strings):
	new_list_of_text_strings = []
	for string_text in list_of_text_strings:
		new_string_text = append_clear_font_space_to_text(string_text)
		new_list_of_text_strings.append(new_string_text)
	return new_list_of_text_strings

#=======================
def applyReplacementRulesToText(text_string, replacement_rule_dict):
	if not isinstance(text_string, str):
		raise TypeError(f"value is not string: {text_string}")
	if replacement_rule_dict is None:
		print("no replacement rules found")
		replacement_rule_dict = base_replacement_rule_dict
	else:
		#replacement_rule_dict = {**base_replacement_rule_dict, **replacement_rule_dict}
		replacement_rule_dict |= base_replacement_rule_dict
	for find_text, replace_text in replacement_rule_dict.items():
		if not replace_text.startswith('<strong>'):
			replace_text = f'<strong>{replace_text}</strong>'
		text_string = text_string.replace(find_text, replace_text)
	return text_string

#=======================
def applyReplacementRulesToList(list_of_text_strings, replacement_rule_dict):
	if replacement_rule_dict is None:
		print("no replacement rules found")
		replacement_rule_dict = base_replacement_rule_dict
	else:
		#replacement_rule_dict = {**base_replacement_rule_dict, **replacement_rule_dict}
		replacement_rule_dict |= base_replacement_rule_dict
	new_list_of_text_strings = []
	for text_string in list_of_text_strings:
		if not isinstance(text_string, str):
			raise TypeError(f"value is not string: {text_string}")
		for find_text, replace_text in replacement_rule_dict.items():
			if not replace_text.startswith('<strong>'):
				replace_text = f'<strong>{replace_text}</strong>'
			text_string = text_string.replace(find_text, replace_text)
		new_list_of_text_strings.append(text_string)
	return new_list_of_text_strings
