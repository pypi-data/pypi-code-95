import pickle

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.types import PublishOptions
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from twisted.logger import Logger
from twisted.internet.error import ReactorNotRunning


@wamp.error(u"com.hipercam.runtimeerror")
class HipercamRuntimeError(Exception):
    """
    An application specific exception that is decorated with a WAMP URI,
    and hence can be automapped by Autobahn.
    """
    pass


TELEMETRY_DELAY = 2
HEARTBEAT_DELAY = 300


class WrapperComponentMixin(ApplicationSession):
    """
    A mixin class for a WAMP component that wraps others.
    """
    log = Logger()

    def onUserError(self, fail, msg):
        self.log.error(msg)

    @inlineCallbacks
    def onJoin(self, details):

        self.telemetry_topic = 'hipercam.{}.telemetry'.format(self._component_name)

        self.log.info("{} joined WAMP session: realm={}, session={}".format(
            self._component_name, details.realm, details.session
        ))

        def make_pass_through(to_topic):
            def inner(*args):
                self.publish(to_topic, *args)
            return inner

        # pass through topics
        for name in self.model.pass_through_topics:
            topic = 'hipercam.{}.{}'.format(
                self._component_name, name
            )
            to_topic = self.model.pass_through_topics[name]
            yield self.subscribe(make_pass_through(to_topic), topic)
            self.log.info('{} is passing messages on {} to {}'.format(
                self._component_name, topic, to_topic
            ))

        # subscribe to all the telemetry channels
        for channel_id in self.model.subscribed_channels:
            channel = self.model.subscribed_channels[channel_id]
            topic = channel + '.telemetry'
            yield self.subscribe(self.model.on_received_telemetry, topic)
            self.log.info("{} subscribed to topic {}".format(
                self._component_name, topic)
            )

        # install a heartbeat logger
        self._tick_no = 0
        self._tick_loop = LoopingCall(self._tick)
        self._tick_loop.start(HEARTBEAT_DELAY)

        # begin publishing telemetry
        self._telemetry_publisher = LoopingCall(self._publish_telemetry)
        self._telemetry_publisher.start(TELEMETRY_DELAY)
        self.log.info("{} started publishing telemetry on topic {}".format(self._component_name, self.telemetry_topic))

    def _tick(self):
        self._tick_no += 1
        self.log.info('{} is alive [tick {}]'.format(
            self._component_name, self._tick_no))

    @inlineCallbacks
    def _publish_telemetry(self):
        pub_options = PublishOptions(
            acknowledge=True,
            exclude_me=True
        )
        package = pickle.dumps(self.model.telemetry())
        publication = yield self.publish(self.telemetry_topic, package, options=pub_options)
        self.log.debug("Published telemetry to {} with publication ID {}".format(
            self.telemetry_topic, publication.id))

    def onLeave(self, details):
        self.log.info("Session closed: {details}", details=details)
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Connection closed")
        if hasattr(self, '_tick_loop') and self._tick_loop:
            self._tick_loop.stop()
            self._tick_loop = None
        if hasattr(self, '_telemetry_publisher') and self._telemetry_publisher:
            self._telemetry_publisher.stop()
            self._telemetry_publisher = None
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass


