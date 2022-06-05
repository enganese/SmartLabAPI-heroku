import fastapi, uvicorn, aiohttp, bs4
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import re

from smart_lab_api import SmartLabAPI, dataclass_types

app = fastapi.FastAPI()


def camel_to_snake(text):
    try:
        import re
    except ImporError:
        print("Bruh, how you dont have 're' library? It's built-in, you stupid.")

    text = re.split("(?=[A-Z])", text)

    result = ""
    result += "_".join(text)

    return result.lower()[1:]


def to_json(total_data, debug: bool = True) -> dict | None:
    try:
        new_total_data = {}

        for item in total_data:
            class_name = camel_to_snake(str(item.__class__.__name__))

            if isinstance(item, dataclass_types.ShareHolders):
                new_total_data[class_name] = {
                    "for_graph": item.for_graph,
                    "data": item.data,
                    "aliases": item.aliases,
                }
            else:
                new_total_data[class_name] = {
                    "values": item.values,
                    "aliases": item.aliases,
                }

        return new_total_data
    except Exception as e:
        if debug:
            print("ERROR:", e)

        return None


@app.get("/{ticker}/{period}")
async def get_url(period: str = None, ticker: str = None):
    if period is None or period not in ["year", "y", "quarter", "q"]:
        return Response(
            content={
                "ok": False,
                "message": "You need to pass an period to get full information",
            },
            status_code=400,
        )

    if ticker is None:
        return Response(
            content={
                "ok": False,
                "message": "You need to pass a company ticker to get full information",
            },
            status_code=400,
        )

    api = SmartLabAPI.SmartLabAPI()
    total_data = api.get_data(ticker=ticker, period=period)

    return JSONResponse(content={"ok": True, "data": to_json(total_data)}, media_type="application/json", status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, log_level="info")
