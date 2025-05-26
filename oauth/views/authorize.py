import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from uuid import uuid4

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, BadRequest
from django.shortcuts import render, redirect
from hashids import Hashids
from jwt import ExpiredSignatureError, InvalidSignatureError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from oauth.models import OAuthClient, CallbackUrl
from oauth.serializer import OAuthTokenRequestSerializer

User = get_user_model()

OAUTH_CODENAME = 'oauth_active'
OAUTH_LOOKUP_NAME = 'oauth.oauth_active'
SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = 'HS256'
ACCESS_EXPIRES_AFTER = 3605
REFRESH_EXPIRES_AFTER = 3600 * 8
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
    return Response(data=create_tokens(request, user))


@api_view
def get_user_info(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response({"error": "Missing or invalid token"}, status=401)

    try:
        payload = jwt.decode(auth_header.split(" ")[1], SECRET_KEY, JWT_ALGORITHM)
    except ExpiredSignatureError:
        return Response(data={'error': 'expired token'}, status=status.HTTP_401_UNAUTHORIZED)
    except InvalidSignatureError:
        return Response(data={'error': 'invalid token'}, status=status.HTTP_403_FORBIDDEN)

    if payload.get('type') != 'access':
        return Response(data={'error': 'invalid token'}, status=status.HTTP_403_FORBIDDEN)

    user = User.objects.filter(pk=hashids.decode(payload.get('sub'))[0]).first()
    if not user:
        return Response(data={'error': 'internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(data={'email': user.email})


@api_view(['POST'])
def refresh(request):
    refresh_token = request.data.get("token")
    if not refresh_token:
        return Response({"error": "Missing or invalid token"}, status=401)

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, JWT_ALGORITHM)
    except ExpiredSignatureError:
        return Response(data={'error': 'expired token'}, status=status.HTTP_401_UNAUTHORIZED)
    except InvalidSignatureError:
        return Response(data={'error': 'invalid token'}, status=status.HTTP_403_FORBIDDEN)

    if payload.get('type') != 'refresh':
        return Response(data={'error': 'invalid token'}, status=status.HTTP_403_FORBIDDEN)

    user = User.objects.filter(pk=hashids.decode(payload.get('sub'))[0]).first()
    if not user:
        return Response(data={'error': 'internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    active_refresh_token = cache.get(f'{user.pk}-{client_fingerprint(request)}-refresh')
    if not active_refresh_token or active_refresh_token != refresh_token:
        return Response(data={'error': 'invalid token'}, status=status.HTTP_403_FORBIDDEN)

    return Response(data=create_tokens(request, user))


def create_tokens(request, user):
    now = datetime.now(timezone.utc)
    access_expires = now + timedelta(seconds=ACCESS_EXPIRES_AFTER)
    access_token = jwt.encode({
        'sub': hashids.encode(user.pk),
        'type': 'access',
        'iat': now,
        'exp': access_expires,
    }, SECRET_KEY, JWT_ALGORITHM)

    refresh_expires = now + timedelta(seconds=REFRESH_EXPIRES_AFTER)
    refresh_token = jwt.encode({
        'sub': hashids.encode(user.pk),
        'type': 'refresh',
        'iat': now,
        'exp': refresh_expires,
    }, SECRET_KEY, JWT_ALGORITHM)

    cache.set(f'{user.pk}-{client_fingerprint(request)}-refresh', refresh_token, REFRESH_EXPIRES_AFTER)

    return {
        'token_type': 'bearer',
        'access_token': access_token,
        'access_expires_in': access_expires,
        'refresh_token': refresh_token,
        'refresh_expires_in': refresh_expires
    }


def client_fingerprint(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    accept = request.META.get("HTTP_ACCEPT", "")
    lang = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    enc = request.META.get("HTTP_ACCEPT_ENCODING", "")
    ip = request.META.get("REMOTE_ADDR", "")
    raw = f"{user_agent}|{accept}|{lang}|{enc}|{ip}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
