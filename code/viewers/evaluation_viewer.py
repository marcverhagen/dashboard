import streamlit as st
import utils
import config


def view(EVALUATIONS):

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
            if file_size < config.MAX_FILESIZE:
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
