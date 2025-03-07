ENGINE_NAME = "canvas_qti_v1_2"

# Standard Library

# Pip3 Library
import lxml.etree

# QTI Package Maker
#from qti_package_maker.common import string_functions
from qti_package_maker.engines.canvas_qti_v1_2 import item_xml_helpers

#==============================================================
def MC(item_cls):
	#crc16_text: str, question_text: str, choices_list: list, answer_text: str):
	"""Create a Multiple Choice (Single Answer; Radio Buttons) question."""
	# Create the root <item> element with a unique identifier and title
	assessment_item_etree = lxml.etree.Element("item",
			ident=f"multiple_choice_{item_cls.item_number:03d}", title=item_cls.item_crc16)
	# Generate the <itemmetadata> section to store metadata about the question
	choice_ids_list = [f"choice_{i+1:03d}" for i in range(len(item_cls.choices_list))]
	itemmetadata = item_xml_helpers.create_itemmetadata(choice_ids_list, 'multiple_choice_question')
	# Create the <presentation> section to hold the question text and answer choices
	presentation_etree = lxml.etree.Element("presentation")
	# Generate the <material> section containing the question text
	material_mattext_etree = item_xml_helpers.create_material_mattext(item_cls.question_text)
	# Generate the <response_lid> section to store answer choices (radio buttons)
	response_lid_etree = item_xml_helpers.create_choice_response_lid(item_cls.choices_list, cardinality="Single")
	# Generate the <resprocessing> section to handle scoring and correctness logic
	resprocessing_etree = item_xml_helpers.create_MC_resprocessing(item_cls.choices_list, item_cls.answer_text)
	# Assemble the XML structure by appending elements in the correct order
	presentation_etree.append(material_mattext_etree)
	presentation_etree.append(response_lid_etree)
	assessment_item_etree.append(itemmetadata)
	assessment_item_etree.append(presentation_etree)
	assessment_item_etree.append(resprocessing_etree)
	# Return the fully assembled XML tree for the question
	return assessment_item_etree

#==============================================================
def MA(item_cls):
	#item_number: int, crc16_text: str, question_text: str, choices_list: list, answers_list: list):
	"""Create a Multiple Answer (Checkboxes) question."""
	# Create the root <item> element with a unique identifier and title
	assessment_item_etree = lxml.etree.Element("item",
		ident=f"multiple_answer_{item_cls.item_number:03d}", title=item_cls.item_crc16)
	# Generate the <itemmetadata> section to store metadata about the question
	choice_ids_list = [f"choice_{i+1:03d}" for i in range(len(item_cls.choices_list))]
	itemmetadata = item_xml_helpers.create_itemmetadata(choice_ids_list, 'multiple_answers_question')
	# Create the <presentation> section to hold the question text and answer choices
	presentation_etree = lxml.etree.Element("presentation")
	# Generate the <material> section containing the question text
	material_mattext_etree = item_xml_helpers.create_material_mattext(item_cls.question_text)
	# Generate the <response_lid> section to store answer choices (checkboxes)
	response_lid_etree = item_xml_helpers.create_choice_response_lid(item_cls.choices_list, cardinality="Multiple")
	# Generate the <resprocessing> section to handle scoring and correctness logic
	resprocessing_etree = item_xml_helpers.create_MA_resprocessing(item_cls.choices_list, item_cls.answers_list)
	# Assemble the XML structure by appending elements in the correct order
	presentation_etree.append(material_mattext_etree)
	presentation_etree.append(response_lid_etree)
	assessment_item_etree.append(itemmetadata)
	assessment_item_etree.append(presentation_etree)
	assessment_item_etree.append(resprocessing_etree)
	# Return the fully assembled XML tree for the question
	return assessment_item_etree

#==============================================================
def MATCH(item_cls):
	#item_number: int, crc16_text: str, question_text: str, prompts_list: list, choices_list: list):
	"""Create a Matching question where users match items from two lists."""
	# Create the root <item> element with a unique identifier and title
	assessment_item_etree = lxml.etree.Element("item",
		ident=f"matching_{item_cls.item_number:03d}", title=item_cls.item_crc16)
	# Generate the <itemmetadata> section for metadata
	choice_ids_list = [f"{i+1:03d}" for i in range(len(item_cls.choices_list))]
	itemmetadata = item_xml_helpers.create_itemmetadata(choice_ids_list, 'matching_question')
	# Create the <presentation> section for question text and matching choices
	presentation_etree = lxml.etree.Element("presentation")
	# Generate the <material> section containing the question text
	material_mattext_etree = item_xml_helpers.create_material_mattext(item_cls.question_text)
	# Generate <response_lid> sections for each answer item
	response_lids_etree = item_xml_helpers.create_matching_response_lid(item_cls.prompts_list, item_cls.choices_list)
	# Generate the <resprocessing> section for scoring
	resprocessing_etree = item_xml_helpers.create_MATCH_resprocessing(item_cls.prompts_list)
	# Assemble the XML structure by appending elements in the correct order
	presentation_etree.append(material_mattext_etree)
	for response_lid in response_lids_etree:
		presentation_etree.append(response_lid)
	assessment_item_etree.append(itemmetadata)
	assessment_item_etree.append(presentation_etree)
	assessment_item_etree.append(resprocessing_etree)
	# Return the fully assembled XML tree for the question
	return assessment_item_etree

#==============================================================
def NUM(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answer: float, tolerance: float, tol_message=True):
	"""Create a Numerical question with an accepted tolerance range."""
	raise NotImplementedError

#==============================================================
def FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answers_list: list):
	"""Create a Fill-in-the-Blank (Single Blank) question."""
	raise NotImplementedError

#==============================================================
def MULTI_FIB(item_cls):
	#item_number: int, crc16_text: str, question_text: str, answer_map: dict) -> str:
	"""Create a Fill-in-the-Blank (Multiple Blanks) question using answer mapping."""
	raise NotImplementedError

#==============================================================
def ORDER(item_cls):
	#item_number: int, crc16_text: str, question_text: str, ordered_answers_list: list):
	"""Create an Ordered List question where users arrange items in a correct sequence."""
	raise NotImplementedError
