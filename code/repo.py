import os
import config


class AnnotationRepository:

    def __init__(self, directory: str):
        self.directory = directory
        gold_directories = os.listdir(os.path.join(self.directory, 'golds'))
        self.categories = { cat: AnnotationTypeRepository(self, cat)
                            for cat in gold_directories }

    def category_names(self):
        return list(sorted(self.categories))

    def types_with_batches_count(self):
        return [[cat, config.DESCRIPTIONS.get(cat, ''), len(self.batch_names(cat))]
                for cat in self.category_names()]

    def category(self, category: str):
        return self.categories[category]

    def batch(self, category, name):
        return self.categories[category].batches[name]

    def batch_names(self, category):
        return sorted(self.categories[category].batches.keys())

    def files_in_batch(self, annotation_type, batch):
        return self.categories[annotation_type].files_in_batch(batch)

    def pp(self):
        for annotation_type in self.categories:
            print(annotation_type)
            at_repository = self.categories[annotation_type]
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

    def __init__(self, repo: AnnotationTypeRepository, name: str):
        self.name = name
        self.directory = os.path.join(repo.directory, name)
        self.annotations_dir = os.path.join(repo.directory, name, 'annotations')
        self.files = [
            [fname, os.path.getsize(os.path.join(self.annotations_dir, fname))]
            for fname in os.listdir(os.path.join(self.annotations_dir))]

    def short_description(self):
        return self.get_description('description.txt')

    def long_description(self):
        description = self.get_description('description.md')
        return self.get_description('description.txt') if not description else description

    def get_description(self, file_name: str):
        path = os.path.join(self.directory, file_name)
        return open(path).read() if os.path.exists(path) else ''


def file_size(directory, project_name, file_name):
    path = os.path.join(directory, project_name, file_name)
    # We could use "f'{os.path.getsize(path):,}'", but then the column will be
    # left aligned, which we may or may not be able to fix with a pandas Styler
    return os.path.getsize(path)


annotations = AnnotationRepository(config.annotations)
