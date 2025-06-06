import re
import pandas as pd
from lxml import etree


template_fname = '../report/scenario.html'

with open(template_fname, 'r') as f:
    c = f.read()

tree = etree.HTML(c)

sec_root = tree.xpath('//ui[@id=scenario_root]')[0]


print(etree.tostring(sec_root))
