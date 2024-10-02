"""

Export the annotation and evaluation repositories as a set of markdown pages.

$ python export.py 
$ python export.py --debug

"""

import io
import os
import sys
import pathlib

import config
import model
from utils import identity


DEBUG = False


MODEL = model.Data(config.ANNOTATIONS, config.EVALUATIONS)
ANNOTATIONS = MODEL.annotations
EVALUATIONS = MODEL.evaluations


ANNOTATIONS_REPO_URL = 'https://github.com/clamsproject/aapb-annotations'
EVALUATIONS_REPO_URL = 'https://github.com/clamsproject/aapb-evaluations'
DASHBOARD_REPO_URL = 'https://github.com/clamsproject/dashboard'


# Top-level directory structure
ANNOTATIONS_DIR = 'annotations'
TASKS_DIR = 'annotations/tasks'
BATCHES_DIR = 'annotations/batches'
EVALUATIONS_DIR = 'evaluations'


# Navigation structure. This contains mappings from pages in directories to pages
# higher up in the hierarchy.
NAVIGATION = {
    'BREADCRUMBS': {
        'annotations/tasks/task':
            [('Dashboard', '../../../index.md'),
             ('Annotations', '../../index.md'),
             ('Tasks', '../index.md')],
        'annotations/tasks/task/drops':
            [('Dashboard', '../../../../index.md'),
             ('Annotations', '../../../index.md'),
             ('Tasks', '../../index.md'),
             ('Task', '../index.md')],
        'annotations/tasks/task/drops/drop':
            [('Dashboard', '../../../../index.md'),
             ('Annotations', '../../../index.md'),
             ('Tasks', '../../index.md'),
             ('Task', '../index.md'),
             ('Data drops', 'index.md')],
        'annotations/batches':
            None,
        'annotations/batches/batch':
            [('Dashboard', '../../../index.md'),
             ('Annotations', '../../index.md'),
             ('Batches', '../index.md')],
    },
    'SUBPAGES': {
        'annotations/tasks/task':
            [('task', 'index.md'), ('readme', 'readme.md'),
             ('gold files', 'golds.md'), ('data drops', 'drops/index.md'),
             ('batches', 'batches.md'), ('script', 'script.md')],
        'annotations/tasks/task/drops':
            [('data drops', 'index.md')],
        'annotations/tasks/task/drops/drop':
            [('data drop', None)],
        'annotations/batches': None,
        'annotations/batches/batch': None
    }
}


def breadcrumbs(path: str):
    return NAVIGATION['BREADCRUMBS'].get(path)


def subpages(path: str, current_page: str):
    pages = NAVIGATION['SUBPAGES'].get(path)
    adjusted_pages = []
    for page, link in pages:
        if page == current_page:
            adjusted_pages.append((f'**{page}**', None))
        else:
            adjusted_pages.append((page, link))
    return adjusted_pages



def debug(text: str):
    if DEBUG:
        print(f'DEBUG: {text}')



