# async_dohod_api.py
import aiohttp, requests
from dataclasses import dataclass
from bs4 import BeautifulSoup
from .share import Share

from types import SimpleNamespace, TracebackType
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    FrozenSet,
    Generator,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)


class AsyncClient:
    def __init__(self):
        self.url = "https://www.dohod.ru/ik/analytics/dividend"
        self.soup = None

    async def __aenter__(self) -> "AsyncClient":
        html = None
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                html = await resp.text()
        
        try:
            import lxml
            self.soup = BeautifulSoup(html, "lxml")        
        except ImportError:
            self.soup = BeautifulSoup(html, "html.parser")
            
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        print("Thanks for using 'Dohod.ru API' library")
        return None

    def normalize_text(self, text: str):
        text = text.strip().replace("\n", "").replace("\t", "") if text != "n/a" else None
        return text

    async def get_data_in_dataclasses(self, limit: int = 25) -> list[Share]:
        soup: BeautifulSoup = self.soup

        all_tr = soup.find_all("tr")[1:limit+1]
        shares = []
        dict_shares = []

        for tr in all_tr:
            dict_share = {'details': {}}
            all_td = tr.find_all("td")

            # need_index = [19, 12, 13, 14, 18, 7, 11, 15, 16, 17]
            # for index, td in enumerate(all_td):
            #     print('"', f"{index} td:", td, '"', end="\n\n\n")

            # break
            # all_td.pop(7)
            # all_td = all_td[:11]

            for index, td in enumerate(all_td):
                if index == 0:
                    dict_share["name"] = self.normalize_text(td.get_text())
                if index == 1:
                    dict_share["sector"] = self.normalize_text(td.get_text())
                if index == 2:
                    dict_share["period"] = self.normalize_text(td.get_text())
                if index == 3:
                    dict_share["payout"] = self.normalize_text(td.get_text())
                if index == 4:
                    check_mark_one = td.find("span")
                    dict_share["check_mark_one"] = True if check_mark_one else False
                if index == 5:
                    dict_share["currency"] = self.normalize_text(td.get_text())
                if index == 6:
                    dict_share["payout_yield"] = self.normalize_text(td.get_text())
                if index == 7:
                    dict_share["details"]['yield_calculation_price'] = f"{self.normalize_text(td.get_text())} руб." # Detail: Цена расчета доходности
                if index == 8:
                    dict_share["registry_closing_date"] = self.normalize_text(
                        td.get_text()
                    )
                if index == 9:
                    check_mark_two = td.find("span")
                    dict_share["check_mark_two"] = True if check_mark_two else False
                if index == 10:
                    dict_share["capitalization"] = self.normalize_text(td.get_text())
                if index == 11:
                    dict_share["dsi"] = self.normalize_text(td.get_text())
                    dict_share["details"]['dsi'] = self.normalize_text(td.get_text()) # Detail: DSI
                if index == 12:
                    dict_share["details"]['profit_forecast'] = f"{self.normalize_text(td.get_text())} млн. руб." # Detail: Прогноз прибыли
                if index == 13:
                    dict_share["details"]['profit_share_allocated_to_dividends'] = f"{self.normalize_text(td.get_text())}%" # Detail: Доля прибыли направляемой на дивиденды (оценка)
                if index == 14:
                    dict_share["details"]['number_of_outstanding_shares'] = f"{self.normalize_text(td.get_text())} млн. шт." # Detail: Количество акции в обращении
                if index == 15:
                    dict_share["details"]['t'] = self.normalize_text(td.get_text()) # Detail: t (Стабильность выплат)
                if index == 16:
                    dict_share["details"]['r'] = self.normalize_text(td.get_text()) # Detail: r (Стабильность роста)
                if index == 17:
                    dict_share['details']['note'] = self.normalize_text(td.get_text()) # Detail: Примечание (описание/текст)
                if index == 18:
                    dict_share['details']['total_amount_allocated_for_dividends'] = f"{self.normalize_text(td.get_text())} млн. руб." # Detail: Общая сумма направляемая на дивиденды
                if index == 19:
                        dict_share['details']['last_date_before_closing_registry'] = self.normalize_text(td.get_text()) # Последняя дата торгов перед закрытием реестра (оценка)

            shares.append(Share(**dict_share))

        return shares

    async def get_data_in_dict(self, limit: int = 25) -> list[dict]:
        try:
            soup: BeautifulSoup = self.soup

            all_tr = soup.find_all("tr")[1:limit+1]
            shares = []
            dict_shares = []

            for tr in all_tr:
                dict_share = {"details": {}}
                all_td = tr.find_all("td")
                # all_td.pop(7)
                # all_td = all_td[:11]

                for index, td in enumerate(all_td):
                    if index == 0:
                        dict_share["name"] = self.normalize_text(td.get_text())
                    if index == 1:
                        dict_share["sector"] = self.normalize_text(td.get_text())
                    if index == 2:
                        dict_share["period"] = self.normalize_text(td.get_text())
                    if index == 3:
                        dict_share["payout"] = self.normalize_text(td.get_text())
                    if index == 4:
                        check_mark_one = td.find("span")
                        dict_share["check_mark_one"] = True if check_mark_one else False
                    if index == 5:
                        dict_share["currency"] = self.normalize_text(td.get_text())
                    if index == 6:
                        dict_share["payout_yield"] = self.normalize_text(td.get_text())
                    if index == 7:
                        dict_share["details"]['yield_calculation_price'] = f"{self.normalize_text(td.get_text())} руб." # Detail: Цена расчета доходности
                    if index == 8:
                        dict_share["registry_closing_date"] = self.normalize_text(
                            td.get_text()
                        )
                    if index == 9:
                        check_mark_two = td.find("span")
                        dict_share["check_mark_two"] = True if check_mark_two else False
                    if index == 10:
                        dict_share["capitalization"] = self.normalize_text(td.get_text())
                    if index == 11:
                        dict_share["dsi"] = self.normalize_text(td.get_text())
                        dict_share["details"]['dsi'] = self.normalize_text(td.get_text()) # Detail: DSI
                    if index == 12:
                        dict_share["details"]['profit_forecast'] = f"{self.normalize_text(td.get_text())} млн. руб." # Detail: Прогноз прибыли
                    if index == 13:
                        dict_share["details"]['profit_share_allocated_to_dividends'] = f"{self.normalize_text(td.get_text())}%" # Detail: Доля прибыли направляемой на дивиденды (оценка)
                    if index == 14:
                        dict_share["details"]['number_of_outstanding_shares'] = f"{self.normalize_text(td.get_text())} млн. шт." # Detail: Количество акции в обращении
                    if index == 15:
                        dict_share["details"]['t'] = self.normalize_text(td.get_text()) # Detail: t (Стабильность выплат)
                    if index == 16:
                        dict_share["details"]['r'] = self.normalize_text(td.get_text()) # Detail: r (Стабильность роста)
                    if index == 17:
                        dict_share['details']['note'] = self.normalize_text(td.get_text()) # Detail: Примечание (описание/текст)
                    if index == 18:
                        dict_share['details']['total_amount_allocated_for_dividends'] = f"{self.normalize_text(td.get_text())} млн. руб." # Detail: Общая сумма направляемая на дивиденды
                    if index == 19:
                        dict_share['details']['last_date_before_closing_registry'] = self.normalize_text(td.get_text()) # Последняя дата торгов перед закрытием реестра (оценка)

                dict_shares.append(dict_share)

            return dict_shares
        except Exception as e:
            print("ERROR AT 195:", e)
            return []


# async def main():
#     async with AsyncClient() as client:
#         data = await client.get_data_in_dict()
#     return data


# import asyncio, pprint

# data = asyncio.run(main())
# pprint.pprint(data, indent=4)