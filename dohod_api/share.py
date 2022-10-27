from dataclasses import dataclass
from typing import Union


@dataclass
class Detail:
    # Последняя дата торгов перед закрытием реестра (оценка)
    last_date_before_closing_registry: Union[str] | None
    
    # Прогноз прибыли
    profit_forecast: Union[str] | None
    
    # Доля прибыли направляемой на дивиденды (оценка)
    profit_share_allocated_to_dividends: Union[str, int, float] | None
    
    # Количество акций в обращении
    number_of_outstanding_shares: Union[str, int, float] | None
    
    # Общая сумма направляемая на дивиденды
    total_amount_allocated_for_dividends: Union[str, int, float] | None

    # Цена расчета доходности
    yield_calculation_price: Union[str, int, float] | None

    # DSI
    dsi: Union[str, int, float] | None

    # t (стабильность выплат)
    t: Union[str, int, float] | None

    # r (стабильность роста)
    r: Union[str, int, float] | None

    # Примечание
    note: Union[str] | None


@dataclass
class Share:
    name: Union[str] | None
    sector: Union[str] | None
    period: Union[str] | None
    payout: Union[str, int, float] | None
    check_mark_one: Union[bool] | None
    currency: Union[str] | None
    payout_yield: Union[str, int, float] | None
    registry_closing_date: Union[str] | None
    check_mark_two: Union[bool] | None
    capitalization: Union[str, int, float] | None
    dsi: Union[str, int, float] | None
    details: list[Detail] | None
    capitalization_size: Union[str, int, float] | None
    full_year: Union[str, int, float] | None
    recommended: Union[str, int, float] | None
