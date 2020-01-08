from .signals import object_viewed_signal
from stringkeeper.standalone_tools import *

class ObjectViewedMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(ObjectViewedMixin, self).get_context_data(*args, **kwargs)
        request = self.request
        instance = context.get('object')
        context['ascii_art'] = get_ascii_art()
        if instance:
            object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return context