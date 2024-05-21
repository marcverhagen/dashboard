import os

import pandas as pd
import streamlit as st
import config


def write_task_data():
    # just some simple placeholder code for now
    with open('create_system_output.txt', 'w') as fh:
        fh.write(config.sources)
        fh.write(config.annotations)

def print_overview():
    st.title('CLAMS Dashboards')
    st.markdown('### Annotation Viewer')
    st.image('../docs/workflows/dashboard-annotations.png')
    st.markdown('### Evaluation Dashboard')
    st.image('../docs/workflows/dashboard-evaluation.png')

def file_size(directory, project_name, file_name):
    path = os.path.join(directory, project_name, file_name)
    # We could use f'{os.path.getsize(path):,}', but then the column will be
    # left aligned, which we may or may not be able to fix with a pandas Styler
    return os.path.getsize(path)


# Style to supress printing the first column of a table
style = """
<style>
thead tr th:first-child {display:none}
tbody th {display:none}
</style>
"""
