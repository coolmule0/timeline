import logging

from rest_framework import permissions, viewsets, status
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.response import Response
from rest_framework.decorators import action
from django.forms.models import model_to_dict

from .models import FileSystemSource
from .models.hackernews import HackerNewsSource
from .models.reddit import RedditSource
from .models.rss import RssSource
from .models.rsync import RsyncSource, RsyncDestination
from .models.trakt import TraktSource
from .models.twitter import TwitterSource
from .serializers import RsyncSourceSerializer, TwitterSourceSerializer, RedditSourceSerializer, \
    HackerNewsSourceSerializer, RssSourceSerializer, FileSystemSourceSerializer, RsyncDestinationSerializer, \
    TraktSourceSerializer    
from .utils.ssh import copy_ssh_keys, SSHCredentialsError, SSHTimeoutError

logger = logging.getLogger(__name__)


class RsyncSourceViewSet(viewsets.ModelViewSet):
    """
    List and manage backup Sources. A Source is a remote server from which files are backed up.
    """
    queryset = RsyncSource.objects.all()
    serializer_class = RsyncSourceSerializer
    permission_classes = [permissions.AllowAny]

    @staticmethod
    def copy_ssh_keys(serializer):
        data = serializer.validated_data
        try:
            logger.info(f"Copying SSH keys to {data['host']}")
            copy_ssh_keys(data['host'], data['port'], data['user'], data['password'], data['key_exchange_method'])
        except SSHCredentialsError:
            raise AuthenticationFailed('Could not fetch SSH keys. The credentials are incorrect.')
        except SSHTimeoutError:
            raise APIException('Could not fetch SSH keys. The operation timed out. Are the host and port correct?')
        except:
            raise APIException('Could not fetch SSH keys.')

    def perform_create(self, serializer):
        self.copy_ssh_keys(serializer)
        serializer.validated_data.pop('password')
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        self.copy_ssh_keys(serializer)
        serializer.validated_data.pop('password')
        return super().perform_update(serializer)


class RsyncDestinationViewSet(RsyncSourceViewSet):
    queryset = RsyncDestination.objects.all().order_by('key')
    serializer_class = RsyncDestinationSerializer
    permission_classes = [permissions.AllowAny]


class TwitterSourceViewSet(viewsets.ModelViewSet):
    queryset = TwitterSource.objects.all().order_by('twitter_username')
    serializer_class = TwitterSourceSerializer
    permission_classes = [permissions.AllowAny]


class RedditSourceViewSet(viewsets.ModelViewSet):
    queryset = RedditSource.objects.all().order_by('reddit_username')
    serializer_class = RedditSourceSerializer
    permission_classes = [permissions.AllowAny]


class HackerNewsSourceViewSet(viewsets.ModelViewSet):
    queryset = HackerNewsSource.objects.all().order_by('hackernews_username')
    serializer_class = HackerNewsSourceSerializer
    permission_classes = [permissions.AllowAny]


class RssSourceViewSet(viewsets.ModelViewSet):
    queryset = RssSource.objects.all()
    serializer_class = RssSourceSerializer
    permission_classes = [permissions.AllowAny]


class FileSystemSourceViewSet(viewsets.ModelViewSet):
    queryset = FileSystemSource.objects.all()
    serializer_class = FileSystemSourceSerializer
    permission_classes = [permissions.AllowAny]


class TraktSourceViewSet(viewsets.ModelViewSet):
    queryset = TraktSource.objects.all()
    serializer_class = TraktSourceSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True)
    def start_poll(self, request, pk=None):
        """
        Poll for checking authentication for this source
        """
        tsource = self.get_object()

        tsource.app_init()
        code = tsource.traktApp.get_code()
        return Response(code)
    
    @action(detail=True)
    def get_url(self, request, pk=None):
        """
        First stage of authentication process: Get URL for user to visit to obtain pin
        """
        tsource = self.get_object()

        tsource.app_init()
        return Response({'url': tsource.traktApp.get_url_pin()})
    
    @action(detail=True, methods=['put'])
    def put_pin(self, request, pk=None):
        """
        Second stage of authentication process: provide pin and let backend exchange token
        """
        tsource = self.get_object()
        # Add pin to already stored data for serializer
        comb_data = {'pin': request.data['pin']} | model_to_dict(tsource)
        serializer = TraktSourceSerializer(data=comb_data)
        if serializer.is_valid():
            tsource.app_init()
            if tsource.traktApp.set_pin(serializer.validated_data['pin']):
                return Response({'status': 'Pin Accepted'})
            else: 
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def status(self, request, pk=None):
        """
        Return the authentication status for this source
        """
        tsource = self.get_object()

        tsource.app_init()
        return Response({'status': tsource.traktApp.status()})

    @action(detail=True)
    def start_poll_device(self, request, pk=None):
        """
        Poll for checking authentication for this source
        """
        tsource = self.get_object()

        tsource.device_init()
        code = tsource.traktDevapp.get_code()
        return Response(code)
    
    @action(detail=True)
    def status_device(self, request, pk=None):
        """
        Return the authentication status for this source
        """
        tsource = self.get_object()

        tsource.device_init()
        return Response({'status': tsource.traktDevapp.status()})
