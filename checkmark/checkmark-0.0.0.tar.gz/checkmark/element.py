

class HTMLElement:
    def __init__(self, tag, content=None, *args, **kwargs):
        self.tag = tag
        self.content = content or []
        self.args = args
        self.kwargs = kwargs

        if not isinstance(self.content, list):
            self.content = [self.content]
        
    def __str__(self):
        """Render element into HTML"""
        content = '\n'.join(map(str, self.content))

        if content:
            content = f'\n{content}\n'

        args = ' '.join(map(str, self.args))

        kwargs = ' '.join([
            f'{key}={value!r}'
            for key, value in self.kwargs.items()
        ])

        return f'<{self.tag} {args} {kwargs}>{content}</{self.tag}>'