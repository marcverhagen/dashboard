"""CLAMS Evaluation

Placeholder for top-level evaluation code.

For now just a viewer of the evaluation repository.

Other modules needed:

- evaluation measures
- data handling
- hooks to visualization (submodule or pip install?)
- hooks to pipeline runner

There is a good case to be made to have some of these as part of a mmif-utils
package.

"""

from pathlib import Path
import utils


class Repository:

    def __init__(self, directory: str):
        self.path = Path(directory) 
        self._evaluations = { p.stem: Evaluation(p) for p in self.eval_directories() }

    def eval_directories(self):
        return [ p for p in self.path.iterdir() if p.name.endswith('eval') and p.is_dir()]

    def evaluation_names(self):
        return sorted(self._evaluations.keys())

    def evaluation(self, name: str):
        return self._evaluations.get(name)

    def evaluations(self):
        return sorted(self._evaluations.values())


class Evaluation(utils.Directory):

    def __init__(self, path: Path):
        super().__init__(path)
        self.readme_file = Path(path / 'README.md')
        self.readme = utils.read_file(self.readme_file)
        self.code_files = list(path.glob('*.py'))
        self.predictions = {}
        self.reports = {}
        for p in self.path.iterdir():
            if p.is_dir() and p.name.startswith('preds@'):
                self.predictions[p.name] = Predictions(p)
            elif p.is_file() and p.name.startswith('report-'):
                self.reports[p.name] = p

    def prediction(self, name: str):
        return self.predictions.get(name)

    def info(self):
        return (
            f'{self}\n\n'
            + f'code files {[f.stem for f in self.code_files]}')


class Predictions(utils.Directory):

    """Class to wrap a directory with predictions. Each prediction is a MMIF file
    with processing results."""

    def __init__(self, path: Path):
        super().__init__(path)
        self.readme = None
        self.files = {}
        readme_path = self.path / 'README.md'
        if readme_path.is_file():
            self.readme = utils.read_file(readme_path)
        for p in self.path.iterdir():
            if p.is_file() and p.name.endswith('.mmif'):
                self.files[p.name] = p
        
    def file_names(self):
        return sorted(self.files)