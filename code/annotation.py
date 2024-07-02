import os
import re
import json
from pathlib import Path
from collections import namedtuple

import utils
import config


Comparison = namedtuple('Comparison', ['in_both', 'in_first', 'in_second'])


class Repository:

    def __init__(self, directory: str):
        self.path = Path(directory)
        self.readme = Path(self.path / 'README.md').open().read()
        self._batches = { p.stem: Batch(p) for p in self.batch_directories() }
        self._tasks = { p.stem: Task(self, p) for p in self.task_directories() }

    def __str__(self):
        return f'<{self.__class__.__name__} {self.path}>'

    def task_directories(self):
        # TODO: now depends on there being a golds subdir, should maybe also
        # look whether there are data drop directories
        return [ p for p in self.path.iterdir() if Path(p / 'golds').is_dir()]

    def task_names(self):
        return list([task.name for task in self.tasks()])

    def task(self, task: str):
        return self._tasks[task]

    def tasks(self):
        return sorted(self._tasks.values())

    def batch(self, name: str):
        return self._batches[name]

    def batch_directories(self):
        return [p for p in Path(self.path / 'batches').iterdir()]

    def batch_names(self):
        return sorted(self._batches.keys())

    def batches(self):
        return sorted(self._batches.values())

    def gold_files(self, task: str):
        return [p.name for p in self.task(task).gold_files]

    def pp(self):
        print()
        print(self)
        print('\nBatches:')
        for batch in self._batches:
            print('   ', batch)
        print('\nTasks:')
        for task in self._tasks:
            print('   ', task)
        print()


class Batch(utils.Directory):

    def __init__(self, path: Path):
        super().__init__(path)
        self.files = []
        with open(path) as fh:
            lines = fh.readlines()
            self.files = [l.strip() for l in lines if not l.strip().startswith('#')]
            self.content = ''.join(lines)

    def __len__(self):
        return len(self.files)


class Task(utils.Directory):

    def __init__ (self, rep: Repository, path: Path):
        super().__init__(path)
        self.path = path
        self._gold_directory = Path(path / 'golds')
        self._gold_files = None
        self.readme_file = Path(path / 'readme.md')
        self.readme = utils.read_file(self.readme_file)
        self.process_file = Path(path / 'process.py')
        self.process = self.process_content()
        self.data_drops = {}
        for subdir in self.path.iterdir():
            if subdir.is_dir() and re.match(r'\d{6}', subdir.name):
                self.data_drops[subdir.name] = DataDrop(subdir)

    def __str__(self):
        return f'<Task {self.path}>'

    def __len__(self):
        return len(self.gold_files)

    @property
    def gold_directory(self):
        return self._gold_directory
    
    @property
    def gold_files(self):
        if self._gold_files is None:
            self._gold_files = []
            for path in sorted(self._gold_directory.iterdir()):
                if path.is_file():
                    self._gold_files.append(path)
                else:
                    for subpath in sorted(path.iterdir()):
                        self._gold_files.append(subpath)
        return self._gold_files
    
    def process_content(self):
        if self.process_file.is_file():
            with self.process_file.open() as fh:
                return fh.read()
        return ''

    def gold_file_ids(self):
        return [f.stem for f in self.gold_files]

    def data_drop(self, data_drop: str):
        return self.data_drops.get(data_drop)

    def gold_content(self, gold_file):
        if gold_file is None:
            return ''
        gold_path = Path(self._gold_directory / gold_file)
        with open(gold_path) as fh:
            return fh.read()

    def compare_to_batch(self, batch: Batch):
        gold_files = set(self.gold_file_ids())
        batch_files = set(batch.files)
        return Comparison(
            len(gold_files.intersection(batch_files)),
            len(gold_files.difference(batch_files)),
            len(batch_files.difference(gold_files)))


class DataDrop(utils.Directory):

    def __init__(self, path: Path):
        super().__init__(path)
        self.files = list([f for f in self.path.iterdir()])
        self.file_names = [f.name for f in self.files]

    def __len__(self):
        return len(self.files)

    def __str__(self):
        return f'<{self.__class__.__name__} {self.name} files={len(self)}>'

    def file_content(self, filename: str):
        path = Path(self.path / filename)
        if path.suffix == '.json':
            return json.dumps(json.load(path.open()), indent=2)
        with path.open() as fh:
            return fh.read()



if __name__ == '__main__':

    repo = Repository(config.ANNOTATIONS)
    print(repo)
    for task in (repo.task('scene-recognition'), repo.task('newshour-chyron')):
        print(f'\n{task}\n')
        for p in task.gold_files:
            print(p)
