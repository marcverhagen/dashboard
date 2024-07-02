"""CLAMS Dashboard

Top-level application code.

"""

import json
from pathlib import Path

import streamlit as st
import pandas as pd

import utils
import config
import annotation
import evaluation


# Maximum size of a file, if it is larger, the user will be prompted whether it
# should be displayed
MAX_FILESIZE = 100000


if 'ANNOTATIONS' not in st.session_state:
    st.session_state['ANNOTATIONS'] = annotation.Repository(config.ANNOTATIONS)
    st.session_state['EVALUATIONS'] = evaluation.Repository(config.EVALUATIONS)

ANNOTATIONS = st.session_state['ANNOTATIONS']
EVALUATIONS = st.session_state['EVALUATIONS']

ANNOTATIONS = annotation.Repository(config.ANNOTATIONS)
EVALUATIONS = evaluation.Repository(config.EVALUATIONS)


st.set_page_config(
    page_title='CLAMS Dashboard',
    layout="wide")

st.markdown(utils.style, unsafe_allow_html=True)


dashboard = st.sidebar.radio(
    'dashboard',
    ['Overview', 'Annotation viewer', 'Evaluation viewer'],
    label_visibility='hidden')


if dashboard == 'Overview':

    st.title('CLAMS Dashboard')
    st.info(
        'These pages contain the CLAMS Viewers, which provide ways to browse ' +
        'the annotations and evaluations repositories. \n\n')
    st.markdown('##### The homepages for the repositories are available at')
    st.page_link(
        'https://github.com/clamsproject/aapb-annotations',
        icon="🏠",
        label='AAPB Annotations GitHub Repository')
    st.page_link(
        'https://github.com/clamsproject/aapb-evaluations',
        icon="🏠",
        label='AAPB Evaluations GitHub Repository')
    st.markdown('The code for this dashboard is maintained at '
                + '[https://github.com/clamsproject/dashboard]'
                + '(https://github.com/clamsproject/dashboard)')


elif dashboard == 'Annotation viewer':

    st.title('CLAMS Annotation Viewer')
    readme, tasks, batches = st.tabs(['Repository readme file', 'Tasks', 'Batches'])

    with readme:
        readme.markdown(ANNOTATIONS.readme)

    with tasks:
        navigation_col, data_col = tasks.columns([0.2, 0.5])
        task = navigation_col.radio('tasks', ['overview'] + ANNOTATIONS.task_names(),
                                    label_visibility='collapsed')
        if task == 'overview':
            tasks_info = [[task.name, len(task)] for task in ANNOTATIONS.tasks()]
            data_col.info('Tasks with number of gold files for each')
            data_col.table(pd.DataFrame(tasks_info, columns=['task name', 'files']))

        else:
            task_obj = ANNOTATIONS.task(task)
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
                readme_tab.markdown(ANNOTATIONS.task(task).readme)

            with gold_tab:
                selected_gold = utils.st_list_files2(gold_tab, task_obj)
                gold_tab.text(task_obj.gold_content(selected_gold))

            with data_tab:
                selected_drop = utils.st_list_files(
                    data_tab, 'selected_drop', task_obj.data_drops)
                data_drop_obj = task_obj.data_drop(selected_drop)
                if data_drop_obj is not None:
                    data_tab.info(
                        f'Data drop "{data_drop_obj.name}" has {len(data_drop_obj)} files')
                    selected_data_drop = utils.st_list_files(
                        data_tab, 'selected_data_drop', data_drop_obj.file_names)
                    data_tab.text(data_drop_obj.file_content(selected_data_drop))

            with batches_tab:
                batches_tab.markdown('##### Overlap with annotation batches')
                data = []
                for batch in ANNOTATIONS.batches():
                    comparison = task_obj.compare_to_batch(batch)
                    data.append([batch.name, comparison.in_both, len(batch)])
                columns = ['batch name', 'overlap', 'batch size']
                batches_tab.table(pd.DataFrame(data, columns=columns))

            with code_tab:
                code_tab.code(ANNOTATIONS.task(task).process, language='python')

    with batches:

        navigation_col, data_col = batches.columns([0.2, 0.5])
        batch = navigation_col.radio('batches', ['overview'] + ANNOTATIONS.batch_names(),
                                     label_visibility='collapsed')

        if batch == 'overview':
            batches_info = [[batch.name, len(batch)] for batch in ANNOTATIONS.batches()]
            data_col.info('Defined batches with number of files for each')
            data_col.table(pd.DataFrame(batches_info, columns=['batch name', 'files']))

        else:
            data_col.markdown(f'### {batch}')
            data_col.info(f'Batch "{batch}" with {len(ANNOTATIONS.batch(batch).files)} files')

            files_tab, content_tab, task_tab = \
                data_col.tabs(['File identifiers', 'Full batch file content', 'Annotation tasks'])

            with task_tab:
                task_tab.markdown('##### Overlap with annotation tasks')
                data = []
                for task in ANNOTATIONS.tasks():
                    comparison = task.compare_to_batch(ANNOTATIONS.batch(batch))
                    data.append([task.name, comparison.in_both, len(task)])
                columns = ['task name', 'overlap', 'task size']
                task_tab.table(pd.DataFrame(data, columns=columns))

            with files_tab:
                files_tab.text('\n'.join(ANNOTATIONS.batch(batch).files))

            with content_tab:
                content_tab.markdown('##### Batch file content with file identifiers')
                content_tab.text(ANNOTATIONS.batch(batch).content)


