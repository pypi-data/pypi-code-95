# coding: utf-8


import asyncio

from .stream import Stream, StreamState


class _OMMStream(Stream):
    """This class is designed for the open message model (OMM) stream.

    The following are the subscription message from the stream (only the asterisk are now supported)
        - ack message
        - error message*
        - generic message
        - post message
        - refresh message*
        - status message*
        - update message*
        - complete message* (this is a special when the update message has a complete flag)
    """

    def __init__(self, session, api=None):
        Stream.__init__(self, session, api)
        self._name = None
        self._service = None
        self._fields = None
        self._domain = None
        self._key = None
        self._extended_params: dict = {}
        self._with_updates: bool = True
        self._subscribe_future = None

    @property
    def name(self):
        return self._name

    @property
    def protocol_name(self):
        return "OMM"

    ###############################################################
    #   open/close asynchronous functions

    async def _do_open_async(self, **kwargs):
        self._with_updates = kwargs.get("with_updates")

        self._session._register_stream(self)

        result = await self._session.wait_for_streaming(self.api, self.protocol_name)

        if result:
            self._initialize_subscribe_response_future()

            open_message = self._get_open_stream_message()
            self._session.debug(f"open message = {open_message}")
            self._send(open_message)

            await self._wait_for_subscribe_response()

        else:
            self._session.debug(
                f"Start streaming failed. Set stream {self.stream_id} as {self.state}"
            )

        return self.state

    async def _do_close_async(self, **kwargs):
        self._session.debug(f"Close Stream subscription {self.stream_id}")

        send_close_msg = kwargs.get("send_close_msg", True)
        if send_close_msg:
            close_message = {"ID": self.stream_id, "Type": "Close"}
            self._session.debug(f"Sent close subscription:\n {close_message}")
            self._send(close_message)

        self._subscribe_response_future and self._subscribe_response_future.cancel()
        self._session._unregister_stream(self)

    def _do_pause(self):
        # do nothing
        pass

    def _do_resume(self):
        # do nothing
        pass

    ###############################################################
    #    methods to construct a omm item subscription

    def _get_open_stream_message(self):
        open_message = {
            "ID": self.stream_id,
            "Domain": self._domain,
            "Streaming": self._with_updates,
        }

        if self._key:
            open_message["Key"] = self._key
        else:
            open_message["Key"] = {}

        open_message["Key"]["Name"] = self.name

        if self._service:
            open_message["Key"]["Service"] = self._service

        if self._fields:
            open_message["View"] = self._fields

        if self._extended_params is not None:
            open_message = self._update_subscription_message_with_extended_params(
                self._session, open_message, self._extended_params
            )

        return open_message

    def _get_close_stream_message(self):
        """
        Construct and return a close message for this stream
        """

        #   construct a close message
        close_message = {"ID": self.stream_id, "Type": "Close"}

        #   done
        return close_message

    ###############################################################
    #    methods to subscribe/unsubscribe

    async def _subscribe_async(self):
        """
        Subscribe omm stream.
        The subscription steps are waiting for stream to be ready and send the message to subscribe item.
        """
        self._session.log(
            5,
            "_OMMStream.subscribe_async() - waiting for subscribe name = {}".format(
                self.name
            ),
        )

        #   waiting for stream to be ready
        result = await self._session.wait_for_streaming_reconnection(
            self.api, self.protocol_name
        )

        #   check the reconnection result
        if not result:
            # failed to reconnection, so do nothing waiting for next reconnection
            self._session.debug(
                "WARNING!!! the reconnection is failed, so waiting for new reconnection."
            )
            return

        #   send message to subscribe item
        #       construct open message
        open_message = self._get_open_stream_message()
        self._session.log(5, "open message = {}".format(open_message))

        #       send message to stream
        self._send(open_message)

    ###############################################################
    #    callback functions

    def _on_reconnect(
        self, failover_state, stream_state, data_state, state_code, state_text
    ):
        """
        Callback when the websocket connection in stream connection is reconnect
        """
        self._session.debug(
            f"_OMMStream._on_reconnect(failover_state={failover_state}, stream_state={stream_state}, data_state={data_state}, state_code={state_code}, state_text={state_text}))"
        )

        from .stream_connection import StreamConnection

        #   check the failover state for sent the new subscription item
        if failover_state == StreamConnection.FailoverState.FailoverCompleted:
            #   the stream connection failover is completed,
            #       so recover the stream by sent a new subscription item

            #   re-subscribe item
            if self._subscribe_future is None or self._subscribe_future.done():
                self._session.debug(
                    "      call subscribe_async() function.............."
                )

                #   do a subscription again
                self._subscribe_future = asyncio.run_coroutine_threadsafe(
                    self._subscribe_async(), loop=self._loop
                )

        #   do call the on_status callback
        #       build status message
        status_message = {
            "ID": self.stream_id,
            "Type": "Status",
            "Key": {"Name": self.name},
            "State": {
                "Stream": stream_state,
                "Data": data_state,
                "Code": state_code,
                "Text": state_text,
            },
        }

        #       call a status callback message
        self._on_status(status_message)

    ###############################################################
    #   callback functions when received messages

    def _on_refresh(self, message):
        with self._stream_lock:
            if self.is_close:
                self.state = StreamState.Open
                self._session.debug(
                    f"Receive message {message} on stream {self.stream_id} [{self.name}]"
                )
                self._session.debug(f"Set stream {self.stream_id} as {self._state}")

            #   check this refresh is a first refresh of this subscribe item or not
            #       it's possible that it's receiving a refresh message multiple time from server
            if (
                self._subscribe_response_future is not None
                and not self._subscribe_response_future.done()
            ):
                #   this is a first subscribe for this stream, so set the future to be True
                self._subscribe_response_future.set_result(True)

                #   set the stream state to open
                self.state = StreamState.Open

    def _on_update(self, update):
        with self._stream_lock:
            if self._state is StreamState.Open:
                self._session.log(
                    1,
                    f"Stream {self.stream_id} [{self.name}] - Receive update {update}",
                )

    def _on_status(self, status):
        """State : Conveys information about the health of the stream.
        Stream : The state of the event stream when using the request/response with interest paradigm.
            - Closed: Data is not available on this service and connection is not likely to become available,
            though the data might be available on another service or connection.
            - ClosedRecover: State is closed, however data can be recovered on this service and connection at a later time.
            - NonStreaming: The stream is closed and updated data is not delivered without a subsequent re-request.
            - Open: Data is streaming, as data changes it is sent to the stream.
            - Redirected: The current stream is closed and has new identifying information. The user can issue a new request
            for the data using the new message key data from the redirect message.
        """
        with self._stream_lock:
            self._session.log(
                1, f"Stream {self.stream_id} [{self.name}] - Receive status {status}"
            )

            #   check this error of this subscribe item
            #       it's possible that it's receiving a error instead of refresh message from server
            if (
                self._subscribe_response_future is not None
                and not self._subscribe_response_future.done()
            ):
                #   this is a first subscribe for this stream, so set the future to be True
                self._subscribe_response_future.set_result(True)

            #   get / update stream state
            state = status.get("State", None)
            assert state is not None
            stream_state = state.get("Stream", None)

            #   update state
            if stream_state == "Open":
                #   received an open stream
                self.state = StreamState.Open
            elif stream_state == "Closed":
                #   received an closed stream
                from ...delivery.stream import StateManager

                StateManager.close(self, send_close_msg=False)
            else:
                #   unsupported state
                self._session.log(
                    1,
                    f"Stream {self.stream_id} [{self.name}] - Receive unsupported stream state {stream_state}",
                )

    def _on_complete(self):
        with self._stream_lock:
            if self.is_open:
                self._session.debug(
                    f"Stream {self.stream_id} [{self.name}] - Receive complete"
                )

    def _on_error(self, error):
        with self._stream_lock:
            self._session.log(
                1, f"Stream {self.stream_id} [{self.name}] - Receive error {error}"
            )

            #   check this error of this subscribe item
            #       it's possible that it's receiving a error instead of refresh message from server
            if (
                self._subscribe_response_future is not None
                and not self._subscribe_response_future.done()
            ):
                #   this is a first subscribe for this stream, so set the future to be True
                self._subscribe_response_future.set_result(True)
