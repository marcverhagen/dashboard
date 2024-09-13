"""CLAMS Dashboard

Top-level application code.

To run this:

$ streamlit run app.py
$ streamlit run app.py -- OPTION+

The second invocation is meant to send options to the application. We have the
following options:

debug
    This for when the appliation runs in debug mode, that is, when you select
    "Always rerun" after a code update. These reruns do not impact the session
    state I think which causes some code updates to not be reflected in the new
    interface, with the debug option annotations and evaluations will be reloaded.

no-checkout
    Do not checkout a branch in the annotation/evaluation repository. This is
    useful when experimenting with the code on changes in the repositories that
    were not committed. Also, when your annotation/evaluation repository has 
    local changes then checkout will fail.

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
from viewers.annotation_viewer import viewer as annotation_viewer
from viewers.evaluation_viewer import viewer as evaluation_viewer


# No debugging by default, this can be overwritten by handing an argument to the
# script, as explained in the doc string.
DEBUG = False
if 'debug' in sys.argv[1:]:
    DEBUG = True

CHECKOUT = True
if 'no-checkout' in sys.argv[1:]:
    CHECKOUT = False

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

    annotation_viewer(ANNOTATIONS, CHECKOUT)

elif dashboard == 'Evaluation viewer':

    evaluation_viewer(EVALUATIONS)