elif dashboard == 'Evaluation viewer':

    st.title('CLAMS Evaluation Viewer')
    navigation_col, eval_col = st.columns([0.2, 0.8])

    eval_name = navigation_col.radio(
        'eval-category', EVALUATIONS.evaluation_names(), label_visibility='collapsed')
    evaluation = EVALUATIONS.evaluation(eval_name)

    eval_col.info(
        f'Evaluation "{evaluation.name}"'
        + f' with {len(evaluation.predictions)} predictions'
        + f' and {len(evaluation.reports)} reports')

    readme_tab, code_tab, predictions_tab, reports_tab = eval_col.tabs(
        [ 'Readme', 'Code', 'Predictions', 'Reports'])

    with readme_tab:
        readme_tab.markdown(evaluation.readme)
    
    with code_tab:
        code_file_names = [f.name for f in evaluation.code_files]
        code_file = code_tab.radio(
            'code_file', code_file_names, label_visibility='collapsed')
        code_tab.code(utils.read_file(evaluation.path / code_file))

    with predictions_tab:
        prediction = utils.st_list_files(
            predictions_tab, 'prediction', evaluation.predictions.keys())
        if prediction is not None:
            prediction_obj = evaluation.prediction(prediction)
            predictions_tab.markdown('##### Readme file')
            prediction_obj.readme
            prediction_files = prediction_obj.file_names()
            predictions_tab.markdown('##### Prediction files')
            predictions_tab.markdown(f'&nbsp;*{len(prediction_files)} files*')
            prediction_file = utils.st_list_files(
                predictions_tab, 'prediction_files', prediction_files)
            path = evaluation.path / prediction / prediction_file
            file_size = path.stat().st_size
            predictions_tab.markdown(f'*File size: {file_size:,}*')
            if file_size < MAX_FILESIZE:
                utils.st_display_file(predictions_tab, path)
            else:
                predictions_tab.markdown(f'*This file is rather big, print it anyway?*')
                print_file = predictions_tab.button('Print File')
                if print_file:
                    utils.st_display_file(predictions_tab, path)
    
    with reports_tab:
        report = utils.st_list_files(
            reports_tab, 'report', evaluation.reports.keys())
        if report is not None:
            reports_tab.markdown(utils.read_file(evaluation.path / report))

