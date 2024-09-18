
from pathlib import Path
import config
import utils


class Repository:

    """Class to give access to data in the evaluation repository."""

    def __init__(self, directory: str):
        self.path = Path(directory) 
        self.evaluations_idx = { p.stem: Evaluation(p) for p in self.eval_directories() }
        self.evaluations = sorted(self.evaluations_idx.values())
        self.evaluation_names = sorted(self.evaluations_idx.keys())

    def __str__(self):
        return f'<{self.__class__.__name__} "{self.path.name}">'

    def __getitem__(self, index: int):
        return self.evaluations[index]

    def eval_directories(self):
        return [ p for p in self.path.iterdir() if p.name.endswith('eval') and p.is_dir()]

    def evaluation(self, name: str):
        return self.evaluations_idx.get(name)


class Evaluation(utils.FileSystemNode):

    def __init__(self, path: Path):
        super().__init__(path)
        self.readme_file = Path(path / 'README.md')
        self.readme = utils.read_file(self.readme_file)
        self._scripts = list(path.glob('*.py'))
        self._predictions = {}
        self.reports = {}
        for p in self.path.iterdir():
            if p.is_dir() and p.name.startswith('preds@'):
                self._predictions[p.name] = PredictionBatch(p)
            elif p.is_file() and p.name.startswith('report-'):
                self.reports[p.name] = Report(p)

    def __str__(self):
        return f'<{self.__class__.__name__} "{self.path.stem}">'

    def __lt__(self, other):
        return self.path.stem < other.path.stem

    def __eq__(self, other):
        return self.path.stem == other.path.stem

    def prediction(self, name: str):
        return self._predictions.get(name)

    @property
    def predictions(self):
        return self._predictions.values()

    @property
    def prediction_names(self):
        return sorted(self._predictions.keys())

    @property
    def scripts(self):
        return self._scripts

    def get_reports(self):
        return sorted(self.reports.values())


    def info(self):
        return (
            f'{self}\n\n'
            + f'code files {[f.stem for f in self.scripts]}')


class PredictionBatch(utils.FileSystemNode):

    """Class to wrap a directory with predictions. Each prediction is a MMIF file
    with processing results."""

    def __init__(self, path: Path):
        super().__init__(path)
        if len(self.name.split('@')) < 3:
            print("WARNING - missing component in name:", self.path)
        self.prediction_name = '@'.join(self.name.split('@')[1:-1])
        self.prediction_batch = self.name.split('@')[-1]
        self.readme = None
        self.files = {}
        readme_path = self.path / 'README.md'
        if readme_path.is_file():
            self.readme = utils.read_file(readme_path)
        for p in self.path.iterdir():
            if p.is_file() and p.name.endswith('.mmif'):
                self.files[p.name] = p
        
    def __str__(self):
        return f'<{self.__class__.__name__} {self.prediction_name} {self.prediction_batch}>'

    def file_names(self):
        return sorted(self.files)


class Report(utils.FileSystemNode):

    def __init__(self, path: Path):
        super().__init__(path)
        self.report_tool = self.name.split('@')[-2]
        self.report_batch = self.path.stem.split('@')[-1]
        self.content = utils.read_file(self.path)



if __name__ == '__main__':

    repo = Repository(config.EVALUATIONS)
    print(repo)

    for evaluation in repo.evaluations:
        print(f'\n -- {evaluation}')
        for prediction in evaluation.predictions:
            print('   ', prediction)
