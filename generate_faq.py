#!/usr/bin/env python
import os

template = """
<h5> <a href="#!">%(question)s<span class="fas fa-caret-right ms-2"></span></a></h5>
<p class="fs--1 mb-0">%(answer)s</p>
"""
separator = "<hr class=\"my-3\" />"

f = open("faq_lines.txt", "r")

lines = f.readlines()

for n, line in enumerate(lines):
    if n%2 == 1:
        print(template%{'question': lines[n-1].strip(), 'answer': lines[n].strip()})
    if n>0 and n%2 == 0:
        print(separator)
