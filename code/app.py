"""CLAMS Dashboard

Top-level application code.

"""

import streamlit as st
import pandas as pd
import utils
from repo import annotations


def reset_session():
    if 'todo' in st.session_state:
        st.session_state.pop('todo')

def create_system_output():
    st.session_state['todo'] = f'create-system-output'

def evaluate_system_output():
    st.session_state['todo'] = f'evaluate-system-output'


st.set_page_config(
    page_title='CLAMS Dashboard',
    layout="wide")

st.markdown(utils.style, unsafe_allow_html=True)

dashboard = st.sidebar.radio(
    'Select a dashboard',
    ['Overview', 'Annotation viewer', 'Evaluation dashboard'])

if dashboard == 'Overview':
    reset_session()
    utils.print_overview()

elif dashboard == 'Annotation viewer':
    reset_session()
    st.title('CLAMS Annotation Viewer')
    navigation_col, _spacer, data_col = st.columns([0.9, 0.1, 4])
    category = navigation_col.radio('Categories', ['overview'] + annotations.category_names())
    if category == 'overview':
        utils.print_categories(data_col, annotations)
    else:
        batch = navigation_col.radio(
            'Select annotation batch',
            ['overview'] + annotations.batch_names(category))
        if batch == 'overview':
            utils.print_batches_for_category(data_col, category, annotations)
        else:
            utils.print_files_for_batch(data_col, category, batch, annotations)

elif dashboard == 'Evaluation dashboard':
    st.title('CLAMS Evaluation Dashboard')
    categories = ['-- select category --'] + annotations.category_names()
    category = st.selectbox('eval-category',
                            categories,
                            on_change=reset_session,
                            label_visibility='collapsed')
    if not category.startswith('--'):
        batches = ['-- select batch --'] + annotations.batch_names(category)
        batch_name = st.selectbox('eval-batch',
                                  batches,
                                  on_change=reset_session,
                                  label_visibility='collapsed')
        if not batch_name.startswith('--'):
            batch = annotations.batch(category, batch_name)
            st.info(f"{batch.long_description()}")
            action_col, table_col = st.columns([1, 4])
            action_col.button('Create system output', on_click=create_system_output)
            action_col.button('Evaluate system output', on_click=evaluate_system_output)
            if 'todo' in st.session_state:
                table = utils.create_task_table(annotations, category, batch_name)
                if st.session_state['todo'].startswith('create'):
                    table_col.markdown(
                        '*This will present information on how to create the system data*'
                        ' *including help on creating MMIF files, running the pipeline,*'
                        ' *and adding the results to the repository*')
                else:
                    table_col.markdown(
                        '*This will run the evaluation, store the results and print them*')
                table_col.table(pd.DataFrame(table))
                utils.write_task_data()
