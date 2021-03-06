from functools import partial, update_wrapper
import inspect

from raiden.api.python import RaidenAPI


def get_channel_events_for_token(app, token_address, start_block=0):
    """ Collect all events from all channels for a given `token_address` and `app` """
    result = list()
    api = RaidenAPI(app.raiden)
    channels = api.get_channel_list(token_address=token_address)
    for channel in channels:
        events = api.get_channel_events(channel.channel_address, start_block)
        result.extend(events)
    return result


class OwnedNettingChannel(object):
    """User end for NettingChannel-Mock implementations, that will fill in 'our_address'
    if and where necessary.
    This allows to use the same method signatures on the outside in all implementations,
    while keeping the simple state sharing implementation of NettingChannelMock.
    """
    def __init__(self, our_address, netting_channel):
        self.netting_channel = netting_channel
        self.our_address = our_address
        for name, value in inspect.getmembers(self.netting_channel):
            # ignore private parts
            if not name.startswith('__'):
                if inspect.ismethod(value):
                    orig_func = getattr(self.netting_channel, name)
                    if 'our_address' in inspect.getargspec(orig_func).args:
                        new_func = partial(orig_func, self.our_address)
                        update_wrapper(new_func, orig_func)
                        setattr(self, name, new_func)
                    else:
                        setattr(self, name, orig_func)
                else:
                    setattr(self, name, value)
