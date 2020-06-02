import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'nanodegrees.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'CoffeeAPI'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
#? implement get_token_auth_header() method
'''
def get_token_auth_header():
    # get the header from the request
    auth = request.headers.get('Authorization', None)

    # raise an AuthError if no header is present
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    # split bearer and the token
    parts = auth.split()

    # raise an AuthError if the header is malformed
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    # store the token on var named token to return it
    token = parts[1]

    # return the token part of the header
    return token


'''
# ? implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload
'''
def check_permissions(permission, payload):
    # raise an AuthError if permissions are not included in the payload
    if 'permissions' not in payload:
        abort(400)
        
    # raise an AuthError if the requested permission string is not in the payload permissions array
    # otherwise return true 
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission Not found',
        }, 401)
    return True

'''
    # ? verify_decode_jwt(token) method
    @INPUTS
    token: a json web token (string)
    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    # Get public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # Get the data in the header
    unverified_header = jwt.get_unverified_header(token)

    # Auth0 token should have a key id - (kid)
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed'
        }, 401)

    rsa_key = {}

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            break

    # verify the token using Auth0 /.well-known/jwks.json
    # decode the payload from the token
    if rsa_key:
        try:
            # Validate the token using the rsa_key
            # validate the claims
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            # return the decoded payload
            return payload

        # otherwise except rise
        except jwt.ExpiredSignatureError:

            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:

            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, '
                'check the audience and issuer.'
            }, 401)

        except Exception:

            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse the authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'not an appropriate key.'
    }, 400)





'''
#? requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')   
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # use the get_token_auth_header method to get the token
            token = get_token_auth_header()
            # use the verify_decode_jwt method to decode the jwt
            payload = verify_decode_jwt(token)
            # use the check_permissions method validate claims and check the requested permission
            check_permissions(permission, payload)
            # return the decorator which passes the decoded payload to the decorated method
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator