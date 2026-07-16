"""CORS on the discovery endpoints."""


def test_well_known_responses_carry_cors_headers(client):
    # Nothing serves this path yet — that's the next exercise. A 404 is fine;
    # what matters is that a browser is allowed to *read* the 404.
    response = client.get("/.well-known/oauth-authorization-server")

    assert response.headers.get("Access-Control-Allow-Origin") == "*", (
        "well-known responses need Access-Control-Allow-Origin (see the TODO in app.py)"
    )
    assert response.headers.get("Access-Control-Allow-Methods") == "GET, HEAD, OPTIONS"
    assert response.headers.get("Access-Control-Allow-Headers") == "mcp-protocol-version"


def test_preflight_is_answered(client):
    response = client.options("/.well-known/oauth-protected-resource/mcp")
    assert response.status_code == 204, (
        "an OPTIONS preflight should be answered directly, without reaching the route"
    )
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
    assert response.headers.get("Access-Control-Max-Age") == "86400"


def test_the_mcp_endpoint_gets_no_cors_headers(client):
    """/mcp isn't browser-facing, so it shouldn't invite browsers."""
    response = client.post("/mcp")
    assert response.headers.get("Access-Control-Allow-Origin") is None, (
        "only /.well-known URLs should get CORS headers"
    )


def test_healthcheck_still_works(client):
    assert client.get("/healthcheck").status_code == 200
