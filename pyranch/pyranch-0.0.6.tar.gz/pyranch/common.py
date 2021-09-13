import json

from . import RequestError


class CattleObject(object):
    object_url = None

    def __call__(self):
        print(json.dumps(self.__dict__, indent=4))

    def find_by_name(self):
        cattle_objects = self.env.request(self.object_url, 'GET')
        return next((cattle_object for cattle_object in cattle_objects['data'] if cattle_object['name'] == self.name),
                    {})

    def all(self, params=None):
        response = self.env.request(self.object_url, 'GET', params=params)
        return response.get('data')

    def delete(self):
        return self.env.request(self.object_url, 'DELETE')

    def action(self, action, data=None):
        if not self.id:
            raise RequestError
        return self.env.request('{}/{}'.format(self.object_url, self.id), 'POST', params={'action': action},
                                        data=data)
