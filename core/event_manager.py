from utils.singleton_decorator import singleton
from typing import Callable, Any
from collections import defaultdict
from utils.debug import debug

import sys
import sdl2 as sdl
import ctypes

from core.event_system.user_events import UserEvents, Payload, UserEventInstance
from core.event_system.event_queue import EventQueue


class SubscriptionData:
    def __init__(
        self,
        callback,
        args,
        kwargs,
        parameters,
    ):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.parameters = parameters

    def __repr__(self):
        return f"{self.callback}, {self.args}, {self.kwargs}, {self.parameters};"


@singleton
class EventManager:

    def __init__(self):
        self.subscriptions = defaultdict(list)

    def subscribe(
        self,
        event_type: Any,
        callback: Callable[[Any], None],
        *args: Any,
        **kwargs: Any,
    ):
        # -- setting subscription parameters
        parameters = {"pass_event": False, "progenitor": None}
        for name in parameters.keys():
            if name in kwargs:
                parameters[name] = kwargs[name]
                del kwargs[name]

        # -- appending a subscription to the list of subscriptions for a specific event
        self.subscriptions[event_type].append(
            SubscriptionData(
                callback=callback,
                args=args,
                kwargs=kwargs,
                parameters=parameters,
            )
        )

        debug.log(f"subscribed callback to {event_type}")

    def unsubscribe(self, event_type: Any, callback: Callable):
        if event_type in self.subscriptions:
            original_subscriptions = self.subscriptions[event_type][:]
            for sub_data in original_subscriptions:
                if sub_data.callback == callback:
                    self.subscriptions[event_type].remove(sub_data)
                    debug.log(f"unsubscribed callback from {event_type}")
                    return
            raise RuntimeError(f"(!) callback not found for {event_type}")
        else:
            raise RuntimeError(f"(!) event_type {event_type} not found in subscriptions")

    def emit(self, event: Any):
        payload = UserEvents.get_payload(event)
        if event.type in self.subscriptions:
            for sub_data in self.subscriptions[event.type]:
                try:
                    progenitor = sub_data.parameters["progenitor"]
                    subscription_has_progenitor = progenitor is not None
                    payload_has_progenitor = hasattr(payload, "progenitor")

                    # -- exiting if either the subscription or the payload are missing progenitor parameters
                    # -- (but not both, that would be a regular global event)
                    if subscription_has_progenitor and not payload_has_progenitor:
                        raise RuntimeError(
                            f"""(!) payload for a progenitor-specific event does not have a "progenitor" field"""
                        )
                    if not subscription_has_progenitor and payload_has_progenitor:
                        raise RuntimeError(
                            f"""(!) subscription for a progenitor-specific event does not have a "progenitor" parameter"""
                        )

                    # -- handling the progenitor-specific event if both parameters are specified
                    if subscription_has_progenitor and payload_has_progenitor:
                        if progenitor != payload.progenitor:
                            continue  # -- the subscription and event instance progenitors do not match

                    # -- calling the function specified in the callback
                    if sub_data.parameters["pass_event"] is True:
                        sub_data.callback(
                            event if payload is None else payload,
                            *sub_data.args,
                            **sub_data.kwargs,
                        )
                    else:
                        sub_data.callback(
                            *sub_data.args,
                            **sub_data.kwargs,
                        )
                except Exception as e:
                    raise RuntimeError(
                        f"(!) error in callback for {event}, {sub_data.callback}: {str(e)}"
                    )

    def get_parameter(self, event_type, callback, parameter_name):
        return getattr(self.subscriptions[event_type].parameters, parameter_name)

    def process_events(self):
        # for key, l in self.subscriptions.items():
        #    print(f"{key}:")
        #    for entry in l:
        #        if hasattr(entry.callback.__self__, "parent_obj"):
        #            print(entry.callback, entry.callback.__self__.parent_obj, entry.parameters)
        UserEvents.get_instance("update").post()
        for event in EventQueue.poll_events():
            if event.type == sdl.SDL_QUIT:
                sys.exit()
            self.emit(event)