class SiteBuilder():

    def __init__(self, directory: str):
        self.path = pathlib.Path(directory)
        self.commit_sha = ANNOTATIONS.repo.head.commit.hexsha
        self.commit_short_sha = ANNOTATIONS.repo.git.rev_parse(self.commit_sha, short=8)

    def build(self):
        self.create_directories()
        self.index()
        self.annotations()
        self.evaluations()

    def create_directories(self):
        dirs = [ANNOTATIONS_DIR, TASKS_DIR, BATCHES_DIR, EVALUATIONS_DIR]
        for batch in ANNOTATIONS.batches:
            dirs.append(os.path.join(BATCHES_DIR, batch.stem))
        for task in ANNOTATIONS.tasks:
            dirs.append(os.path.join(TASKS_DIR, task.name))
            dirs.append(os.path.join(TASKS_DIR, task.name, 'drops'))
        for directory in dirs:
            full_path = self.path / directory
            full_path.mkdir(parents=True, exist_ok=True)

    def index(self):
        # Building /index.md
        path = self.path / 'index.md'
        with PageBuilder(path) as pb:
            pb.header('CLAMS Viewers')
            pb.p('CLAMS Viewers for browsing annotations and evaluations.')
            pb.p('The homepages for the repositories are available at')
            pb.write(f'- 🏠 [{ANNOTATIONS_REPO_URL}]({ANNOTATIONS_REPO_URL})\n')
            pb.write(f'- 🏠 [{EVALUATIONS_REPO_URL}]({EVALUATIONS_REPO_URL})\n\n')
            pb.p('The code for this dashboard is maintained at'
                 f' [{DASHBOARD_REPO_URL}]({DASHBOARD_REPO_URL})')
            pb.write('- 🕵️‍♀️ [Annotation Viewer](annotations/index.md)\n\n')
            pb.write('- 🕵️‍♀️ [Evaluation Viewer](evaluations/index.md)\n\n')

    def annotations(self):
        # Building /annotations/
        self.annotations_index()
        self.annotations_readme()
        self.annotations_tasks()
        self.annotations_batches()

    def annotations_index(self):
        # Building /annotations/index.md
        path = self.path / 'annotations' / 'index.md'
        with PageBuilder(path) as pb:
            pb.header('Annotation Viewer')
            pb.debug(f'annotations_index()\n{path}')
            pb.navigation(
                [('Dashboard Home', '../index.md'), ('Annotation Viewer', None)],
                [('Repository Readme', 'readme.md'),
                 ('Tasks', 'tasks/index.md'), ('Batches', 'batches/index.md')])
            pb.write(
                'The Annotation Viewer gives a user-friendly peek into the GitHub '
                'repository with all the annotations. You can see the repository\'s '
                'readme file and inspect annotation tasks and annotation batches.')

    def annotations_readme(self):
        # Building /annotations/readme.md
        path = self.path / 'annotations' / 'readme.md'
        with PageBuilder(path) as pb:
            pb.header('Annotation Viewer', 'Repository Readme File')
            pb.debug(f'annotations_readme()\n{path}')
            pb.navigation(
                [('Dashboard Home', '../index.md'), ('Annotation Viewer', 'index.md')],
                [('Repository Readme', None),
                 ('Tasks', 'tasks/index.md'), ('Batches', 'batches/index.md')])
            pb.write(ANNOTATIONS.readme)

    def annotations_tasks(self):
        # Building /annotations/tasks/index.md
        # Building /annotations/tasks/{task.name}/
        path = self.path / 'annotations' / 'tasks' / 'index.md'
        with PageBuilder(path) as pb:
            pb.header('Annotation Viewer', 'Tasks')
            pb.debug('annotations_tasks()')
            pb.navigation(
                [('Dashboard Home', '../../index.md'),
                 ('Annotation Viewer', '../index.md')],
                [('Repository Readme', '../readme.md'),
                 ('Tasks', None),
                 ('Batches', '../batches/index.md')])
            pb.p(f'Annotation tasks with number of gold files in each task:')
            pb.table_header('task', 'size', align="lr")
            for task in ANNOTATIONS.tasks:
                pb.table_row([f'[{task.name}]({task.name}/index.md)', len(task)])
                self.annotations_task(task)

    def annotations_task(self, task):
        # Building /annotations/tasks/{task.name}/
        path = self.path / 'annotations' / 'tasks' / task.name
        self.annotations_task_index(path / 'index.md', task)
        self.annotations_task_readme(path / 'readme.md', task)
        self.annotations_task_gold(path / 'golds.md', task)
        self.annotations_task_drops(path / 'drops', task, task.data_drops)
        self.annotations_task_batches(path / 'batches.md', task)
        self.annotations_task_script(path / 'script.md', task)

    def annotations_task_index(self, path, task):
        # Building /annotations/tasks/{task.name}/index.md
        with PageBuilder(path) as pb:
            pb.header('Annotation Task', task.name)
            pb.debug(f'annotations_task_index()')
            pb.navigation(
                breadcrumbs('annotations/tasks/task'),
                subpages('annotations/tasks/task', 'task'))
            pb.p(
                f'Task {task.name} has {len(task.data_drops)} data drops'
                f' and {len(task)} gold files.')

    def annotations_task_readme(self, path, task):
        # Building /annotations/tasks/{task.name}/readme.md
        with PageBuilder(path) as pb:
            pb.header('Annotation Task', task.name, 'Readme')
            pb.debug(f'annotations_task_readme()')
            pb.navigation(
                breadcrumbs('annotations/tasks/task'),
                subpages('annotations/tasks/task', 'readme'))
            # NOTE: if we just give a link to the README at GitHub we can use
            # /tree/{self.commit_sha}/{task.name}/readme.md
            pb.write(task.readme)

    def annotations_task_gold(self, path, task):
        # Building /annotations/tasks/{task.name}/golds.md
        with PageBuilder(path) as pb:
            pb.header('Annotation Task', task.name, 'Gold files')
            pb.debug(f'annotations_task_gold()')
            pb.navigation(
                breadcrumbs('annotations/tasks/task'),
                subpages('annotations/tasks/task', 'gold files'))
            pb.subheader('Gold standard files in this task.')
            pb.p(f'Total number of files is {len(task.gold_files)},'
                 ' this includes files from all data drops. Clicking'
                 ' a link takes you to the data file in the repository.')
            url = f'{ANNOTATIONS_REPO_URL}/tree/{self.commit_sha}/{task.name}/golds'
            for gf in task.gold_files:
                pb.write(f'1. [{gf.name}]({url}/{gf.name})\n')

    def annotations_task_drops(self, path, task, drops: dict):
        # Building /annotations/tasks/{task.name}/drops/index.md
        # Building /annotations/tasks/{task.name}/drops/{datadrop.name}.md
        index_path = path / 'index.md'
        with PageBuilder(index_path) as pb:
            pb.header('Annotation Task', task.name, 'Data drops')
            pb.debug(f'annotations_task_drops()')
            pb.navigation(
                breadcrumbs('annotations/tasks/task/drops'),
                subpages('annotations/tasks/task/drops', 'data drops'))
            pb.p(f'Data drops for task **{task.name}** with size in number of files.')
            pb.table_header('data drop name', 'size', align='lr')
            for dd in task.data_drops.values():
                pb.table_row([f'[{dd.name}]({dd.name}.md)', len(dd)])
                self.annotations_task_drop_index(path, task, dd)

    def annotations_task_drop_index(self, path, task, datadrop):
        # Building /annotations/tasks/{task.name}/drops/{datadrop.name}.md
        index_path = path / f'{datadrop.stem}.md'
        with PageBuilder(index_path) as pb:
            pb.header('Data Drop', datadrop.name)
            pb.navigation(
                breadcrumbs('annotations/tasks/task/drops/drop'),
                subpages('annotations/tasks/task/drops/drop', 'data drop'))
            pb.p(f'Files in data drop **{datadrop.name}**,'
                 + f' with links to sources on the GitHub repository.')
            tree_url = f'{ANNOTATIONS_REPO_URL}/tree/{self.commit_sha}'
            for fname in sorted(datadrop.file_names):
                file_url = f'{tree_url}/{task.name}/{datadrop.name}/{fname}'
                pb.write(f'1. [{fname}]({file_url})\n')

    def annotations_task_batches(self, path, task):
        with PageBuilder(path) as pb:
            pb.header('Annotation Task', task.name, 'Batches')
            pb.debug(f'annotations_task_batches()')
            pb.navigation(
                breadcrumbs('annotations/tasks/task'),
                subpages('annotations/tasks/task', 'batches'))
            pb.p('GUIDs from annotation batches that were used in this task:')
            pb.table_header('batch', 'guids', 'batch size', align='llr')
            for batch in ANNOTATIONS.batches:
                comp = task.compare_to_batch(batch)
                batch_link = f'[{batch.stem}](../../batches/{batch.stem}/index.md)'
                pb.table_row([batch_link, comp.in_both, len(batch)])

    def annotations_task_script(self, path, task):
        with PageBuilder(path) as pb:
            pb.header('Annotation Task', task.name, 'Script')
            pb.debug(f'annotations_task_script()')
            pb.navigation(
                breadcrumbs('annotations/tasks/task'),
                subpages('annotations/tasks/task', 'script'))
            pb.code(task.process_content())

    def annotations_batches(self):
        batches_path = self.path / 'annotations' / 'batches'
        batches_index_path = batches_path / 'index.md'
        with PageBuilder(batches_index_path) as pb:
            pb.header('Annotation Viewer', 'Batches')
            pb.debug(f'annotation_batches()\n{batches_index_path}')
            pb.navigation(
                [('Dashboard Home', '../../index.md'),
                 ('Annotation Viewer', '../index.md')],
                [('Repository Readme', '../readme.md'),
                 ('Tasks', '../tasks/index.md'), ('Batches', None)])
            pb.p(f'Annotation batches with number of files in each batch:')
            pb.table_header('batch', 'size', align='lr')
            for batch in ANNOTATIONS.batches:
                pb.table_row([f'[{batch.stem}]({batch.stem}/index.md)', len(batch)])
                self.annotations_batch(batch)

    def annotations_batch(self, batch):
        batch_path = self.path / 'annotations' / 'batches' / batch.stem
        batch_index_path = batch_path / 'index.md'
        batch_files_path = batch_path / 'files.md'
        batch_content_path = batch_path / 'content.md'
        batch_tasks_path = batch_path / 'tasks.md'
        batch_evaluation_path = batch_path / 'evaluation.md'
        self.annotations_batch_index(batch_index_path, batch)
        self.annotations_batch_files(batch_files_path, batch)
        self.annotations_batch_content(batch_content_path, batch)
        self.annotations_batch_tasks(batch_tasks_path, batch)
        self.annotations_batch_evaluation(batch_evaluation_path, batch)

    def annotations_batch_breadcrumbs(self):
        return breadcrumbs('annotations/batches/batch')

    def annotations_batch_pages(self, current_page: str = ''):
        """Returns the pages of the annotation batch."""
        pages = [('batch', 'index.md'),
                 ('files', 'files.md'), ('content', 'content.md'),
                 ('tasks', 'tasks.md'), ('use in evaluation', 'evaluation.md')]
        adjusted_pages = []
        for page, link in pages:
            if page == current_page:
                adjusted_pages.append((f'**{page}**', None))
            else:
                adjusted_pages.append((page, link))
        return adjusted_pages

    def annotations_batch_index(self, path, batch):
        with PageBuilder(path) as pb:
            pb.header('Annotation Batch', batch.stem)
            pb.debug(f'annotations_batch_index()\n{path}')
            pb.navigation(
                self.annotations_batch_breadcrumbs(),
                self.annotations_batch_pages('batch'))
            pb.p(f'Batch **{batch.stem}** has {len(batch.files)} files.')
            pb.subheader(f'Batch comment')
            pb.write(batch.comment)

    def annotations_batch_files(self, path, batch):
        with PageBuilder(path) as pb:
            pb.header('Annotation Batch', batch.stem)
            pb.debug(f'annotations_batch_files()\n{path}')
            pb.navigation(
                self.annotations_batch_breadcrumbs(),
                self.annotations_batch_pages('files'))
            pb.subheader('File identifiers in batch')
            for fileid in batch.files:
                pb.write(f'1. {fileid}\n')
 
    def annotations_batch_content(self, path, batch):
        with PageBuilder(path) as pb:
            pb.header('Annotation Batch', batch.stem)
            pb.debug(f'annotations_batch_content()\n{path}')
            pb.navigation(
                self.annotations_batch_breadcrumbs(),
                self.annotations_batch_pages('content'))
            pb.subheader('Batch file content')
            pb.write(f'<pre>\n{batch.content.strip()}\n</pre>\n\n')
 
    def annotations_batch_tasks(self, path, batch):
        with PageBuilder(path) as pb:
            pb.header('Annotation Batch', batch.stem)
            pb.debug(f'annotations_batch_tasks()\n{path}')
            pb.navigation(
                self.annotations_batch_breadcrumbs(),
                self.annotations_batch_pages('tasks'))
            pb.subheader('Batch usage by annotation task')
            pb.p('This shows how many GUIDs from this batch were used in annotation tasks.')
            pb.table_header('task name', 'overlap', 'task size', align='lrr')
            for task in ANNOTATIONS.tasks:
                comparison = task.compare_to_batch(batch)
                pb.table_row([task.name, comparison.in_both, len(task)])

    def annotations_batch_evaluation(self, path, batch):
        with PageBuilder(path) as pb:
            pb.header('Annotation Batch', batch.stem)
            pb.debug(f'annotations_batch_evaluation()\n{path}')
            pb.navigation(
                self.annotations_batch_breadcrumbs(),
                self.annotations_batch_pages('use in evaluation'))
            pb.subheader('Batch usage in evaluation repository')
            batch_usage1 = MODEL.batch_usage_in_system_predictions(batch.stem)
            batch_usage2 = MODEL.batch_usage_in_system_reports(batch.stem)
            pb.p('Usage in system predictions:')
            if batch_usage1:
                pb.table_header('evaluation', 'system prediction')
                pb.table_rows(batch_usage1)
            else:
                pb.write('*None*\n\n')
            pb.p('Usage in system reports:')
            if batch_usage2:
                pb.table_header('evaluation', 'system report')
                pb.table_rows(batch_usage2)
            else:
                pb.write('*None*\n\n')

    def evaluations(self):
        with PageBuilder(self.path / 'evaluations' / 'index.md') as pb:
            pb.header('CLAMS Evaluation Viewer')
            pb.navigation(
                [('Dashboard Home', '../index.md'), ('Evaluation Viewer', None)])


