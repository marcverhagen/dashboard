import os
import config


class AnnotationRepository:

    def __init__(self, directory: str):
        self.directory = directory
        self.annotation_types = {}
        for at in os.listdir(os.path.join(self.directory, 'golds')):
            self.annotation_types[at] = AnnotationTypeRepository(self, at)

    def types(self):
        return list(sorted(self.annotation_types))

    def batches_in_type(self, annotation_type):
        return sorted(self.annotation_types[annotation_type].batches.keys())

    def files_in_batch(self, annotation_type, batch):
        return self.annotation_types[annotation_type].files_in_batch(batch)

    def pp(self):
        for annotation_type in self.annotation_types:
            print(annotation_type)
            at_repository = self.annotation_types[annotation_type]
            for batch in at_repository.batches:
                print(f'    {self.directory}{batch}')
                for fname in at_repository.files_in_batch(batch):
                    print(f'        {fname}')


class AnnotationTypeRepository:

    def __init__ (self, rep: AnnotationRepository, at):
        self.annotation_type = at
        self.directory = os.path.join(rep.directory, 'golds', at)
        self.batches = {}
        for batch in os.listdir(self.directory):
            self.batches[batch] = AnnotationBatch(self, batch)

    def files_in_batch(self, batch):
        return self.batches[batch].files


class AnnotationBatch:

    def __init__(self, repo: AnnotationTypeRepository, batch: str):
        self.batch = batch
        self.directory = os.path.join(repo.directory, batch)
        self.files = [
            [fname, os.path.getsize(os.path.join(self.directory, fname))]
            for fname in os.listdir(os.path.join(self.directory))]


def file_size(directory, project_name, file_name):
    path = os.path.join(directory, project_name, file_name)
    # We could use "f'{os.path.getsize(path):,}'", but then the column will be
    # left aligned, which we may or may not be able to fix with a pandas Styler
    return os.path.getsize(path)


annotations = AnnotationRepository(config.annotations)
