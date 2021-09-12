import docker
import time


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class DockerHandler:

    IMAGE_NAME = '5minds/atlas_engine_fullstack_server'

    def __init__(self, **kwargs):

        params = {
            'base_url': 'unix://var/run/docker.sock',
            'timeout': 120
        }

        self._client = docker.DockerClient(**params)
        self._api_client = docker.APIClient(**params)
        self._name = kwargs.get(
            'container_name', 'robotframework_processcube-engine')
        self._auto_remove = str2bool(kwargs.get('auto_remove', True))
        self._image_name = kwargs.get('image_name', DockerHandler.IMAGE_NAME)

        self._delay = kwargs.get('delay', 5.0)

    def start(self):
        args = {
            'detach': True,
            'publish_all_ports': True,
            'name': self._name,
            'auto_remove': self._auto_remove,
        }

        if self.find_container():
            if self._container.status == 'exited':
                self._container.restart()
        else:
            self._container = self._client.containers.run(
                self._image_name, **args)

        time.sleep(float(self._delay))

        attr = self._api_client.inspect_container(self._container.id)
        key = list(attr['NetworkSettings']['Ports'].keys())[0]

        self._port = attr['NetworkSettings']['Ports'][key][0]['HostPort']

    def get_engine_url(self):
        engine_url = f"http://localhost:{self._port}"

        return engine_url

    def find_container(self):
        containers = self._client.containers.list(
            all=True, filters={'name': self._name})

        if len(containers) > 0:
            self._container = containers[0]
            found = True
        else:
            found = False

        return found

    def shutown(self, prune=False):
        self._container.stop()

        if prune:
            self._client.containers.prune()

    def report(self):
        print(f"container id: {self._container.id}")
        print(f"container attr: {self._port}")


def main():
    handler = DockerHandler(auto_remove=False)

    handler.start()
    handler.report()
    handler.shutown()


if __name__ == '__main__':
    main()
