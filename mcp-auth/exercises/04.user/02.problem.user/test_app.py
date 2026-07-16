"""Who am I?"""

import json

from epicme.testing import call_tool, mcp_request, mcp_result, tool_text


def test_whoami_reports_the_authenticated_user(client, token):
    result = call_tool(client, "whoami", token=token)
    assert not result.get("isError"), tool_text(result)

    user = json.loads(tool_text(result))
    assert user["username"] == "kody", (
        "whoami should report the user the token belongs to (see the TODO in auth.py)"
    )
    assert user["email"] == "kody@epicme.test"


def test_whoami_follows_the_token(client, other_token):
    user = json.loads(tool_text(call_tool(client, "whoami", token=other_token)))
    assert user["username"] == "olivia"


def test_the_user_resource_is_readable(client, token):
    mcp_request(client, "initialize", None, token=token)
    result = mcp_result(
        mcp_request(client, "resources/read", {"uri": "epicme://user"}, token=token)
    )
    user = json.loads(result["contents"][0]["text"])
    assert user["username"] == "kody"


async def test_fetch_user_asks_the_authorization_server(token):
    from auth import fetch_user, resolve_auth_info

    auth_info = await resolve_auth_info(f"Bearer {token}")
    user = await fetch_user(auth_info)

    assert user is not None, "a valid token should get a profile back"
    assert user.sub == "user-kody"
    assert user.username == "kody"
