import tracardi.service.storage.drivers.elastic.profile
import tracardi.service.storage.drivers.elastic.session
import tracardi.service.storage.drivers.elastic.event
import tracardi.service.storage.drivers.elastic.events
import tracardi.service.storage.drivers.elastic.flow
import tracardi.service.storage.drivers.elastic.rules
import tracardi.service.storage.drivers.elastic.segment
import tracardi.service.storage.drivers.elastic.plugin
import tracardi.service.storage.drivers.elastic.debug_info
import tracardi.service.storage.drivers.elastic.resource


class ElasticDriver:

    @property
    def profile(self):
        return tracardi.service.storage.drivers.elastic.profile

    @property
    def session(self):
        return tracardi.service.storage.drivers.elastic.session

    @property
    def event(self):
        return tracardi.service.storage.drivers.elastic.event

    @property
    def events(self):
        return tracardi.service.storage.drivers.elastic.events

    @property
    def flow(self):
        return tracardi.service.storage.drivers.elastic.flow

    @property
    def rules(self):
        return tracardi.service.storage.drivers.elastic.rules

    @property
    def segment(self):
        return tracardi.service.storage.drivers.elastic.segment

    @property
    def plugin(self):
        return tracardi.service.storage.drivers.elastic.plugin

    @property
    def debug_info(self):
        return tracardi.service.storage.drivers.elastic.debug_info

    @property
    def resource(self):
        return tracardi.service.storage.drivers.elastic.resource
