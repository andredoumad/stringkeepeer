from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication

from stringkeeper import settings
from core.serializers import MessageModelSerializer, UserModelSerializer
from core.models import MessageModel

from django.contrib.auth import get_user_model

from stringkeeper.standalone_tools import *

User = get_user_model()

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """
    eventlog('CsrfExemptSessionAuthentication')
    def enforce_csrf(self, request):
        return


class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    eventlog('MessagePagination')
    page_size = settings.MESSAGES_TO_LOAD


class MessageModelViewSet(ModelViewSet):
    eventlog('MessageModelViewSet')
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    eventlog('serializer_class: ' + str(serializer_class))
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)
    pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        eventlog('MessageModelViewSet list')
        self.queryset = self.queryset.filter(Q(recipient=request.user) |
                                             Q(user=request.user))
        eventlog('MessageModelViewSet self.queryset: ' + str(self.queryset))
        target = self.request.query_params.get('target', None)
        eventlog('MessageModelViewSet target: ' + str(target))
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__email=target) |
                Q(recipient__email=target, user=request.user))
            eventlog('MessageModelViewSet self.queryset: ' + str(self.queryset))
        return super(MessageModelViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        eventlog('MessageModelViewSet retrieve')
        msg = get_object_or_404(
            self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk'])))
        eventlog('msg = get_object_or_404: ' + str(msg))
        debug_query = self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk']))
        eventlog('debug_query: ' + str(debug_query))
        serializer = self.get_serializer(msg)
        return Response(serializer.data)


class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all user
    eventlog('UserModelViewSet')
    def list(self, request, *args, **kwargs):
        # Get all users except yourself
        eventlog('UserModelViewSet list' + str(self.queryset))
        self.queryset = self.queryset.exclude(id=request.user.id)
        eventlog('self.queryset ' + str(self.queryset))
        return super(UserModelViewSet, self).list(request, *args, **kwargs)
