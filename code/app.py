"""CLAMS Dashboard

"""

import streamlit as st
import pandas as pd

import config
from repo import annotations


# This is here as a placeholder for readme files in the repository
readme = {
    'ner': {
        '2022-jun-namedentity': (
            'Annotation batch over 20 files from **The Newshour with Jim Lehrer**. '
            'Annotated in the Summer of 2022 by one annotator.'),
        'sample': 'Sample batch'
    },
    'nel': {
        '2022-12': 'Named entity annotations over NewsHour files.'
    }
}

st.set_page_config(
    page_title='CLAMS Dashboard',
    layout="wide")

dashboard = st.sidebar.radio(
    'Select a dashboard',
    ['Overview', 'Annotation viewer', 'Evaluation dashboard'])

if dashboard == 'Overview':
    st.title('CLAMS Dashboards')
    st.markdown('#### Annotation Viewer')
    st.image('../docs/workflows/dashboard-annotations.png', width=1000)
    st.markdown('#### Evaluation Dashboard')
    st.image('../docs/workflows/dashboard-evaluation.png', width=1000)

elif dashboard == 'Annotation viewer':
    st.title('CLAMS Annotation Viewer')
    '---'
    col1, _, col2 = st.columns([0.9, 0.1, 4])
    col1.info('Gold data')
    gold = col1.radio('Gold data', annotations.types(), label_visibility='collapsed')
    batch = col1.radio('Select annotation batch',
                       ['overview'] + annotations.batches_in_type(gold))
    if batch == 'overview':
        batch_names = annotations.batches_in_type(gold)
        batches = []
        for name in batch_names:
            batch = annotations.annotation_types[gold].batches[name]
            files = len(batch.files)
            readme_str = readme[gold][name]
            batches.append([name, readme_str, files])
        col2.info(f'{gold}')
        col2.markdown(annotations.annotation_types[gold].directory)
        col2.table(pd.DataFrame(batches, columns=['batch', 'description', 'files']))
    else:
        col2.info(f'{gold} &longrightarrow; {batch}')
        col2.markdown(annotations.annotation_types[gold].batches[batch].directory)
        col2.markdown(readme[gold][batch])
        col2.table(pd.DataFrame(annotations.files_in_batch(gold, batch),
                                columns=['file name', 'size']))

elif dashboard == 'Evaluation dashboard':
    st.title('CLAMS Evaluation Dashboard')
    st.info(config.sources)
    st.info(config.annotations)
