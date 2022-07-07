from gevent import monkey


def stub(*args, **kwargs):  # pylint: disable=unused-argument
    pass


monkey.patch_all = stub

import grequests
import requests, json, aiohttp, re, bs4

from bs4 import BeautifulSoup
from typing import List, Dict, Any
from lxml.html import fromstring

from .tools import Tools
from . import dataclass_types
from .dataclass_types import *


def handler(err, e):
    # KEEP IT HERE, JUST FOR SOME DEBUG STAFF
    print("Handler:", err, e)


class SmartLabAdvancedAPI:
    @classmethod
    async def get_full_info(
        cls, include_data_array, period: str = None, ticker: str = None
    ) -> List[FullInfo]:
        if ticker is None or period is None:
            return None

        url = None

        if period in ["year", "y", "yaer"]:
            url = [f"https://smart-lab.ru/q/{ticker}/f/y/"]

        if period in ["quarter", "q", "qurater"]:
            url = [f"https://smart-lab.ru/q/{ticker}/f/q/"]

        if url is None:
            print(
                f"Period '{period}' is incorrect. Please, make sure period is either 'year' or 'quarter'. \nAlso, you can specify only first letter of periods. \ne.g: 'y' - for 'year', 'q' - for 'quarter'."
            )
            return None

        # resp = (grequests.get(u) for u in url)
        # response = grequests.map(resp)

        resp = None

        async with aiohttp.ClientSession() as session:
            async with session.get(url[0]) as response:
                resp = await response.text()

        if resp is None:
            return None

        soup = bs4.BeautifulSoup(resp, "lxml")

        all_links = soup.find_all("a", attrs={"target": "_blank"})
        all_a = []

        for link in all_links[1:]:
            text = link.get_text()
            href = link.get("href")
            url = "https://smart-lab.ru" + href

            if (
                href.startswith("/q/")
                and "MSFO" in href
                and not "/y/" in href
                and not "/f/" in href
                and "shares_fundamental" not in href
                or href.startswith("/q/")
                and "GAAP" in href
                and not "/y/" in href
                and not "/f/" in href
                and "shares_fundamental" not in href
                or href.startswith("/q/")
                and not "GAAP" in href
                and not "MSFO" in href
                and not "/y/" in href
                and not "/f/" in href
                and "shares_fundamental" not in href
            ):
                title = href.split("/")[-2]
                
                if "dividend" in title:
                    data_type = "Unknown"
                    ticker = href.split("/")[-3]
                else:
                    data_type = href.split("/")[-3]
                    ticker = href.split("/")[-4]


                if isinstance(include_data_array, str) and include_data_array == "any":
                    data = FullInfo(
                        ticker=ticker,
                        data_type=data_type,
                        title=title,
                        text=text,
                        url=url,
                        href=href,
                    )

                    all_a.append(data)

                elif (
                    isinstance(include_data_array, list) and title in include_data_array
                ):
                    data = FullInfo(
                        ticker=ticker,
                        data_type=data_type,
                        title=title,
                        text=text,
                        url=url,
                        href=href,
                    )

                    all_a.append(data)

        if all_a is None or len(all_a) == 0:
            return []

        return all_a

    @classmethod
    async def get_full_data_year(
        cls, full_info: List[FullInfo] = None
    ) -> List[FullData]:
        if full_info is None:
            return None

        if isinstance(full_info, list):
            print("full_info:", full_info)
            full_data = []

            # rs = (grequests.get(info.url) for info in full_info)
            # responses = grequests.map(rs)

            responses = []

            div = 0

            async with aiohttp.ClientSession() as session:
                for info in full_info:
                    if "dividend" in str(info.url):
                        if div == 0:
                            async with session.get(info.url) as response:
                                if "dividend" in str(info.url):
                                    div += 1
                                
                                data = {
                                    "text": await response.text(),
                                    "url": response.url,
                                }
                                responses.append(data)

                    else:
                        async with session.get(info.url) as response:
                            data = {
                                "text": await response.text(),
                                "url": response.url,
                            }
                            responses.append(data)

            for response in responses:
                soup = bs4.BeautifulSoup(response["text"], "lxml")

                all_scripts = soup.find_all("script", attrs={"type": "text/javascript"})

                if "dividend" not in str(response['url']):
                    str_dict = (
                        str(all_scripts[-2].string)
                        .split('{point.comment}"},')[0]
                        .replace("var aYearData = ", "")
                        .replace("\t", "")
                        .replace("\n", "")
                        .replace("'", '"')
                        + '{point.comment}"}}'
                    )
                else:
                    variables = re.findall("aQuarterSeries", all_scripts[-2].string)
                        
                    if len(variables) == 5:
                        str_dict = (
                                str(all_scripts[-2].string)
                                .split('{point.comment}"},')[0]
                                .replace("var aYearSeries = ", "")
                                .replace("\t", "")
                                .replace("\n", "")
                                .replace("'", '"').split(";function div")[0]
                            )
                        print("str_dict year WITHOUT quarter:", str_dict)
                    
                    elif len(variables) == 6:
                        str_dict = (
                            str(all_scripts[-2].string)
                            .replace("var aYearSeries = ", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .replace("'", '"')
                            .split(";var aQuarterSeries = ")[0]
                        )
                        print("str_dict year with quarter:", str_dict)
                    
                try:
                    json_dict = json.loads(str_dict)

                    tree = fromstring(response["text"])
                    title = tree.findtext(".//title")

                    splitted_texts = str(response["url"]).split("/")
                    name = splitted_texts[-2]

                    if name == "dividend":
                        data = FullDataDividend(
                            name=name,
                            title=title,
                            categories=json_dict["xaxis"],
                            dividend=json_dict["dividend"],
                            div_yield=json_dict["div_yield"],
                            div_payout_ratio=json_dict["div_payout_ratio"],
                            dividend_payout=json_dict["dividend_payout"]
                        )

                    else:
                        data = FullData(
                            name=name,
                            title=title,
                            categories=json_dict["diagram"]["categories"],
                            data=json_dict["diagram"]["data"],
                            field=json_dict["diagram"]["field"],
                            point_format=json_dict["diagram"]["point_format"],
                        )

                    full_data.append(data)
                except Exception as e:
                    print("ERROR 2:", e)

                    tree = fromstring(response["text"])
                    title = tree.findtext(".//title")

                    splitted_texts = str(response["url"]).split("/")
                    name = splitted_texts[-2]

                    full_data.append(
                        FullData(name=name, title=title, categories=[], data=[], field="", point_format="")
                    )

                    continue

            # print("Length of all links:", len(full_info))
            # print("Length of all data:", len(full_data))

            return full_data

        else:
            return []

    @classmethod
    async def get_full_data_quarter(cls, full_info: List[FullInfo]) -> List[FullData]:
        if isinstance(full_info, list):
            full_data = []

            # rs = (grequests.get(info.url) for info in full_info)

            # responses = grequests.map(rs)

            responses = []

            async with aiohttp.ClientSession() as session:
                for info in full_info:
                    async with session.get(info.url) as response:
                        data = {
                            "text": await response.text(),
                            "url": response.url,
                        }
                        responses.append(data)

            for response in responses:
                soup = bs4.BeautifulSoup(response["text"], "lxml")

                all_scripts = soup.find_all("script", attrs={"type": "text/javascript"})

                try:
                    if "dividend" not in str(response['url']):
                        str_dict = (
                            str(all_scripts[-2].string)
                            .split('{point.comment}"},')[0]
                            .replace("var aYearData = ", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .replace("'", '"')
                            + '{point.comment}"}}'
                        )
                    else:
                        variables = re.findall("aQuarterSeries", all_scripts[-2].string)
                        # Если квартер инфы нет
                        if len(variables) == 5:
                            str_dict = (
                                str(all_scripts[-2].string)
                                .split('{point.comment}"},')[0]
                                .replace("var aYearSeries = ", "")
                                .replace("\t", "")
                                .replace("\n", "")
                                .replace("'", '"').split(";function div")[0]
                            )
                        # Если квартер инфа есть
                        elif len(variables) == 6:
                            str_dict = (
                                str(all_scripts[-2].string)
                                .split('{point.comment}"},')[0]
                                .replace("var aYearSeries = ", "")
                                .replace("\t", "")
                                .replace("\n", "")
                                .replace("'", '"').split(";var aQuarterSeries = ")[1]
                                .split(";function div")[0]
                            )

                except Exception as e:
                    print("ERROR 3:", e)
                    # print("page:", response["url"])
                    # print("ALL scripts:", all_scripts)

                
                name = str(response["url"]).split("/")[-2]

                try:
                    json_dict = json.loads(str_dict)

                    tree = fromstring(response["text"])
                    title = tree.findtext(".//title")

                    if name == "dividend":
                        data = FullDataDividend(
                            name=name,
                            title=title,
                            categories=json_dict["xaxis"],
                            dividend=json_dict["dividend"],
                            div_yield=json_dict["div_yield"],
                            div_payout_ratio=json_dict["div_payout_ratio"],
                            dividend_payout=json_dict["dividend_payout"]
                        )

                    else:
                        data = FullData(
                            name=name,
                            title=title,
                            categories=json_dict["diagram"]["categories"],
                            data=json_dict["diagram"]["data"],
                            field=json_dict["diagram"]["field"],
                            point_format=json_dict["diagram"]["point_format"],
                        )

                    full_data.append(data)
                except Exception as e:
                    # print("ERROR 1:", e, "\nname:", name, "\nlink:", str(response["url"]), end="\n\n")

                    tree = fromstring(response["text"])
                    title = tree.findtext(".//title")

                    splitted_texts = str(response["url"]).split("/")
                    name = splitted_texts[-2]

                    full_data.append(
                        FullData(name=name, title=title, categories=[], data=[], field="", point_format="")
                    )
                    continue

            # print("Length of all links:", len(full_info))
            # print("Length of all data:", len(full_data))

            return full_data
        else:
            return []

    @classmethod
    async def get_full_data_for_period(
        cls, include_data: str, period: str = None, ticker: str = None
    ):
        include_data_array = (
            "any"
            if include_data == "any"
            else include_data.replace(" ", "").split(",")
            if "," in include_data
            else [include_data]
        )

        if ticker is None or period is None:
            return None

        if period in ["year", "y", "yaer"]:
            full_info_year = await cls.get_full_info(
                period="year", ticker=ticker, include_data_array=include_data_array
            )
            full_data_year = await cls.get_full_data_year(full_info=full_info_year)
            return full_data_year

        elif period in ["quarter", "q", "qurater"]:
            full_info_quarter = await cls.get_full_info(
                period="quarter", ticker=ticker, include_data_array=include_data_array
            )
            full_data_quarter = await cls.get_full_data_quarter(
                full_info=full_info_quarter
            )
            return full_data_quarter

        else:
            return None


class SmartLabAPI:
    """
    SmartLab API
    Version: 0.1.1-release(not full)
    """

    def __init__(self):
        self.ticker = None
        self.parser = None

    def get_years(self) -> List[str]:
        """
        Get years from the table
        """

        try:
            years = []

            soup = self.parser

            rows = soup.select("tr:has(td, th)")

            td_rows = rows[2].find_all("td")

            for td in td_rows:
                if "\xa0" in td:
                    td_rows.remove(td)

            for td in td_rows:
                text = Tools.normalize_text(td.get_text())

                years.append(text.split()[0])

            return years

        except Exception as e:
            print("year error:", e)
            return []

    def get_currency(self):
        try:
            # Get currency
            currency = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "currency"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                currency.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return currency
        except Exception as e:
            return []

    def get_report_url(self):
        try:
            # Get report_url
            report_url = []

            soup = self.parser

            td_rows = soup.find("tr", attrs={"field": "report_url"}).find_all("td")

            for td in td_rows:
                if td.get("class") is None:
                    a = td.find("a", attrs={"class": "icon pdf"})

                    if a == [] or a is None:
                        report_url.append("Недоступно / Not available")

                    elif a != [] or a is None:
                        report_url.append(a.get("href"))

                else:
                    continue

            return report_url
        except Exception as e:
            return []

    def get_year_report_url(self):
        try:
            # Get year_report_url
            year_report_url = []

            soup = self.parser

            td_rows = soup.find("tr", attrs={"field": "year_report_url"}).find_all("td")

            for td in td_rows:
                if td.get("class") is None:
                    a = td.find("a", attrs={"class": "icon pdf"})

                    if a == [] or a is None:
                        year_report_url.append("Недоступно / Not available")

                    elif a != [] or a is None:
                        year_report_url.append(a.get("href"))

                else:
                    continue

            return year_report_url
        except Exception as e:
            return []

    def get_presentation_url(self):
        try:
            # Get presentation_url
            presentation_url = []

            soup = self.parser

            td_rows = soup.find("tr", attrs={"field": "presentation_url"}).find_all(
                "td"
            )

            for td in td_rows:
                if td.get("class") is None:
                    a = td.find("a", attrs={"class": "icon pdf"})

                    if a == [] or a is None:
                        presentation_url.append("Недоступно / Not available")

                    elif a != [] or a is None:
                        presentation_url.append(a.get("href"))

                else:
                    continue

            return presentation_url
        except Exception as e:
            return []

    def get_oil_production(self):
        try:
            # Get oil_production
            oil_production = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "oil_production"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                oil_production.append(text) if Tools.isfloat(
                    text
                ) or text.isdigit() else None

            return oil_production
        except Exception as e:
            return []

    def get_oil_refining(self):
        try:
            # Get oil_refining
            oil_refining = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "oil_refining"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                oil_refining.append(text) if Tools.isfloat(
                    text
                ) or text.isdigit() else None

            return oil_refining
        except Exception as e:
            return []

    def get_gas_production(self):
        try:
            # Get gas_production
            gas_production = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "gas_production"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                gas_production.append(text) if Tools.isfloat(
                    text
                ) or text.isdigit() else None

            return gas_production
        except Exception as e:
            return []

    def get_revenue(self):
        try:
            # Get revenue
            revenue = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "revenue"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                revenue.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return revenue
        except Exception as e:
            return []

    def get_operating_income(self):
        try:
            # Get operating_income
            operating_income = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "operating_income"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                operating_income.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return operating_income
        except Exception as e:
            return []

    def get_ebitda(self):
        try:
            # Get ebitda
            ebitda = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "ebitda"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                ebitda.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return ebitda
        except Exception as e:
            return []

    def get_net_income(self):
        try:
            # Get net_income
            net_income = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "net_income"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                net_income.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return net_income
        except Exception as e:
            return []

    def get_net_income_ns(self):
        try:
            # Get net_income_ns
            net_income_ns = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "net_income_ns"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                net_income_ns.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return net_income_ns
        except Exception as e:
            return []

    def get_ocf(self):
        try:
            # Get ocf
            ocf = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "ocf"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                ocf.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return ocf
        except Exception as e:
            return []

    def get_capex(self):
        try:
            # Get capex
            capex = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "capex"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                capex.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return capex
        except Exception as e:
            return []

    def get_fcf(self):
        try:
            # Get fcf
            fcf = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "fcf"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                fcf.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return fcf
        except Exception as e:
            return []

    def get_dividend_payout(self):
        try:
            # Get dividend_payout
            dividend_payout = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "dividend_payout"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                dividend_payout.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return dividend_payout
        except Exception as e:
            return []

    def get_dividend(self):
        try:
            # Get dividend
            dividend = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "dividend"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                dividend.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return dividend
        except Exception as e:
            return []

    def get_div_yield(self):
        try:
            # Get div_yield
            div_yield = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "div_yield"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                div_yield.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return div_yield
        except Exception as e:
            return []

    def get_div_payout_ratio(self):
        try:
            # Get div_payout_ratio
            div_payout_ratio = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "div_payout_ratio"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                div_payout_ratio.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return div_payout_ratio
        except Exception as e:
            return []

    def get_opex(self):
        try:
            # Get opex
            opex = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "opex"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                opex.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return opex
        except Exception as e:
            return []

    def get_cost_of_production(self):
        try:
            # Get cost_of_production
            cost_of_production = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "cost_of_production"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                cost_of_production.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return cost_of_production
        except Exception as e:
            return []

    def get_r_and_d(self):
        try:
            # Get r_and_d
            r_and_d = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "r_and_d"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                r_and_d.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return r_and_d
        except Exception as e:
            return []

    def get_employment_expenses(self):
        try:
            # Get employment_expenses
            employment_expenses = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "employment_expenses"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                employment_expenses.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return employment_expenses
        except Exception as e:
            return []

    def get_interest_expenses(self):
        try:
            # Get interest_expenses
            interest_expenses = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "interest_expenses"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                interest_expenses.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return interest_expenses
        except Exception as e:
            return []

    def get_assets(self):
        try:
            # Get assets
            assets = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "assets"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                assets.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return assets
        except Exception as e:
            return []

    def get_net_assets(self):
        try:
            # Get net_assets
            net_assets = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "net_assets"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                net_assets.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return net_assets
        except Exception as e:
            return []

    def get_debt(self):
        try:
            # Get debt
            debt = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "debt"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                debt.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return debt
        except Exception as e:
            return []

    def get_cash(self):
        try:
            # Get cash
            cash = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "cash"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                cash.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return cash
        except Exception as e:
            return []

    def get_net_debt(self):
        try:
            # Get net_debt
            net_debt = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "net_debt"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                net_debt.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return net_debt
        except Exception as e:
            return []

    def get_common_share(self):
        try:
            # Get common_share
            common_share = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "common_share"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                common_share.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return common_share
        except Exception as e:
            return []

    def get_number_of_shares(self):
        try:
            # Get number_of_shares
            number_of_shares = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "number_of_shares"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                number_of_shares.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return number_of_shares
        except Exception as e:
            return []

    def get_free_float(self):
        try:
            # Get free_float
            free_float = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "free_float"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                free_float.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return free_float
        except Exception as e:
            return []

    def get_market_cap(self):
        try:
            # Get market_cap
            market_cap = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "market_cap"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                market_cap.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return market_cap
        except Exception as e:
            return []

    def get_ev(self):
        try:
            # Get ev
            ev = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "ev"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                ev.append(text) if len(
                    text
                ) <= 10 and text != "" and "EV" not in text or text == "Недоступно / Not available" else None

            return ev
        except Exception as e:
            return []

    def get_book_value(self):
        try:
            # Get book_value
            book_value = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "book_value"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                book_value.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return book_value
        except Exception as e:
            return []

    def get_eps(self):
        try:
            # Get eps
            eps = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "eps"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                eps.append(text) if len(
                    text
                ) <= 10 and text != "" and "EPS" not in text or text == "Недоступно / Not available" else None

            return eps
        except Exception as e:
            return []

    def get_fcf_share(self):
        try:
            # Get fcf_share
            fcf_share = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "fcf_share"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                fcf_share.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return fcf_share
        except Exception as e:
            return []

    def get_bv_share(self):
        try:
            # Get bv_share
            bv_share = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "bv_share"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                bv_share.append(text) if len(
                    text
                ) <= 10 and text != "" and "P/BV" not in text or text == "Недоступно / Not available" else None

            return bv_share
        except Exception as e:
            return []

    def get_ebitda_margin(self):
        try:
            # Get ebitda_margin
            ebitda_margin = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "ebitda_margin"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                ebitda_margin.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return ebitda_margin
        except Exception as e:
            return []

    def get_net_margin(self):
        try:
            # Get net_margin
            net_margin = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "net_margin"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                net_margin.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return net_margin
        except Exception as e:
            return []

    def get_fcf_yield(self):
        try:
            # Get fcf_yield
            fcf_yield = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "fcf_yield"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                fcf_yield.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return fcf_yield
        except Exception as e:
            return []

    def get_roe(self):
        try:
            # Get roe
            roe = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "roe"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                roe.append(text) if len(
                    text
                ) <= 10 and text != "" and "ROE" not in text or text == "Недоступно / Not available" else None

            return roe
        except Exception as e:
            return []

    def get_roa(self):
        try:
            # Get roa
            roa = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "roa"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                roa.append(text) if len(
                    text
                ) <= 10 and text != "" and "ROA" not in text or text == "Недоступно / Not available" else None

            return roa
        except Exception as e:
            return []

    def get_p_e(self):
        try:
            # Get p_e
            p_e = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "p_e"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                p_e.append(text) if len(
                    text
                ) <= 10 and text != "" and text != "P/E" or text == "Недоступно / Not available" else None

            return p_e
        except Exception as e:
            return []

    def get_p_s(self):
        try:
            # Get p_s
            p_s = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "p_s"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                p_s.append(text) if len(
                    text
                ) <= 10 and text != "" and text != "P/S" or text == "Недоступно / Not available" else None

            return p_s
        except Exception as e:
            return []

    def get_p_bv(self):
        try:
            # Get p_bv
            p_bv = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "p_bv"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                p_bv.append(text) if len(
                    text
                ) <= 10 and text != "" and "P/BV" not in text or text == "Недоступно / Not available" else None

            return p_bv
        except Exception as e:
            print("Couldn't get p/bv info, now trying to fetch p/b")
            try:
                # Get p_bv
                p_b = []

                soup = self.parser

                tr_rows = soup.find("tr", attrs={"field": "p_b"})

                for tr in tr_rows:
                    text = Tools.normalize_text(tr.get_text())

                    p_b.append(text) if len(
                        text
                    ) <= 10 and text != "" and "P/B" not in text or text == "Недоступно / Not available" else None

                return p_bv
            except Exception as e:
                print("quarter error:", e)
                return []

    def get_ev_ebitda(self):
        try:
            # Get ev_ebitda
            ev_ebitda = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "ev_ebitda"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                ev_ebitda.append(text) if len(
                    text
                ) <= 10 and text != "" and "EV/EBITDA" not in text or text == "Недоступно / Not available" else None

            return ev_ebitda
        except Exception as e:
            return []

    def get_debt_ebitda(self):
        try:
            # Get debt_ebitda
            debt_ebitda = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "debt_ebitda"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                debt_ebitda.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return debt_ebitda
        except Exception as e:
            return []

    def get_employees(self):
        try:
            # Get employees
            employees = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "employees"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                employees.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return employees
        except Exception as e:
            return []

    def get_labour_productivity(self):
        try:
            # Get labour_productivity
            labour_productivity = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "labour_productivity"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                labour_productivity.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return labour_productivity
        except Exception as e:
            return []

    def get_expenses_per_employee(self):
        try:
            # Get expenses_per_employee
            expenses_per_employee = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "expenses_per_employee"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                expenses_per_employee.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return expenses_per_employee
        except Exception as e:
            return []

    def get_r_and_d_capex(self):
        try:
            # Get r_and_d_capex
            r_and_d_capex = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "r_and_d_capex"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                r_and_d_capex.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return r_and_d_capex
        except Exception as e:
            return []

    def get_capex_revenue(self):
        try:
            # Get capex_revenue
            capex_revenue = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "capex_revenue"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                capex_revenue.append(text) if len(
                    text
                ) <= 10 and text != "" or text == "Недоступно / Not available" else None

            return capex_revenue
        except Exception as e:
            return []

    def get_irr(self):
        try:
            # Get irr
            irr = []

            soup = self.parser

            tr_rows = soup.find("tr", attrs={"field": "irr"})

            for tr in tr_rows:
                text = Tools.normalize_text(tr.get_text())

                irr.append(text) if len(
                    text
                ) <= 10 and text != "" and text != "IRрейтинг" or text == "Недоступно / Not available" else None

            return irr
        except Exception as e:
            return []

    def get_share_holders(self):
        try:
            # Share Holder's URL, bruh, this is the only way to get the share holders
            share_holders_url = f"https://smart-lab.ru/q/{self.ticker}/shareholders/"

            # Get share_holders
            share_holders = [
                {
                    "for_graph": [
                        [
                            "Акционеры",
                            "Доля в %",
                        ]
                    ],
                    "data": [],
                }
            ]

            html = requests.get(share_holders_url).text

            soup = BeautifulSoup(html, "lxml")

            tr_rows = soup.find_all("tr", attrs={"class": None})

            for tr in tr_rows[1:]:
                text = Tools.normalize_text_2(tr.get_text()).split(" || ")

                dumped_holder = json.dumps(text[1] + f" - {text[2]}")

                (
                    share_holders[0]["data"].append(
                        {
                            "holder": text[1],
                            "holder_unicode_escape": dumped_holder.strip('"'),
                            "share": text[2],
                        }
                    )
                    if len(text) != 1 or len(text) != 0 and len(text) == 3
                    else None
                )
                (
                    share_holders[0]["for_graph"].append(
                        [text[1], float(text[2][0:-1]) if text[2] is not None else None]
                    )
                    if len(text) != 1 or len(text) != 0 and len(text) == 3
                    else None
                )

            return share_holders
        except Exception as e:
            print("ERROR:", e)
            return []

    def get_data(self, ticker: str = None, period: str = None):
        """
        **Parameters:**
        :param ticker:  str (e.g: 'AAPL' or 'TCSG')
        :param period:  str (e.g: 'year' or 'y' or 'quarter' or 'q')

        **Examples:**
        >>> api = SmartLabAPI()              # Create instance of SmartLabAPI
        >>> api.get_data('AAPL', 'year')     # For quarters information
        >>> api.get_data('AAPL', 'quarter')  # For years information

        **Returns:**
        :return: TotalData object
        """

        ticker = ticker.upper() if isinstance(ticker, str) else None

        if ticker is None:
            print(
                "Unexpected object was passed as a 'ticker', company's ticker must be passed instead(i.e: ROSN, TCSG). \nWhat's ticker? More: https://en.wikipedia.org/wiki/Ticker_symbol"
            )
            return None

        self.ticker = ticker

        if period is None or period not in [
            "year",
            "quarter",
            "y",
            "q",
            "yaer",
            "qurater",
        ]:
            print(
                "Unexpected object was passed as a 'period', 'year' or 'quarter' must be passed instead. \nNeed a help? More: https://en.wikipedia.org/wiki/Calendar_year"
            )
            return None

        url = None

        if period in ["year", "y", "yaer"]:
            url = f"https://smart-lab.ru/q/{ticker}/f/y/"

        if period in ["quarter", "q", "qurater"]:
            url = f"https://smart-lab.ru/q/{ticker}/f/q/"

        if url is None:
            print(
                f"Period '{period}' is incorrect. Please, make sure period is either 'year' or 'quarter'. \nAlso, you can specify only first letter of periods. \ne.g: 'y' - for 'year', 'q' - for 'quarter'."
            )
            return None

        # Initialize the BeautifulSoup object
        try:
            print("INFO:", "Using lxml for parsing")
            self.parser = BeautifulSoup(requests.get(url).text, "lxml")

        except ImportError as e:
            print("WARNING: Using html.parser instead")
            self.parser = BeautifulSoup(requests.get(url).text, "html.parser")

        # Assign the instant to a variable
        soup = self.parser

        # Get years
        years = self.get_years()

        # Get currency
        currency = self.get_currency()

        # Get report_url
        report_url = self.get_report_url()

        # Get year_report_url
        year_report_url = self.get_year_report_url()

        # Get presentation_url
        presentation_url = self.get_presentation_url()

        # Get oil_production
        oil_production = self.get_oil_production()

        # Get oil_refining
        oil_refining = self.get_oil_refining()

        # Get gas_production
        gas_production = self.get_gas_production()

        # Get revenue
        revenue = self.get_revenue()

        # Get operating_income
        operating_income = self.get_operating_income()

        # Get ebitda
        ebitda = self.get_ebitda()

        # Get net_income
        net_income = self.get_net_income()

        # Get net_income_ns
        net_income_ns = self.get_net_income_ns()

        # Get ocf
        ocf = self.get_ocf()

        # Get capex
        capex = self.get_capex()

        # Get fcf
        fcf = self.get_fcf()

        # Get dividend_payout
        dividend_payout = self.get_dividend_payout()

        # Get dividend
        dividend = self.get_dividend()

        # Get div_yield
        div_yield = self.get_div_yield()

        # Get div_payout_ratio
        div_payout_ratio = self.get_div_payout_ratio()

        # Get opex
        opex = self.get_opex()

        # Get cost_of_production
        cost_of_production = self.get_cost_of_production()

        # Get r_and_d
        r_and_d = self.get_r_and_d()

        # Get employment_expenses
        employment_expenses = self.get_employment_expenses()

        # Get interest_expenses
        interest_expenses = self.get_interest_expenses()

        # Get assets
        assets = self.get_assets()

        # Get net_assets
        net_assets = self.get_net_assets()

        # Get debt
        debt = self.get_debt()

        # Get cash
        cash = self.get_cash()

        # Get net_debt
        net_debt = self.get_net_debt()

        # Get common_share
        common_share = self.get_common_share()

        # Get number_of_shares
        number_of_shares = self.get_number_of_shares()

        # Get free_float
        free_float = self.get_free_float()

        # Get market_cap
        market_cap = self.get_market_cap()

        # Get ev
        ev = self.get_ev()

        # Get book_value
        book_value = self.get_book_value()

        # Get eps
        eps = self.get_eps()

        # Get fcf_share
        fcf_share = self.get_fcf_share()

        # Get bv_share
        bv_share = self.get_bv_share()

        # Get ebitda_margin
        ebitda_margin = self.get_ebitda_margin()

        # Get net_margin
        net_margin = self.get_net_margin()

        # Get fcf_yield
        fcf_yield = self.get_fcf_yield()

        # Get roe
        roe = self.get_roe()

        # Get roa
        roa = self.get_roa()

        # Get p_e
        p_e = self.get_p_e()

        # Get p_s
        p_s = self.get_p_s()

        # Get p_bv
        p_bv = self.get_p_bv()

        # Get ev_ebitda
        ev_ebitda = self.get_ev_ebitda()

        # Get debt_ebitda
        debt_ebitda = self.get_debt_ebitda()

        # Get employees
        employees = self.get_employees()

        # Get labour_productivity
        labour_productivity = self.get_labour_productivity()

        # Get expenses_per_employee
        expenses_per_employee = self.get_expenses_per_employee()

        # Get r_and_d_capex
        r_and_d_capex = self.get_r_and_d_capex()

        # Get capex_revenue
        capex_revenue = self.get_capex_revenue()

        # Get irr
        irr = self.get_irr()

        # Get share_holders
        share_holders = self.get_share_holders()

        total_data = TotalData(
            Years(years, ["Периоды", "Время", "Года", "Periods", "Dates", "Years"]),
            Currency(currency, ["Валюта", "Currency"]),
            ReportUrl(
                report_url, ["Финансовый отчет", "Financial report", "report url"]
            ),
            YearReportUrl(
                year_report_url,
                [
                    "Годовой отчет",
                    "Годовой финансовый отчет",
                    "Year report url",
                    "Year financial report",
                    "Year financial report url",
                ],
            ),
            PresentationUrl(
                presentation_url,
                ["Презентация", "Presentation", "presentation url"],
            ),
            OilProduction(oil_production, ["Добыча нефти", "Oil production"]),
            OilRefining(oil_refining, ["Переработка нефти", "Oil refining"]),
            GasProduction(gas_production, ["Добыча газа", "Gas production"]),
            Revenue(revenue, ["Выручка", "Доходы", "Revenue"]),
            OperatingIncome(
                operating_income, ["Операционная прибыль", "Operating Income"]
            ),
            Ebitda(ebitda, ["ebitda", "Ebitda", "EBITDA"]),
            NetIncome(net_income, ["Чистая прибыль", "Net Income"]),
            NetIncomeNS(net_income_ns, ["Чистая прибыль н/с", "Net Income N/S"]),
            Ocf(ocf, ["Операционный денежный поток", "Operating Cash Flow (OCF)"]),
            Capex(
                capex,
                [
                    "Сумма операционных расходов",
                    "capex",
                    "Capital expenditure (Capex)",
                ],
            ),
            Fcf(fcf, ["Свободный денежный поток (FCF)", "Free Cash Flow (FCF)"]),
            DividendPayout(
                dividend_payout,
                ["Див. выплата", "Выплата дивидендов", "Dividend Payout"],
            ),
            Dividend(dividend, ["Дивиденд", "Dividend"]),
            DivYield(div_yield, ["Див. доход, ао", "Dividend yield"]),
            DivPayoutRatio(
                div_payout_ratio,
                ["Дивиденды/прибыль", "Div Payout Ratio", "Dividend/Payout ratio"],
            ),
            Opex(opex, ["Опер. расходы", "Operational expenditure", "Opex"]),
            CostOfProduction(
                cost_of_production, ["Себестоимость", "Cost of production"]
            ),
            RandD(r_and_d, ["НИОКР", "research and development", "R&D"]),
            EmploymentExpenses(
                employment_expenses, ["Расход на персонал", "Employment expenses"]
            ),
            InterestExpenses(
                interest_expenses, ["Процентные расходы", "Interest expenses"]
            ),
            Assets(assets, ["Активы", "Assets"]),
            NetAssets(net_assets, ["Чистые активы", "Net assets"]),
            Debt(debt, ["Долг", "Debt"]),
            Cash(cash, ["Наличность", "Cash"]),
            NetDebt(net_debt, ["Чистый долг", "Net debt"]),
            CommonShare(common_share, ["Цена акции ао", "Common share"]),
            NumberOfShares(number_of_shares, ["Число акций ао", "Number of shares"]),
            FreeFloat(free_float, ["Free Float"]),
            MarketCap(market_cap, ["Капитализация", "Market cap"]),
            EV(ev, ["EV"]),
            BookValue(book_value, ["Баланс стоимость", "Book value"]),
            Eps(eps, ["EPS"]),
            FcfShare(fcf_share, ["FCF/акцию", "FCF/share"]),
            BvShare(bv_share, ["BV/акцию", "BV/share"]),
            EbitdaMargin(ebitda_margin, ["Рентаб. EBITDA", "Ebitda margin"]),
            NetMargin(net_margin, ["Чистая рентаб.", "Net margin"]),
            FcfYield(fcf_yield, ["Доходность FCF", "FCF yield"]),
            Roe(roe, ["ROE"]),
            Roa(roa, ["ROA"]),
            PE(p_e, ["P/E"]),
            PS(p_s, ["P/S"]),
            PBV(p_bv, ["P/BV"]),
            EvEbitda(ev_ebitda, ["EV/EBITDA"]),
            DebtEbitda(debt_ebitda, ["Долг/EBITDA", "Debt/EBITDA"]),
            Employees(employees, ["Персонал", "Employees"]),
            LabourProductivity(
                labour_productivity,
                ["Производительность труда", "Labour productivity"],
            ),
            ExpensesPerEmployee(
                expenses_per_employee, ["Расходы/чел/год", "Expenses per employee"]
            ),
            RDcapex(r_and_d_capex, ["R&D/Capex"]),
            CapexRevenue(capex_revenue, ["CAPEX/Выручка", "CAPEX/Revenue"]),
            IRR(irr, ["IR Рейтинг", "IR Rating"]),
            ShareHolders(
                for_graph=share_holders[0]["for_graph"],
                data=share_holders[0]["data"],
                aliases=[
                    "Держатель акции",
                    "Структура и состав акционеров",
                    "Share holder",
                ],
            ),
        )

        print(
            "\n\nWARNING: If function returned absolutely empty list, then it means that there is no data for this company. \nPlease, make sure the company ticker you passed is correct and exists.\n\n"
        )
        return total_data

    def get_companies_names(self):
        """
        **Examples:**
        >>> api = SmartLabAPI()         # Create instance of SmartLabAPI
        >>> api.get_companies_names()     # To get all company names from smart-lab.ru

        **Returns:**
        :return: list
        """

        url = "https://smart-lab.ru/q/shares/"

        resp = requests.get(url).text
        soup = BeautifulSoup(resp, "lxml")

        all_companies = soup.find_all("tr", attrs={"class": None})
        tds = []

        for company in all_companies[1:]:
            temp_tds = company.find_all("td")

            tds.append([temp_tds[2].get_text(), temp_tds[3].get_text()])

        if tds is None or len(tds) == 0:
            return None

        return tds

    def get_auto_complete_values(self, value):
        try:
            resp = requests.get(
                f"https://smart-lab.ru/forum/ajaxsearchticker/?reports=1&value={value}"
            ).json()
            return resp
        except Exception as e:
            return None
