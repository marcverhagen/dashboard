"""Configuration settings"""

import os

# TODO: this is way too hackish, consider it a placeholder
current_directory = os.path.abspath(os.path.curdir)
if 'Documents/git' in current_directory:
    sources = '/Users/marc/Documents/git/clams/wgbh-collaboration/'
    annotations = '/Users/marc/Documents/git/clams/clams-aapb-annotations/'
else:
    sources = '/Users/marc/Desktop/projects/clams/code/clamsproject/wgbh-collaboration/'
    annotations = '/Users/marc/Desktop/projects/clams/code/clamsproject/clams-aapb-annotations/'


DESCRIPTIONS = { 'ner': 'Named Entities',
                 'nel': 'Named Entity Links (groundings)' }