class ModelComponentMixin(ApplicationSession):
    """
    A mixin class for a WAMP Component reflecting a single model.

    Telemetry is regularly published, and a tick is published regularly
    to check if the component is alive.

    In addition, the component subscribes to topics for each settable
    attribute of the model, and registers RPC calls for any defined
    methods on the model, and all state transitions of the model.
    """
    log = Logger()

    def onUserError(self, fail, msg):
        self.log.error(msg)

    @inlineCallbacks
    def onJoin(self, details):

        self.telemetry_topic = 'hipercam.{}.telemetry'.format(self._component_name)

        self.log.info("{} joined WAMP session: realm={}, session={}".format(
            self._component_name, details.realm, details.session
        ))

        # start a looping call step state machines on
        # needs to be on a tigher loop than poll times in the machines,
        # of order 1s. Since there are many machines in a model,
        # we work out the loop time here
        nmachines = len(self.model.machines)
        if nmachines > 0:
            loop_time = 0.3/nmachines
            self._machine_loop = LoopingCall(self._forward_step_statemachines)
            self._machine_loop.start(loop_time)

        # add any Looping calls defined in the model
        self._model_looping_calls = []
        if hasattr(self.model, 'extra_looping_calls'):
            for call in self.model.extra_looping_calls:
                interval = self.model.extra_looping_calls[call]
                function = getattr(self.model, call)
                loop = LoopingCall(function)
                self._model_looping_calls.append(loop)
                loop.start(interval)

        # register all triggers of state transistions as RPC callbacks
        def make_trigger(machine, event):
            # use this factory function to avoid statemachine
            # being returned from trigger (it cannot be pickled)
            def f(**event_parameters):
                allowed_events = machine.statechart.events_for(machine.configuration)
                if event not in allowed_events:
                    raise HipercamRuntimeError('unsupported state transition on {}\n{} not in {}'.format(
                                        self._component_name, event, ",".join(allowed_events)
                                    ))
                machine.queue(event, **event_parameters)
            return f

        for machine_name in self.model.machines:
            self.log.info('registering state transition triggers')
            machine = self.model.machines[machine_name]
            events = machine.statechart.events_for()
            self.log.info('registering {} for {}'.format(events, machine_name))
            for event in events:
                rpc_name = 'hipercam.{}.rpc.{}.{}'.format(
                    self._component_name, machine_name, event
                )
                trigger = make_trigger(machine, event)
                yield self.register(trigger, rpc_name)
                self.log.info("{} registered procedure {}".format(self._component_name, rpc_name))

        # add additional RPC calls
        for method_name in self.model.extra_rpc_calls:
            trigger_function = getattr(self.model, method_name)
            rpc_name = 'hipercam.{}.rpc.{}'.format(
                self._component_name, method_name
            )
            yield self.register(trigger_function, rpc_name)
            self.log.info("{} registered procedure {}".format(self._component_name, rpc_name))

        # subscribe to channels corresponding to settable attributes

        # needs a factory function because of scopes
        # see https://eev.ee/blog/2011/04/24/gotcha-python-scoping-closures/
        def make_setter(attr):
            def setter(val):
                setattr(self.model, attr, val)
            return setter

        for i in range(len(self.model.settable_attributes)):
            # declared inside loop so it has proper scope for capture in callback
            attr = str(self.model.settable_attributes[i])
            topic = 'hipercam.{}.{}'.format(
                self._component_name, attr
            )
            yield self.subscribe(make_setter(attr), topic)
            self.log.info("{} registered settable attribute {} on topic {}".format(self._component_name, attr, topic))

        # install a heartbeat logger
        self._tick_no = 0
        self._tick_loop = LoopingCall(self._tick)
        self._tick_loop.start(HEARTBEAT_DELAY)

        # begin publishing telemetry
        self._telemetry_publisher = LoopingCall(self._publish_telemetry)
        self._telemetry_publisher.start(TELEMETRY_DELAY)
        self.log.info("{} started publishing telemetry on topic {}".format(self._component_name, self.telemetry_topic))

    def _forward_step_statemachines(self):
        """
        Step each state machine in the model forward.

        Needs to be on a tight control loop, because if this loops
        slower than poll times in the state machines, unusual
        behaviour can occur.

        This is because we want bound state changes between, e.g
        connection handlers and sensors, to propagate faster than
        the poll time, so devices don't try to poll a closed connection

        Each model can have many machines, and the fastest poll times
        are of order 1 second
        """
        for machine_name in self.model.machines:
            machine = self.model.machines[machine_name]
            machine.execute()

    def _tick(self):
        self._tick_no += 1
        self.log.info('{} is alive [tick {}]'.format(
            self._component_name, self._tick_no))

    @inlineCallbacks
    def _publish_telemetry(self):
        pub_options = PublishOptions(
            acknowledge=True,
            exclude_me=True
        )
        package = pickle.dumps(self.model.telemetry())
        publication = yield self.publish(self.telemetry_topic, package, options=pub_options)
        self.log.debug("Published telemetry to {} with publication ID {}".format(
            self.telemetry_topic, publication.id))

    def onLeave(self, details):
        self.log.info("Session closed: {details}", details=details)
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Connection closed")
        if hasattr(self, '_model_looping_calls') and self._model_looping_calls:
            for call in self._model_looping_calls:
                call.stop()
            self._model_looping_calls = None
        if hasattr(self, '_tick_loop') and self._tick_loop:
            self._tick_loop.stop()
            self._tick_loop = None
        if hasattr(self, '_telemetry_publisher') and self._telemetry_publisher:
            self._telemetry_publisher.stop()
            self._telemetry_publisher = None
        if hasattr(self, '_machine_loop') and self._machine_loop:
            self._machine_loop.stop()
            self._machine_loop = None
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass
