#    Copyright 2021 Qruise project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
from typing import Iterable, Type, TypeVar, Union

import numpy as np
from cuid import cuid
from icecream import ic
import inspect

from ._grpc import qcalibrate_pb2 as pb2
from ._grpc.qcalibrate_pb2_grpc import QCalibrateStub
from ._buffer import QueueBuffer
from ._browser import BrowserPresenter
from ._endpoint import Endpoint, EndpointSecureKey
from ._fom import EvaluateFigureOfMerit, EvaluateFigureOfMeritFactory, Pulse
from ._observer import OptimizationObserver, OptimizationResultCollector


def _is_request_end(request: pb2.Request) -> bool:
    return request.HasField('end')


#:TypeVar("T"): Type variable serving as a parameter for an optimization observer type.
TObserver = TypeVar('TObserver', bound=OptimizationObserver)

OpenBrowserOption = Union[None, bool]

class _OptimizationRunner:

    def __init__(
        self,
        stub: QCalibrateStub,
        experiment_id: str,
        evaluate_fom_factory: EvaluateFigureOfMeritFactory,
        process_timeout: float,
        observers: Iterable[OptimizationObserver]
    ) -> None:

        self._stub = stub
        self._experiment_id = experiment_id
        self._evaluate_fom_factory = evaluate_fom_factory
        self._fom: EvaluateFigureOfMerit = None
        self._process_timeout = process_timeout
        self._buffer = QueueBuffer[pb2.Request](
            is_end=_is_request_end,
            timeout=process_timeout)
        self._configuration: pb2.Initialized = None
        self._session_id = cuid()
        self._observers = observers

    def _send(self, request: pb2.Request) -> None:
        ic()
        ic(request)
        self._buffer.put(request)

    def _create_fom(self, configuration: pb2.Initialized) -> None:
        self._configuration = configuration

        for observer in self._observers:
            observer.on_start(
                run_id=configuration.run_id,
                configuration=configuration,
                parameter_metas=configuration.parameter_metas,
                pulse_metas=configuration.pulse_metas)

        arguments = configuration.arguments
        kvargs = {arg.name: getattr(arg, arg.WhichOneof(
            'value')) for arg in arguments}
        ic(kvargs)
        self._fom = self._evaluate_fom_factory(**kvargs)
        self._send(pb2.Request(start=pb2.Start()))

    def _evaluate_fom(self, parameters: pb2.Parameters) -> None:
        try:
            iteration = parameters.iteration
            merged_parameters = {k.name: v for (k, v) in zip(
                self._configuration.parameter_metas, parameters.values)}
            merged_pulses = {k.name: Pulse(np.array(v.times), np.array(v.values)) for (k, v) in zip(
                self._configuration.pulse_metas, parameters.pulses)}
            fom = self._fom.evaluate(
                parameters=merged_parameters, pulses=merged_pulses)

            for observer in self._observers:
                observer.on_iteration(
                    iteration=iteration,
                    parameters=merged_parameters,
                    pulses=merged_pulses,
                    figure_of_merit=fom.figure_of_merit,
                    data=fom.data)

            self._send(pb2.Request(fom=pb2.Fom(
                iteration=iteration,
                figure_of_merit=fom.figure_of_merit, data=fom.data)))

        except Exception as ex:
            logging.exception(ex)
            self._send(pb2.Request(end=pb2.End(
                typ=ex.__class__.__name__, error=str(ex))))

    def _end(self, typ: str = None, error: str = None):
        self._send(pb2.Request(end=pb2.End(typ=typ, error=error)))

    def run(self):
        ic(self._experiment_id, self._session_id)
        self._buffer.put(pb2.Request(initialize=pb2.Initialize(
            experiment_id=self._experiment_id, session_id=self._session_id)))

        response_stream = self._stub.Run(self._buffer.get())
        self._run_loop(response_stream)

    def _run_loop(self, response_stream: Iterable[pb2.Response]) -> None:
        try:
            ic()
            ic(response_stream)
            response: pb2.Response

            for response in response_stream:
                ic()
                ic(response)
                message = response.WhichOneof('message')
                if message == 'initialized':
                    self._create_fom(response.initialized)
                elif message == 'parameters':
                    self._evaluate_fom(response.parameters)
                elif message == 'end':
                    # signal to producer to close
                    self._buffer.put(None)
                    break
                else:
                    raise Exception(message="Invalid message", arg=message)

            for observer in self._observers:
                observer.on_end()

        except Exception as ex:
            logging.exception(ex)
            # ic()
            # ic(traceback.format_exc(ex))
            self._end(typ=ex.__class__.__name__, error=str(ex))  # end cycle
            for observer in self._observers:
                observer.on_error(exception=ex)
        finally:
            if self._fom:
                self._fom.close()


