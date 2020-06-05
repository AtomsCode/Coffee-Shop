from os import environ
import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'nanodegrees.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'CoffeeAPI'

# AuthError Exception


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

# Auth Header
'''
#? get_token_auth_header() method
# get the header from the request
# raise an AuthError if no header is present
# it split to bearer and the token
# raise an AuthError if the header is malformed
# return token part of the header
'''


def get_token_auth_header():
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
        if auth_header:
            bearer_token_array = auth_header.split(' ')
            if bearer_token_array[0] and bearer_token_array[0].lower() == "bearer" and bearer_token_array[1]:
                return bearer_token_array[1]
    raise AuthError({
        'success': False,
        'message': 'JWT not found',
        'error': 401
    }, 401)


'''
#? check_permissions(permission, payload) method
@INPUTS
permission: string permission (i.e. 'post:drink')
payload: decoded jwt payload
# raise an AuthError if permissions are not included in the payload
# raise an AuthError if the requested permission string
is not in the payload permissions
'''


def check_permissions(permission, payload):
    if "permissions" in payload:
        if permission in payload['permissions']:
            return True
    raise AuthError({
        'success': False,
        'message': 'Permission not found in JWT',
        'error': 401
    }, 401)


'''
#? verify_decode_jwt(token) method
@INPUTS
token: a json web token (string)
it should be an Auth0 token with key id (kid)
# verify the token using Auth0 /.well-known/jwks.json
# decode the payload from the token
# should validate the claims
# return the decoded payload
'''


def verify_decode_jwt(token):
    # GET PUBLIC KEY from  AUTH0
    jsonurl = urlopen(f'http://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET DATA from the header
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'success': False,
            'message': 'Authorization malformed',
            'error': 401,
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # verify the token
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            # validate the claims
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'success': False,
                'message': 'Token expired',
                'error': 401,
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'success': False,
                'message': 'Please, check the audience and issuer',
                'error': 401,
            }, 401)
        except Exception:
            raise AuthError({
                'success': False,
                'message': 'Unable to parse authentication token',
                'error': 401,
            }, 401)
    raise AuthError({
        'success': False,
        'message': 'Unable to find the appropriate key',
        'error': 401,
    }, 401)


'''
#? @requires_auth(permission) decorator method
@INPUTS
permission: string permission (i.e. 'post:drink')
# use the get_token_auth_header method to get the token
# use the verify_decode_jwt method to decode the jwt
# use the check_permissions method validate claims
and check the requested permission
# return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