class PageBuilder:

    def __init__(self, path: pathlib.Path):
        self.path = path
        self._debug = DEBUG

    def __enter__(self):
        self.fh = self.path.open('w')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            print(exc_type, exc_value, exc_tb)
        self.fh.close()

    def __str__(self):
        return f'<PageBuilder debug={self._debug}>'

    def debug(self, text: str):
        if self._debug:
            self.fh.write(f'<pre>{text}</pre>\n\n')

    def write(self, text: str):
        self.fh.write(text)

    def header(self, *components: list):
        sep = ' &nbsp; ⎯ &nbsp; '
        self.fh.write(f'# {sep.join(components)}\n\n')

    def subheader(self, text: str):
        self.fh.write(f'#### {text}\n\n')

    def navigation(self, breadcrumbs: list, pages: list = None):
        """Adds the markdown for a navigation bar, including the breadcrumbs, the
        sub pages if any, and a horizontal rule as a separator."""
        for n, (name, link) in enumerate(breadcrumbs):
            prefix = '' if n == 0 else ' &nbsp; > &nbsp; '
            if link is None:
                self.fh.write(f'{prefix}**{name}** ')
            else:
                self.fh.write(f'{prefix}[{name}]({link}) ')
        if pages:
            self.fh.write(' &nbsp; > &nbsp; ')
            for n, (name, link) in enumerate(pages):
                prefix = '\[ ' if n == 0 else '| '
                if link is None:
                    if not name.startswith('**'):
                        name = f'**{name}**'
                    self.fh.write(f'{prefix}{name} ')
                else:
                    self.fh.write(f'{prefix}[{name}]({link}) ')
            self.fh.write('\]')
        self.fh.write('\n\n---\n\n')

    def p(self, text: str):
        self.fh.write(f'{text}\n\n')

    def hr(self):
        self.fh.write(f'---\n\n')

    def table_header(self, *headers, align=None):
        if align is None:
            align = 'l' * len(headers)
        # TODO: now just allows 'l' and 'r', may need 'c' as well
        header_strings = []
        header_aligns = []
        for (h, a) in zip(headers, align):
            header_strings.append(h)
            header_align = ':------' if a == 'l' else '------:'
            header_aligns.append(header_align)
        self.fh.write(f'| {" | ".join(header_strings)} |\n')
        self.fh.write(f'| {" | ".join(header_aligns)} |\n')

    def table_rows(self, rows: list):
        for row in rows:
            self.table_row(row)

    def table_row(self, row: list):
        row = [str(element) for element in row]
        self.fh.write(f'| {" | ". join(row)} |\n')

    def code(self, text: str, language='python'):
        self.fh.write(f'```{language}\n')
        self.fh.write(text)
        self.fh.write('\n```\n')




if __name__ == '__main__':

    if '--debug' in sys.argv:
        DEBUG = True
    builder = SiteBuilder('../docs/www')
    builder.build()
    #print(builder.commit_sha, builder.commit_short_sha)


'''

🕵️‍♀️

🌍 🌎 🌏

👁

'''

