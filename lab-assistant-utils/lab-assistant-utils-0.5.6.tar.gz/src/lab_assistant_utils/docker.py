

class DockerRunOptionsBuilder(object):
    def __init__(self):
        self.options = set()

    def with_gpu(self) -> 'DockerRunOptionsBuilder':
        self.options.add('--gpus all')
        return self

    def with_privileged(self) -> 'DockerRunOptionsBuilder':
        self.options.add('--privileged')
        return self

    def with_add_devices(self) -> 'DockerRunOptionsBuilder':
        self.options.add('-v /dev:/dev')
        self.with_privileged()
        return self

    def with_display(self, display) -> 'DockerRunOptionsBuilder':
        self.options.add(f'-e DISPLAY={display}')
        self.options.add('-e QT_X11_NO_MITSHM=1')
        self.options.add('-v /tmp/.X11-unix:/tmp/.X11-unix:ro')
        return self

    def with_shared_memory(self) -> 'DockerRunOptionsBuilder':
        self.options.add(f'--ipc=host')
        self.with_add_devices()
        return self

    def build(self):
        return ' '.join(self.options)

