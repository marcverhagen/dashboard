
import pandas as pd
import streamlit as st
from directory_tree import DisplayTree

import utils


def viewer(MODEL, CHECKOUT):

    ANNOTATIONS = MODEL.annotations
    EVALUATIONS = MODEL.evaluations

    st.title('CLAMS Annotation Viewer')

    if CHECKOUT:
        branch = utils.st_display_branch(st, ANNOTATIONS)
        ANNOTATIONS.checkout(branch)

    readme, tasks, batches = st.tabs(['Repository readme file', 'Tasks', 'Batches'])

    with readme:
        readme.markdown(ANNOTATIONS.readme)

    with tasks:
        navigation_col, data_col = tasks.columns([0.2, 0.5])
        task = navigation_col.radio('tasks', ['overview'] + ANNOTATIONS.task_names,
                                    label_visibility='collapsed')
        if task == 'overview':
            tasks_info = [[task.name, len(task)] for task in ANNOTATIONS.tasks]
            data_col.info('Tasks with number of gold files for each')
            data_col.table(pd.DataFrame(tasks_info, columns=['task name', 'files']))

        else:
            task_obj = ANNOTATIONS.task(task)
            data_col.info(
                f'Task "{task}" with {len(task_obj.data_drops)} data drops and' +
                f' {len(task_obj)} gold files')

            readme_tab, gold_tab1, gold_tab2, data_tab, batches_tab, code_tab = \
                data_col.tabs(
                    ["Readme", "Gold directory", "Gold files", "Data drops",
                     "Batches", "Process.py"])

            with readme_tab:
                # TODO: any links in the readme file need to be updated for streamlit
                # TODO: little intro saying that the stuff below is a README file from
                # a repository and that it was not designed to be displayed in streamlit
                # and that some links may be broken, also include a URL to the repository
                # (might be tricky if we are not in the main branch)
                readme_tab.markdown(ANNOTATIONS.task(task).readme)

            with gold_tab1:
                tree = DisplayTree(task_obj.gold_directory, stringRep=True)
                st.text_area(label='Gold directory tree', value=tree, height=800)

            with gold_tab2:
                selected_gold = utils.st_list_files2(gold_tab2, task_obj)
                gold_tab2.text(task_obj.gold_content(selected_gold))

            with data_tab:
                data_drops = list(task_obj.data_drops.keys())
                data_tab.text(f'Number of data drops: {len(data_drops)}')
                data_drop = utils.st_list_files(
                    data_tab, 'selected_drop', data_drops, cutoff=0)
                data_drop_obj = task_obj.data_drop(data_drop)
                if data_drop_obj is not None:
                    data_tab.text(f'Number of files in this data drop: {len(data_drop_obj)}')
                    data_drop_file = utils.st_list_files(
                        data_tab, 'selected_data_drop', data_drop_obj.file_names, cutoff=0)
                    data_tab.text(data_drop_obj.file_content(data_drop_file))

            with batches_tab:
                batches_tab.markdown('##### GUIDs from annotation batches used in this task')
                data = []
                for batch in ANNOTATIONS.batches:
                    comparison = task_obj.compare_to_batch(batch)
                    data.append([batch.name, comparison.in_both, len(batch)])
                columns = ['batch name', 'guids', 'batch size']
                batches_tab.table(pd.DataFrame(data, columns=columns))

            with code_tab:
                code_tab.code(ANNOTATIONS.task(task).process, language='python')

    with batches:

        navigation_col, data_col = batches.columns([0.2, 0.5])
        batch = navigation_col.radio('batches', ['overview'] + ANNOTATIONS.batch_names,
                                     label_visibility='collapsed')

        if batch == 'overview':
            batches_info = [[batch.name, len(batch)] for batch in ANNOTATIONS.batches]
            data_col.info('Defined batches with number of files for each')
            data_col.table(pd.DataFrame(batches_info, columns=['batch name', 'files']))

        else:
            data_col.markdown(f'### {batch}')
            data_col.info(f'Batch "{batch}" with {len(ANNOTATIONS.batch(batch).files)} files')
            data_col.info(f'{ANNOTATIONS.batch(batch).comment}')

            files_tab, content_tab, task_tab, preds_tab = \
                data_col.tabs(
                    ['File identifiers', 'Full batch file content',
                     'Annotation tasks', 'Use in evaluations'])

            with files_tab:
                files_tab.text('\n'.join(ANNOTATIONS.batch(batch).files))

            with content_tab:
                content_tab.markdown('##### Batch file content with file identifiers')
                content_tab.text(ANNOTATIONS.batch(batch).content)

            with task_tab:
                task_tab.markdown('##### Batch usage by annotation tasks')
                task_tab.markdown('This shows how many GUIDs from this batch were used'
                                  + ' in all annotation tasks.')
                data = []
                for task in ANNOTATIONS.tasks:
                    comparison = task.compare_to_batch(ANNOTATIONS.batch(batch))
                    data.append([task.name, comparison.in_both, len(task)])
                columns = ['task name', 'overlap', 'task size']
                task_tab.table(pd.DataFrame(data, columns=columns))

            with preds_tab:
                preds_tab.markdown('##### Batch usage in evaluation repository')
                preds_tab.markdown('Usage in system predictions:')
                preds_tab.table(
                    pd.DataFrame(MODEL.batch_usage_in_system_predictions(batch),
                                 columns=['evaluation', 'system predictions']))
                preds_tab.markdown('Usage in system reports:')
                preds_tab.table(
                    pd.DataFrame(MODEL.batch_usage_in_system_reports(batch),
                                 columns=['evaluation', 'system report']))

