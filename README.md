# Dognito

> A dummy JWT service for test environments

Dognito is a small HTTP service that can be used to create JSON Web Tokens that can be verified by other services using a set of well-known JSON Web Keys.
This is useful in testing environments where you might have a service that accepts tokens from, for example, AWS Cognito, but you don't want to rely on an actual running AWS Cognito instance.

## Getting started

The quickest way to try it out, assuming you have docker:

```shell
> git clone https://github.com/daehlith/dognito.git
> cd dognito/
> docker build -t dognito:local-build . && docker run -p 8080:8080 --rm --name dognito_local dognito:local-build 
```

This clones the repository, builds a docker image from the provided Dockerfile and then runs dognito on port 8080.

The service exposes three endpoints:

* `POST /token` - creates a token, optionally accepting a JSON object in the request payload specifying additional claims.
* `GET /verify` - verifies a token that was being passed via the `Authorization` header.
* `GET /.well-known/jwks.json` - returns a JWKS that can be used to verify tokens created by this process.

Please note that the JWKS is not persisted between runs of this service.

## Usage

The usage examples assume that you have the excellent [httpie](https://httpie.org) utility installed.

### Creating tokens

Creating a token is as easy as issuing the following command:

```bash
$ http POST localhost:8080/token foo=bar baz=4711
HTTP/1.1 200 OK
Content-Length: 679
Content-Type: application/json; charset=utf-8
Date: Sat, 03 Apr 2021 16:40:34 GMT
Server: Python/3.9 aiohttp/3.7.4.post0

{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjQ0NTYwNjVhLTNhY2UtNGZlMS04MGNhLWRiMjY0NWFiMmNkZSJ9.eyJpc3MiOiJkb2duaXRvIiwic3ViIjoiOGNkN2RkNTYtYmI4Zi00NjRkLWJkZmYtYTFmOTVhOTE1YzRlIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwiYXV0aF90aW1lIjoxNjE3NDY4MDM0LCJmb28iOiJiYXIiLCJiYXoiOiI0NzExIn0.pEek5L4kxe2k7cR4HE8Uh13pWMJH0iwFY6SoMcqkeMtQuLh5FherUkP-XCGRFtB1yT4-jM_et4zviwgn66qFYzZ_lfhmdEtWWSYJ0txaRm2SmJqRu_4P_eQjYS6vu1TOi2qu5169CKyS1ikQsJIsDwN4EFhQJtHMkt1h6CcVJK2pWxpjLFNKo8Ask0MpVpuI1rv3NlvtaJRfzfBlIfAzugAoQTClmpLMGEAQIVoGRbeqZc5h96Ek76F0BYGum-EXVTAVqgvCDhC_7ZeSYlPI3RdR-hMFkuezwhzRskIc3mU-AnXkdg3ll9J_lJaV09uwixdVox2kQ-3G6ozRwgGGVA",
    "expires_in": 3600,
    "token_type": "Bearer"
}
```

### Verifying tokens

Tokens can be verified either manually using the JWKS at `localhost:8080/.well-known/jwks.json`, 
or by issuing a command to the `verify` endpoint with the token in the `Authorization` header:
```bash
$ http localhost:8080/verify "Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjQ0NTYwNjVhLTNhY2UtNGZlMS04MGNhLWRiMjY0NWFiMmNkZSJ9.eyJpc3MiOiJkb2duaXRvIiwic3ViIjoiOGNkN2RkNTYtYmI4Zi00NjRkLWJkZmYtYTFmOTVhOTE1YzRlIiwidG9rZW5fdXNlIjoiYWNjZXNzIiwiYXV0aF90aW1lIjoxNjE3NDY4MDM0LCJmb28iOiJiYXIiLCJiYXoiOiI0NzExIn0.pEek5L4kxe2k7cR4HE8Uh13pWMJH0iwFY6SoMcqkeMtQuLh5FherUkP-XCGRFtB1yT4-jM_et4zviwgn66qFYzZ_lfhmdEtWWSYJ0txaRm2SmJqRu_4P_eQjYS6vu1TOi2qu5169CKyS1ikQsJIsDwN4EFhQJtHMkt1h6CcVJK2pWxpjLFNKo8Ask0MpVpuI1rv3NlvtaJRfzfBlIfAzugAoQTClmpLMGEAQIVoGRbeqZc5h96Ek76F0BYGum-EXVTAVqgvCDhC_7ZeSYlPI3RdR-hMFkuezwhzRskIc3mU-AnXkdg3ll9J_lJaV09uwixdVox2kQ-3G6ozRwgGGVA"
HTTP/1.1 200 OK
Content-Length: 154
Content-Type: application/json; charset=utf-8
Date: Sat, 03 Apr 2021 16:42:16 GMT
Server: Python/3.9 aiohttp/3.7.4.post0

{
    "claims": {
        "auth_time": 1617468034,
        "baz": "4711",
        "foo": "bar",
        "iss": "dognito",
        "sub": "8cd7dd56-bb8f-464d-bdff-a1f95a915c4e",
        "token_use": "access"
    }
}
```
