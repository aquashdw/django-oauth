from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import uuid4

import jwt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, BadRequest
from django.shortcuts import render, redirect
from hashids import Hashids
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from oauth.models import OAuthClient, CallbackUrl
from oauth.serializer import OAuthTokenRequestSerializer

OAUTH_CODENAME = 'oauth_active'
OAUTH_LOOKUP_NAME = 'oauth.oauth_active'
SECRET_KEY = settings.SECRET_KEY
hashids = Hashids(salt=SECRET_KEY[-16:], min_length=8)


@login_required
def authorize(request):
    client_id = request.GET.get('clientid', '')
    callback_url = request.GET.get('callback', '')
    response_type = request.GET.get('response_type')
    if not client_id or not callback_url or response_type != 'code':
        raise BadRequest('insufficient params')

    client = OAuthClient.objects.filter(client_id=client_id).exclude(status=OAuthClient.DELETED).first()
    if not client:
        raise BadRequest('invalid client')

    callback = CallbackUrl.objects.filter(client=client, url=callback_url).first()
    if not callback:
        raise BadRequest('invalid callback')

    if client.status == OAuthClient.DEVELOPMENT and not client.test_users.contains(
            request.user) and request.user != client.owner:
        raise PermissionDenied

    if request.method == 'GET':
        return render(request, 'oauth/authorize.html', {'client': client})

    code = str(uuid4()).replace('-', '')
    payload = {
        'user': request.user,
        'code': code,
        'client': client,
    }
    cache.set(code, payload, timeout=600)
    params = {'code': code}
    if request.GET.get('state'):
        params['state'] = request.GET.get('state')
    return redirect(f'{callback_url}?{urlencode(params)}')


@api_view(['POST'])
def token(request):
    serializer = OAuthTokenRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    code = serializer.validated_data['code']
    instance = cache.get(code)
    if not instance:
        return Response(status=status.HTTP_404_NOT_FOUND)

    client = instance.get('client')
    if client.client_secret != serializer.validated_data['client_secret']:
        return Response(status=status.HTTP_403_FORBIDDEN)
    cache.delete(code)

    user = instance.get('user')
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=3605)
    encoded_jwt = jwt.encode({
        'sub': hashids.encode(user.pk),
        'iat': now,
        'exp': expires,
    }, SECRET_KEY, 'HS256')

    return Response(data={
        'token_type': 'bearer',
        'access_token': encoded_jwt,
        'expires_in': expires,
    })
