"""CLAMS Dashboard

Top-level application code.

To run this:

$ streamlit run app.py
$ streamlit run app.py -- debug

The second invocation runs the appliation in debug mode, meaning the annotation
and evaluation repositories are updated when the code restarts. It also allows
printing to the standard output if used.

"""

import json
import sys
from pathlib import Path

import streamlit as st
import pandas as pd

import utils
import config
import annotation
import evaluation
from viewers.annotation_viewer import view as annotation_viewer
from viewers.evaluation_viewer import view as evaluation_viewer


# No debugging by default, this can be overwritten by handing an argument to the
# script, as explained in the doc string.
DEBUG = False
if 'debug' in sys.argv[1:]:
    DEBUG = True


if 'ANNOTATIONS' not in st.session_state:
    st.session_state['ANNOTATIONS'] = annotation.Repository(config.ANNOTATIONS)
    st.session_state['EVALUATIONS'] = evaluation.Repository(config.EVALUATIONS)
ANNOTATIONS = st.session_state['ANNOTATIONS']
EVALUATIONS = st.session_state['EVALUATIONS']

# Without this, updates to Repository code will not be available on restarts.
if DEBUG:
    ANNOTATIONS = annotation.Repository(config.ANNOTATIONS)
    EVALUATIONS = evaluation.Repository(config.EVALUATIONS)


def debug(text: str):
    if DEBUG:
        print(text)


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

    annotation_viewer(ANNOTATIONS)

elif dashboard == 'Evaluation viewer':

    evaluation_viewer(EVALUATIONS)
