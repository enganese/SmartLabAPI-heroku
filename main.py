import fastapi, uvicorn, aiohttp, bs4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
import re
from smart_lab_api import SmartLabAPI, dataclass_types
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dohod_api.client import AsyncClient as dohod_api


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Smart-Lab API",
        version="1.1.0",
        description="SmartLab API powered by FastAPI. \n\nIt's not official, but it works.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://i.imgur.com/ni2IwH2.png"
    }

    app.openapi_schema = openapi_schema
    
    return app.openapi_schema


app.openapi = custom_openapi


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
        print("Total data:", total_data)

        for item in total_data:
            dict_name = item.name            

            if dict_name == "dividend" and dict_name != "ir-rating":
                new_total_data[dict_name] = {
                    "name": item.name,
                    "title": item.title,
                    "categories": item.categories,
                    "dividend": item.dividend,
                    "div_yield": item.div_yield,
                    "div_payout_ratio": item.div_payout_ratio,
                    "dividend_payout": item.dividend_payout,
                }

            else:
                if dict_name != "ir-rating":
                    new_total_data[dict_name] = {
                        # IMPORTANT: title is title of each page in cyrillic!
                        "title": item.title,
                        # IMPORTANT: categories are years!
                        "categories": item.categories,
                        "data": item.data,
                        "field": item.field,
                        "point_format": item.point_format,
                    }

        return new_total_data
    except Exception as e:
        if debug:
            print("ERROR in to_json2():", e)

        return None


@app.exception_handler(404)
async def custom_404_handler(_, __):
    return RedirectResponse("/redoc")


@app.exception_handler(500)
async def custom_500_handler(_, __):
    resp = JSONResponse(
        content={"ok": False, "message": "Хьюстон, у нас проблемы!"},
        media_type="application/json",
        status_code=500,
    )
    return resp


@app.get("/ik/analytics/dividend/{ticker}")
async def get_html_page(ticker: str, direct_info: bool = False):
    html = None
    async with dohod_api() as api:
        html = await api.get_company_html_page(ticker)
    
    if direct_info:
        return html.replace('"', "'")

    return JSONResponse(
        content={"ok": True, "data": html},
        media_type="application/json",
        status_code=200,
    )

@app.get("/ik/analytics/dividend")
async def get_dividend(limit: int = 25, direct_info: bool = False):
    try:
        async with dohod_api() as api:
            list_of_dividend = await api.get_data_in_dict(limit=limit)

        # print(list_of_dividend)

        if direct_info:
            return list_of_dividend
        else:
            return JSONResponse(
                content={"ok": True, "data": list_of_dividend},
                media_type="application/json",
                status_code=200,
            )
    except Exception as e:
        return JSONResponse(
            content={
                "ok": False,
                "message": "Something went wrong on server's side. Please, try again later.",
            },
            media_type="application/json",
            status_code=400,
        )


@app.get("/{ticker}/{period}")
async def get_info_about_company(
    period: str = None,
    ticker: str = None,
    full_info: bool = False,
    include_data: str = "any",
):
    """
    ticker&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(path, required)&nbsp;&nbsp;&nbsp;&nbsp;- ticker of company\n
    period&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(path, required)&nbsp;&nbsp;&nbsp;&nbsp;- year or quarter\n
    full_info&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(query, optional)&nbsp;&nbsp;&nbsp;- if true, returns all info about company\n
    include_data&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(query, optional)&nbsp;&nbsp;&nbsp;- data names seperated with comma. E.g: revenue,ebitda,operating_income\n
    """
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
            total_data = await api.get_full_data_for_period(
                ticker=ticker, period="year", include_data=include_data
            )

        if period in ["quarter", "q", "qurater"]:
            api = SmartLabAPI.SmartLabAdvancedAPI()
            total_data = await api.get_full_data_for_period(
                ticker=ticker, period="quarter", include_data=include_data
            )

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
                "data": to_json2(total_data, debug=True),
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
                "message": "Something went wrong on server's side. Please, try again later.",
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