class QOptimizerClient():
    """Interface to an remote QCalibrate optimizer
    """

    def __init__(self, endpoint: Endpoint, remote_timeout: float = None):
        """Constructs optimization clients

        Parameters
        ----------
        endpoint : Endpoint
            client connection endpoint, creates a communication channel
        process_timeout : float, optional
            Timeout in seconds to wait for a remote reply, by default None - wait forever
        """
        self._browser_presenter = BrowserPresenter.from_endpoint(endpoint)
        self._stub = QCalibrateStub(endpoint.create_channel())
        self._process_timeout = remote_timeout

    def run(
            self,
            experiment_id: str,
            evaluate_fom_class: Union[Type[EvaluateFigureOfMerit], EvaluateFigureOfMeritFactory],
            observer: Union[Type[TObserver],TObserver] = OptimizationResultCollector,
            debug=False,
            show_progress: OpenBrowserOption = False,
    ) -> TObserver:
        """Runs optimization using a remote optimizer, evaluates figure of merit locally use specified class
        class is instatiated with optional argument  specified in the the experiment configuration 

        Parameters
        ----------
        experiment_id : str
            the experiment id, used to configure the optimizer 
        evaluate_fom_class : Union[Type[EvaluateFom], EvaluateFomFactory]
            class to evaluate figure of merit
        observer : OptimizationObserver
            class or object to observe and accumulate optimization results, default :py:class:`OptimizationResultCollector`
        debug : bool, optional
            Enables addition logs, can help debugging the issues, by default False
        show_progress : bool, optional
            Open browser with run details (if running in a notebook), by default False

        Returns
        -------
        TObserver
            The observer object object specified by the 'observer' parameter, by default returns an instance of :py:class:`OptimizationResultCollector`
        """


        if inspect.isclass(observer):
            observer_instance:TObserver = observer()
        else:
            observer_instance:TObserver = observer

        observers = [observer_instance]
        if show_progress and self._browser_presenter:
            observers.append(self._browser_presenter)

        was_enabled = ic.enabled
        if not debug:
            ic.disable()
        try:
            _OptimizationRunner(
                stub=self._stub,
                experiment_id=experiment_id,
                evaluate_fom_factory=evaluate_fom_class,
                process_timeout=self._process_timeout,
                observers=observers,
            ).run()
            return observer_instance
        finally:
            if was_enabled:
                ic.enable()


def create_optimizer_client(
        host: str,
        port: int,
        token: str,
        ca_cert: Union[bytes, str] = None,
        remote_timeout: float = None
) -> QOptimizerClient:
    """Creates remote optimizer client

    Parameters
    ----------
    host : str
        endpoint host
    port : int
        enpoint port
    token : str
        client authentication token
    ca_cert : Union[bytes, str], optional
        server CA certificate file content or certificate file name (.pem)
        used to verify server identity in case it uses a self-signed server certificate
        default None
    process_timeout : float, optional
        Timeout in seconds to wait for a remote reply, by default None - wait forever

    Returns
    -------
    QOptimizerClient
        creates remote optimizer client object
    """
    endpoint = EndpointSecureKey(host=host, port=port, token=token, ca_cert=ca_cert)
    return QOptimizerClient(endpoint=endpoint, remote_timeout=remote_timeout)
