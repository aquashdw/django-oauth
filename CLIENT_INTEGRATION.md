# OAuth client integration

This server implements a browser-based authorization-code flow. Its endpoints
are mounted below `/oauth/`; replace `https://auth.example.com` in the examples
with the server's origin. The authorization endpoint is for a user's browser.
Keep the client secret on your server and use it only when exchanging the code.

This implementation does not support PKCE. It also does not implement a
standard OAuth token response exactly: expiration fields contain timestamps,
and the token endpoint does not validate the submitted redirect URI.

## 1. Register the client and callback

Create an OAuth client in the server and register the exact callback URL that
your application will use. The callback URL supplied during authorization must
match a URL registered for that client. Do not add a query string or fragment
to the registered URL; the server adds response parameters to it.

The client needs its `client_id` and `client_secret`. Do not expose the secret
in browser code, mobile applications, or URLs.

## 2. Send the user to authorization

Navigate the user's browser to:

```text
GET https://auth.example.com/oauth/authorize/?clientid=CLIENT_ID&callback=CALLBACK_URL&response_type=code&state=STATE
```

URL-encode each query parameter. For example:

```text
https://auth.example.com/oauth/authorize/?clientid=abc123&callback=https%3A%2F%2Fapp.example.com%2Foauth%2Fcallback&response_type=code&state=8f3a12
```

Parameters:

| Parameter | Required | Description |
| --- | --- | --- |
| `clientid` | Yes | The OAuth client's `client_id`. |
| `callback` | Yes | An exact callback URL registered for this client. |
| `response_type` | Yes | Must be `code`. |
| `state` | No | A client-generated, URL-safe random value. It is returned on successful authorization so the client can correlate the response and mitigate request forgery. |

The user must be signed in to the OAuth server. Otherwise, the server sends
them through its login flow before continuing. On first use, the user sees a
consent page. After consent, or on later uses after consent has been saved, the
server redirects to the callback with `code` and, if supplied, `state`:

```text
https://app.example.com/oauth/callback?code=AUTHORIZATION_CODE&state=8f3a12
```

If the user refuses consent, the consent page redirects to the callback with
`error=refused` and, if supplied, `state`. Treat any error response as a failed
authorization; do not attempt to exchange a code.

The authorization code is short-lived (10 minutes) and can be exchanged only
once. For clients that are not in production status, authorization is limited
to the client owner and configured test users.

Missing or unsupported parameters, an unknown client, or an unregistered
callback cause the authorization request to fail with `400 Bad Request`.
Non-production clients used by users outside the owner/test-user list fail
with `403 Forbidden`.

## 3. Exchange the code for tokens

From your server, make a `POST` request to
`https://auth.example.com/oauth/token/`. The endpoint accepts form data or JSON.
For example, using JSON:

```http
POST /oauth/token/ HTTP/1.1
Host: auth.example.com
Content-Type: application/json

{
  "grant_type": "code",
  "client_secret": "CLIENT_SECRET",
  "redirect_uri": "https://app.example.com/oauth/callback",
  "code": "AUTHORIZATION_CODE"
}
```

`grant_type` must be `code`; all four fields are required. The server currently
does not compare `redirect_uri` with the callback used to authorize the request.
Still send the same registered callback URL, but do not rely on the token
endpoint to enforce that match.

On success, the response contains:

```json
{
  "token_type": "bearer",
  "access_token": "ACCESS_TOKEN",
  "access_expires_in": "<ISO-8601 timestamp>",
  "refresh_token": "REFRESH_TOKEN",
  "refresh_expires_in": "<ISO-8601 timestamp>"
}
```

The expiration values are timestamps (not seconds), despite the `_in` field
names. Access tokens are valid for about one hour; refresh tokens are valid for
eight hours. Store tokens securely.

Possible responses include `400 Bad Request` for invalid or missing request
fields, `404 Not Found` for an expired, unknown, or already-used code, and
`403 Forbidden` when the client secret does not match.

## 4. Call the user-info endpoint

Send the access token as a bearer token:

```http
GET /oauth/user-info/ HTTP/1.1
Host: auth.example.com
```

Include an `Authorization` header whose value is the bearer-token scheme,
followed by one space and the access token.

A successful response contains the user's nickname and email:

```json
{
  "nickname": "Example",
  "email": "user@example.com"
}
```

An expired token returns `401 Unauthorized`; an invalid token returns
`403 Forbidden`.

## 5. Refresh an access token

Before the access token expires, your server can exchange the refresh token by
posting it to `https://auth.example.com/oauth/refresh/`:

```http
POST /oauth/refresh/ HTTP/1.1
Host: auth.example.com
Content-Type: application/json

{
  "token": "REFRESH_TOKEN"
}
```

The response has the same shape as the token response. The server associates a
refresh token with the request's IP address and selected request headers. Make
refresh requests from the same client environment so that this binding matches.
An expired refresh token returns `401 Unauthorized`; an invalid or no-longer
active token returns `403 Forbidden`.

## Endpoint summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/oauth/authorize/` | Start browser authorization. |
| `POST` | `/oauth/token/` | Exchange an authorization code for tokens. |
| `GET` | `/oauth/user-info/` | Read the authenticated user's nickname and email. |
| `POST` | `/oauth/refresh/` | Exchange an active refresh token for new tokens. |
