import streamlit as st
import pandas as pd
import utils


def view(ANNOTATIONS):

    st.title('CLAMS Annotation Viewer')

    branches = ANNOTATIONS.branches
    branch_names = ANNOTATIONS.branch_names
    index = utils.get_index(branch_names, 'main')
    branch = st.selectbox('Branch in repository:', branch_names, index=index)
    branches[branch].checkout()

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
                for batch in ANNOTATIONS.batches:
                    comparison = task_obj.compare_to_batch(batch)
                    data.append([batch.name, comparison.in_both, len(batch)])
                columns = ['batch name', 'overlap', 'batch size']
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

            files_tab, content_tab, task_tab = \
                data_col.tabs(['File identifiers', 'Full batch file content', 'Annotation tasks'])

            with task_tab:
                task_tab.markdown('##### Overlap with annotation tasks')
                data = []
                for task in ANNOTATIONS.tasks:
                    comparison = task.compare_to_batch(ANNOTATIONS.batch(batch))
                    data.append([task.name, comparison.in_both, len(task)])
                columns = ['task name', 'overlap', 'task size']
                task_tab.table(pd.DataFrame(data, columns=columns))

            with files_tab:
                files_tab.text('\n'.join(ANNOTATIONS.batch(batch).files))

            with content_tab:
                content_tab.markdown('##### Batch file content with file identifiers')
                content_tab.text(ANNOTATIONS.batch(batch).content)
