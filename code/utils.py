import os

import pandas as pd
import streamlit as st
import config


def create_task_table(annotations, category, batch_name):
    table = [
        ['task', st.session_state['todo']],
        ['category', category]]
    if st.session_state['todo'].startswith('create'):
        table.extend([
            ['pipeline', ''],
            ['sources', config.sources],
            ['system output', '']])
    else:
        table.extend([
            ['gold standard', annotations.batch(category, batch_name).directory],
            ['system output', '']])
    return table

def write_task_data():
    # just some simple placeholder code for now
    with open('create_system_output.txt', 'w') as fh:
        fh.write(config.sources)
        fh.write(config.annotations)

def print_overview():
    st.title('CLAMS Dashboards')
    st.markdown('#### Annotation Viewer')
    st.image('../docs/workflows/dashboard-annotations.png', width=1000)
    st.markdown('#### Evaluation Dashboard')
    st.image('../docs/workflows/dashboard-evaluation.png', width=1000)

def print_categories(column, annotations):
    column.info('Annotation categories')
    column.markdown(os.path.join(annotations.directory, 'golds'))
    column.table(pd.DataFrame(annotations.types_with_batches_count(),
                              columns=['category', 'description', 'batches']))

def print_batches_for_category(column, category: str, annotations):
    batch_names = annotations.batch_names(category)
    batches = []
    for name in batch_names:
        batch = annotations.categories[category].batches[name]
        batches.append([name, batch.short_description(), len(batch.files)])
    column.info(f'{category}')
    column.markdown(annotations.category(category).directory)
    column.table(pd.DataFrame(batches, columns=['batch', 'description', 'files']))

def print_files_for_batch(column, category, batch_name, annotations):
    description = annotations.batch(category, batch_name).long_description()
    column.info(f'{category} &longrightarrow; {batch_name}')
    column.markdown(annotations.batch(category, batch_name).directory)
    if description:
        column.markdown(description)
    column.table(pd.DataFrame(annotations.files_in_batch(category, batch_name),
                              columns=['file name', 'size']))


style = """
<style>
thead tr th:first-child {display:none}
tbody th {display:none}
</style>
"""
