# The CLAMS Dashboard

Experiments with CLAMS dashboards, starting with an annotation viewer and an evaluation dashboard.

To run the dashboard first install the necessary Python modules:

```shell
pip install -f requirements.txt
```

Then start the Streamlit application:

```shell
streamlit run app.py
```

Dashboards expect access to a couple of repositories:

<img src="docs/workflows/dashboard-annotations.png" width=500>
<img src="docs/workflows/dashboard-evaluation.png" width=500>

You should get a local copy of these repositories:

- [https://github.com/clamsproject/aapb-annotations](https://github.com/clamsproject/aapb-annotations)
- [https://github.com/clamsproject/aapb-evaluations](https://github.com/clamsproject/aapb-evaluations)
- [https://github.com/clamsproject/aapb-collaboration](https://github.com/clamsproject/aapb-collaboration)

Once they are available on your local machine, edit the following lines in `code/config.py` if needed:

```python
# By default, assume the files, annotations and evaluations are in a sister repository
SOURCES = '../../wgbh-collaboration/'
ANNOTATIONS = '../../aapb-annotations/'
EVALUATIONS = '../../aapb-evaluations/'
```
