from typing import List

class PaperContent():
    """Conveninent helper to write papers from the python-client.

    Usage
    --------------

    paper = PaperContent()
    paper.add('# Title')
    paper.add('## Subtitle')
    paper.add('Hello world')
    
    # Add image
    img_uid = run.add_artifact(path, wait_response=True)['uuid']
    paper.img(img_uid)
    
    # Push data
    paper.update_run_paper(run)

    """        
    def __init__(self):
        self.text = ''
    
    def add(self, text: str):
        self.text += text + '\n'
    
    def new_line(self):
        self.text += '\n'
        
    def img(self, uid: str):
        self.text += f'\n__ARTIFACT__[{uid}]\n\n'
        
    def imgs(self, uids: List[str]):
        self.text += '\n'
        for uid in uids:
            self.text += f'__ARTIFACT__[{uid}]\n'
        self.text += '\n'
    
    def hrule(self):
        self.text += '-------------------------------\n'
    
    def update_run_paper(self, run: 'Run'):
        run.set_paper(self.text)

    def __str__(self):
        return self.text
    
    def __repr__(self):
        return self.text