# The CLAMS Dashboard

Experiments with a CLAMS dashboard, starting with an annotation viewer and an evaluation viewer.


### Requirements

Install the necessary Python modules:

```shell
pip install streamlit==1.34.0
pip install directory-tree==1.0.0
```

Or use the requirements file:

```shell
pip install -f requirements.txt
```

 
The dashboard expects access to a couple of repositories, you should get a local copy of them:

<!--
<img src="docs/workflows/dashboard-annotations.png" width=500>
<img src="docs/workflows/dashboard-evaluation.png" width=500>
-->

- [https://github.com/clamsproject/aapb-annotations](https://github.com/clamsproject/aapb-annotations)
- [https://github.com/clamsproject/aapb-evaluations](https://github.com/clamsproject/aapb-evaluations)
- [https://github.com/clamsproject/aapb-collaboration](https://github.com/clamsproject/aapb-collaboration)

Once these repositories are available on your local machine, edit the following lines in `code/config.py` if needed:

```python
# The default is that source files, annotations and evaluations are in a sister repository.
SOURCES = '../../wgbh-collaboration/'
ANNOTATIONS = '../../aapb-annotations/'
EVALUATIONS = '../../aapb-evaluations/'
```


### Running the Dashboard

To start the Streamlit application:

```shell
streamlit run app.py
```

