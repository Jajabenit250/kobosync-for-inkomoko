import json

async def register_webhook(session, url):
        async with session.post(
            "http://dev.inkomoko.com:1055/register_webhook",
            body=json.dumps({"url": url}),
            headers={
                "Content-Type": "application/json",
            },
        ) as response:
            return response
      