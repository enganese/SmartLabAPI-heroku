import fastapi, uvicorn, aiohttp, bs4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
import re
from smart_lab_api import SmartLabAPI, dataclass_types
from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def to_json2(total_data, debug: bool = True) -> dict | None:
    try:
        new_total_data = {}

        for item in total_data:
            dict_name = item.name

            new_total_data[dict_name] = {
                # IMPORTANT: title is title of each page in cyrillic!
                "title": item.title,
                # IMPORTANT: categories are years!
                "categories": item.categories,
                "data": item.data,
            }

        return new_total_data
    except Exception as e:
        if debug:
            print("ERROR:", e)

        return None


@app.exception_handler(404)
async def custom_404_handler(_, __):
    return RedirectResponse("/docs")


@app.get("/{ticker}/{period}")
async def get_url(period: str = None, ticker: str = None, full_info: bool = False):
    if period is None or period not in ["year", "y", "yaer", "quarter", "q", "qurater"]:
        return JSONResponse(
            content={
                "ok": False,
                "message": "You need to pass an period to get full information",
            },
            media_type="application/json",
            status_code=400,
        )

    if ticker is None:
        return JSONResponse(
            content={
                "ok": False,
                "message": "You need to pass a company ticker to get full information",
            },
            media_type="application/json",
            status_code=400,
        )

    if full_info:
        api = None
        total_data = None

        if period in ["year", "y", "yaer"]:
            api = SmartLabAPI.SmartLabAdvancedAPI()
            total_data = api.get_full_data_for_period(ticker=ticker, period="year")
            print("Total data:", total_data)

        if period in ["quarter", "q", "qurater"]:
            api = SmartLabAPI.SmartLabAdvancedAPI()
            total_data = api.get_full_data_for_period(ticker=ticker, period="quarter")

        if total_data is None:
            return JSONResponse(
                content={
                    "ok": False,
                    "message": "Something went wrong! Please check the query parameters.",
                },
                media_type="application/json",
                status_code=400,
            )

        return JSONResponse(
            content={
                "ok": True,
                "ticker": ticker,
                "period": period,
                "data": to_json2(total_data),
            },
            media_type="application/json",
            status_code=200,
        )

    else:
        api = SmartLabAPI.SmartLabAPI()
        total_data = api.get_data(ticker=ticker, period=period)

        if total_data is None:
            return JSONResponse(
                content={
                    "ok": False,
                    "message": "Something went wrong! Please check the query parameters.",
                },
                media_type="application/json",
                status_code=400,
            )

        return JSONResponse(
            content={
                "ok": True,
                "ticker": ticker,
                "period": period,
                "data": to_json(total_data),
            },
            media_type="application/json",
            status_code=200,
        )


@app.get("/get_companies")
async def get_companies():
    try:
        api = SmartLabAPI.SmartLabAPI()
        list_of_companies = api.get_companies_names()

        return JSONResponse(
            content={"ok": True, "data": list_of_companies},
            media_type="application/json",
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={
                "ok": False,
                "message": "If function returned absolutely empty list, then it means that there is no data or something went wrong on server's side. Please, try again later.",
            },
            media_type="application/json",
            status_code=400,
        )


@app.get("/autocomplete")
async def get_auto_complete_values(direct_info: bool, value: str = None):
    try:
        if value is None or value == "":
            return JSONResponse(
                content={
                    "ok": False,
                    "message": "You need to pass a value(as a GET query) to get autocomplete values. Example: https://smartlab.herokuapp.com/autocomplete?value=Microso",
                },
                media_type="application/json",
                status_code=400,
            )

        api = SmartLabAPI.SmartLabAPI()
        auto_complete_values = api.get_auto_complete_values(value=value)

        if direct_info:
            return auto_complete_values["results"]
        else:
            return JSONResponse(
                content={"ok": True, "data": auto_complete_values},
                media_type="application/json",
                status_code=200,
            )
    except Exception as e:
        return JSONResponse(
            content={
                "ok": False,
                "message": "Server side error(exception was handled). Try again later, please.",
            },
            media_type="application/json",
            status_code=500,
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, log_level="info")
