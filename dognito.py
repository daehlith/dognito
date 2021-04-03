"""
A dummy service to generate JWTs
"""
import http
import json
import random
import time
import uuid
import aiohttp.web
import jwt
from jwt.algorithms import RSAAlgorithm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


INTERNAL_KEY_SET = 'dognito-keys'
WELL_KNOWN_KEY_SET = 'dognito-jwks'


async def create_token(request):
    """ Returns a JWT that can be verified with the

    Claims to be encoded in the JWT can be provided as a json-encoded dictionary
    via the request body.
    If no claims are provided, a JWT with the following claims is created:
    `iss`, `sub`, `token_use` and `auth_time`.
    """
    claims = {}
    if request.can_read_body:
        claims = await request.json()

    access_token = {
        'iss': 'dognito',
        'sub': str(uuid.uuid4()),
        'token_use': 'access',
        'auth_time': int(time.time())
    }
    access_token.update(claims)

    kid = random.choice(list(request.app[INTERNAL_KEY_SET]))
    key_pair = request.app[INTERNAL_KEY_SET][kid]

    access_token = jwt.encode(
        access_token, key_pair['private'], headers={'kid': kid}, algorithm='RS256'
    )
    return aiohttp.web.json_response(
        data={
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    )


async def get_well_known_keys(request):
    """ Returns the set of well-known keys that was created on start up.
    """
    return aiohttp.web.json_response(
        data=request.app[WELL_KNOWN_KEY_SET]
    )


def create_keys(app):
    """ Create a set of RSA key pairs to use for creating tokens.
    """
    keys = {}
    for _ in range(2):
        kid = str(uuid.uuid4())
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        private_jwk = RSAAlgorithm.to_jwk(private_key)
        public_key = private_key.public_key()
        public_jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
        public_jwk.pop('key_ops', None)
        public_jwk['alg'] = 'RS256'
        public_jwk['use'] = 'sig'
        public_jwk['kid'] = kid

        keys[kid] = {
            'private': private_key,
            'private_jwk': private_jwk,
            'public': public_key,
            'public_jwk': public_jwk
        }

    app[INTERNAL_KEY_SET] = keys
    app[WELL_KNOWN_KEY_SET] = {
        'keys': [key['public_jwk'] for key in keys.values()]
    }


async def verify_token(request):
    """ Endpoint that can be used to verify a token received from this service.

    The token to verify must be passed via the Authorization header.
    """
    token = request.headers.get('Authorization', '').split(' ')[-1]
    if not token:
        return aiohttp.web.json_response(data={
            'error': 'Missing authorization header'
        }, status=http.HTTPStatus.BAD_REQUEST)

    header = jwt.get_unverified_header(token)
    key = RSAAlgorithm.from_jwk(
        json.dumps(request.app[INTERNAL_KEY_SET][header['kid']]['public_jwk'])
    )
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=[header['alg']]
        )
        return aiohttp.web.json_response(data={
            'claims': claims
        })
    except jwt.InvalidTokenError as err:
        return aiohttp.web.json_response(data={
            'token': token,
            'header': header,
            'error': str(err)
        }, status=http.HTTPStatus.BAD_REQUEST)


def main():
    """ Entrypoint that bootstraps and starts the service
    """
    app = aiohttp.web.Application()
    create_keys(app)
    app.router.add_post('/token', create_token)
    app.router.add_get('/verify', verify_token)
    app.router.add_get('/.well-known/jwks.json', get_well_known_keys)
    aiohttp.web.run_app(app)


if __name__ == '__main__':
    main()
