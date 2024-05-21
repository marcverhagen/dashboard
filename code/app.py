"""CLAMS Dashboard

Top-level application code.

"""

import streamlit as st
import pandas as pd
from pathlib import Path
import utils
import config
from repo import repository


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
    'dashboard',
    ['Overview', 'Annotation viewer', 'Evaluation dashboard'],
    label_visibility='hidden')


if dashboard == 'Overview':
    reset_session()
    st.title('CLAMS Dashboards')
    st.info(
        'These pages contain the CLAMS Dashboards, which contain ways to browse ' +
        'the annotations and evaluations repositories. \n\n' +
        'The only available dashboards are the Annotation Viewer and the very ' +
        'beginnings of a dashboard for evaluations.')
    st.markdown('#### The homepages for the repositories are available at')
    st.page_link(
        'https://github.com/clamsproject/aapb-annotations',
        icon="🏠",
        label='AAPB Annotations GitHub Repository')
    st.page_link(
        'https://github.com/clamsproject/aapb-evaluations',
        icon="🏠",
        label='AAPB Evaluations GitHub Repository')

    #utils.print_overview()


elif dashboard == 'Annotation viewer':

    reset_session()
    st.title('CLAMS Annotation Viewer')
    tasks, batches = st.tabs(["Tasks", "Batches"])

    with tasks:
        navigation_col, data_col = tasks.columns([0.2, 0.5])
        task = navigation_col.radio('tasks', ['overview'] + repository.task_names(),
                                    label_visibility='collapsed')
        if task == 'overview':
            tasks_info = [[task.name, len(task)] for task in repository.tasks()]
            data_col.info('Tasks with number of gold files for each')
            data_col.table(pd.DataFrame(tasks_info, columns=['task name', 'files']))
        else:
            task_obj = repository.task(task)
            data_col.info(
                f'Task "{task}" with {len(task_obj.data_drops)} data drops and' +
                f' {len(task_obj)} gold files')
            readme_tab, gold_tab, data_tab, batches_tab, code_tab = data_col.tabs(
                [ "Readme", "Gold files", "Data drops","Batches", "Process.py"])
            with readme_tab:
                # TODO: any links in the readme file need to be updated for streamlit
                # TODO: little intro saying that the stuff below is a README file from
                # a repository and that it was not designed to be displayed in streamlits
                # and that some links may be broken, also include a URL to the repository
                # (might be tricky if we are not in the main branch)
                readme_tab.markdown(repository.task(task).readme)
            with gold_tab: 
                selected_gold = gold_tab.selectbox(
                    'selected_gold', repository.gold_files(task),
                    label_visibility='collapsed')
                gold_tab.text(task_obj.gold_content(selected_gold))
            with data_tab:
                selected_drop = data_tab.radio(
                    'selected_drop', task_obj.data_drops, label_visibility='collapsed')
                data_drop_obj = task_obj.data_drop(selected_drop)
                if data_drop_obj is not None:
                    data_tab.info(
                        f'Data drop "{data_drop_obj.name}" has {len(data_drop_obj)} files')
                    selected_data_drop = data_tab.selectbox(
                        'selected_data_drop', data_drop_obj.file_names,
                        label_visibility='collapsed')
                    data_tab.text(data_drop_obj.file_content(selected_data_drop))
            with batches_tab:
                batches_tab.markdown('##### Overlap with annotation batches')
                data = []
                for batch in repository.batches():
                    comparison = task_obj.compare_to_batch(batch)
                    data.append([batch.name, comparison.in_both, len(batch)])
                batches_tab.table(pd.DataFrame(data, columns=['batch name', 'overlap', 'batch size']))
            with code_tab:
                code_tab.code(repository.task(task).process, language='python')

    with batches:
        navigation_col, data_col = batches.columns([0.2, 0.5])
        batch = navigation_col.radio('batches', ['overview'] + repository.batch_names(),
                                     label_visibility='collapsed')
        if batch == 'overview':
            batches_info = [[batch.name, len(batch)] for batch in repository.batches()]
            data_col.info('Defined batches with number of files for each')
            data_col.table(pd.DataFrame(batches_info, columns=['batch name', 'files']))
        else:
            data_col.markdown(f'### {batch}')
            data_col.info(f'Batch "{batch}" with {len(repository.batch(batch).files)} files')
            task_tab, content_tab = data_col.tabs(['Annotation tasks', 'Batch content'])
            with task_tab:
                task_tab.markdown('##### Overlap with annotation tasks')
                data = []
                for task in repository.tasks():
                    comparison = task.compare_to_batch(repository.batch(batch))
                    data.append([task.name, comparison.in_both, len(task)])
                task_tab.table(pd.DataFrame(data, columns=['task name', 'overlap', 'task size']))
            with content_tab:
                content_tab.markdown('##### Batch file content with file identifiers')
                content_tab.text(repository.batch(batch).content)


elif dashboard == 'Evaluation dashboard':
    st.title('CLAMS Evaluation Dashboard')
    tasks = ['-- select task --'] + repository.task_names()
    task = st.selectbox('eval-category',
                            tasks,
                            on_change=reset_session,
                            label_visibility='collapsed')
    if not task.startswith('--'):
        batches = ['-- select batch --'] + repository.task_names()
        batch_name = st.selectbox('eval-batch',
                                  batches,
                                  on_change=reset_session,
                                  label_visibility='collapsed')
        if not batch_name.startswith('--'):
            st.warning('TBD')
            #batch = repository.batch(task, batch_name)
            #st.info(f"{batch.long_description()}")
            #action_col, table_col = st.columns([1, 4])
            #action_col.button('Create system output', on_click=create_system_output)
            #action_col.button('Evaluate system output', on_click=evaluate_system_output)
            #if 'todo' in st.session_state:
            #    table = utils.create_task_table(repository, category, batch_name)
            #    if st.session_state['todo'].startswith('create'):
            #        table_col.markdown(
            #            '*This will present information on how to create the system data*'
            #            ' *including help on creating MMIF files, running the pipeline,*'
            #            ' *and adding the results to the repository*')
            #    else:
            #        table_col.markdown(
            #            '*This will run the evaluation, store the results and print them*')
            #    table_col.table(pd.DataFrame(table))
            #    utils.write_task_data()
