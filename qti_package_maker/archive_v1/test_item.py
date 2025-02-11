#!/usr/bin/env python3

# Standard Library

# Pip3 Library
import lxml.etree

# QTI Package Maker
import items

question_text = 'what is your favorite color?'
choices_list = ['blue', 'red', 'yellow']
answer_text = 'red'
etree = items.add_QTI_MC_Question(1, question_text, choices_list, answer_text)

# Convert lxml.etree to a string
xml_string = lxml.etree.tostring(etree, pretty_print=True, encoding='unicode')
print(xml_string)

# Save the formatted XML to a file
with open("output.xml", "w") as f:
    f.write(xml_string)

print("XML saved as 'output.xml'")
