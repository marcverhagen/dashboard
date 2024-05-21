import os
import re
import json
from pathlib import Path
from collections import namedtuple
import config


Comparison = namedtuple('Comparison', ['in_both', 'in_first', 'in_second'])


class Repository:

    def __init__(self, directory: str):
        self.path = Path(directory)
        self._batches = { p.stem: Batch(p) for p in self.batch_directories() }
        self._tasks = { p.stem: Task(self, p) for p in self.task_directories() }

    def __str__(self):
        return f'<{self.__class__.__name__} {self.directory}>'

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
        return [p.name for p in repository.task(task).golds]

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


class Batch:

    def __init__(self, path: Path):
        self.name = path.stem
        self.directory = path
        self.files = []
        with open(path) as fh:
            lines = fh.readlines()
            for line in lines:
                line = line.strip()
                if not line.startswith('#'):
                    self.files.append(line)
            self.content = ''.join(lines)

    def __len__(self):
        return len(self.files)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return f'<{self.__class__.__name__} {self.name} files={len(self)}>'


class Task:

    def __init__ (self, rep: Repository, path: Path):
        self.name = path.name
        self.task_directory = path
        self.gold_directory = Path(path / 'golds')
        self.golds = [f for f in self.gold_directory.iterdir()]
        self.readme_file = Path(path / 'readme.md')
        self.readme = self.readme_content()
        self.process_file = Path(path / 'process.py')
        self.process = self.process_content()
        self.data_drops = {}
        for subdir in self.task_directory.iterdir():
            if subdir.is_dir() and re.match(r'\d{6}', subdir.name):
                self.data_drops[subdir.name] = DataDrop(subdir)

    def __len__(self):
        return len(self.golds)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return f'<{self.__class__.__name__} {self.name} size={len(self)}>'

    def readme_content(self):
        if self.readme_file.is_file():
            with self.readme_file.open() as fh:
                return fh.read()
        return ''

    def process_content(self):
        if self.process_file.is_file():
            with self.process_file.open() as fh:
                return fh.read()
        return ''

    def gold_file_ids(self):
        return [f.stem for f in self.golds]

    def data_drop(self, data_drop: str):
        return self.data_drops.get(data_drop)

    def gold_content(self, gold_file):
        if gold_file is None:
            return ''
        gold_path = Path(self.gold_directory / gold_file)
        with open(gold_path) as fh:
            return fh.read()

    def compare_to_batch(self, batch: Batch):
        gold_files = set(self.gold_file_ids())
        batch_files = set(batch.files)
        return Comparison(
            len(gold_files.intersection(batch_files)),
            len(gold_files.difference(batch_files)),
            len(batch_files.difference(gold_files)))


class DataDrop:

    def __init__(self, path: Path):
        self.name = path.name
        self.path = path
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


class DataDropFile:

    def __init__(self, path):
        pass



repository = Repository(config.ANNOTATIONS)

#repository.pp()