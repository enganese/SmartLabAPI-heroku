from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class FullInfo:
    ticker: str
    data_type: Optional[str]
    title: str
    text: str
    url: str
    href: str


@dataclass
class FullData:
    name: str | None
    title: str | None
    categories: List[int] | list
    data: List[dict] | list


@dataclass
class FullDataDividend:
    name: str | None
    title: str | None
    categories: List[int] | List[str] | list
    dividend: list
    div_yield: list
    div_payout_ratio: list
    dividend_payout: list


@dataclass
class Years:
    values: List[str] | List[int]
    aliases: List[str]


@dataclass
class Currency:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class ReportUrl:
    values: List[str] | List[Any]
    aliases: List[str] | None


@dataclass
class YearReportUrl:
    values: List[str] | List[Any]
    aliases: List[str] | None


@dataclass
class PresentationUrl:
    values: List[str] | List[Any]
    aliases: List[str] | None


@dataclass
class OilProduction:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class OilRefining:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class GasProduction:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Revenue:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class OperatingIncome:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Ebitda:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class NetIncome:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class NetIncomeNS:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Ocf:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Capex:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Fcf:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class DividendPayout:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Dividend:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class DivYield:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class DivPayoutRatio:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Opex:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class CostOfProduction:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class RandD:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class EmploymentExpenses:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class InterestExpenses:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Assets:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class NetAssets:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Debt:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Cash:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class NetDebt:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class CommonShare:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class NumberOfShares:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class FreeFloat:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class MarketCap:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class EV:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class BookValue:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Eps:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class FcfShare:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class BvShare:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class EbitdaMargin:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class NetMargin:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class FcfYield:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Roe:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Roa:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class PE:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class PS:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class PBV:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class EvEbitda:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class DebtEbitda:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class Employees:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class LabourProductivity:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class ExpensesPerEmployee:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class RDcapex:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class CapexRevenue:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class ForChart:
    data: list


@dataclass
class SimpleData:
    holder: str
    holder_unicode_escape: str
    share: str


@dataclass
class IRR:
    values: List[str] | List[int] | List[float]
    aliases: List[str] | None


@dataclass
class ShareHolders:
    for_graph: List[ForChart]
    data: List[SimpleData]
    aliases: List[str] | None


class TotalData:
    def __init__(
        self,
        years: List[str] | List[int],
        currency: Currency,
        report_url: ReportUrl,
        year_report_url: YearReportUrl,
        presentation_url: PresentationUrl,
        oil_production: OilProduction,
        oil_refining: OilRefining,
        gas_production: GasProduction,
        revenue: Revenue,
        operating_income: OperatingIncome,
        ebitda: Ebitda,
        net_income: NetIncome,
        net_income_ns: NetIncomeNS,
        ocf: Ocf,
        capex: Capex,
        fcf: Fcf,
        dividend_payout: DividendPayout,
        dividend: Dividend,
        div_yield: DivYield,
        div_payout_ratio: DivPayoutRatio,
        opex: Opex,
        cost_of_production: CostOfProduction,
        r_and_d: RandD,
        employment_expenses: EmploymentExpenses,
        interest_expenses: InterestExpenses,
        assets: Assets,
        net_assets: NetAssets,
        debt: Debt,
        cash: Cash,
        net_debt: NetDebt,
        common_share: CommonShare,
        number_of_shares: NumberOfShares,
        free_float: FreeFloat,
        market_cap: MarketCap,
        ev: EV,
        book_value: BookValue,
        eps: Eps,
        fcf_share: FcfShare,
        bv_share: BvShare,
        ebitda_margin: EbitdaMargin,
        net_margin: NetMargin,
        fcf_yield: FcfYield,
        roe: Roe,
        roa: Roa,
        p_e: PE,
        p_s: PS,
        p_bv: PBV,
        ev_ebitda: EvEbitda,
        debt_ebitda: DebtEbitda,
        employees: Employees,
        labour_productivity: LabourProductivity,
        expenses_per_employee: ExpensesPerEmployee,
        r_and_d_capex: RDcapex,
        capex_revenue: CapexRevenue,
        irr: IRR,
        share_holders: ShareHolders,
    ):
        self.years: List[str] | List[int] = years
        self.currency: Currency = currency
        self.report_url: ReportUrl = report_url
        self.year_report_url: YearReportUrl = year_report_url
        self.presentation_url: PresentationUrl = presentation_url
        self.oil_production: OilProduction = oil_production
        self.oil_refining: OilRefining = oil_refining
        self.gas_production: GasProduction = gas_production
        self.revenue: Revenue = revenue
        self.operating_income: OperatingIncome = operating_income
        self.ebitda: Ebitda = ebitda
        self.net_income: NetIncome = net_income
        self.net_income_ns: NetIncomeNS = net_income_ns
        self.ocf: Ocf = ocf
        self.capex: Capex = capex
        self.fcf: Fcf = fcf
        self.dividend_payout: DividendPayout = dividend_payout
        self.dividend: Dividend = dividend
        self.div_yield: DivYield = div_yield
        self.div_payout_ratio: DivPayoutRatio = div_payout_ratio
        self.opex: Opex = opex
        self.cost_of_production: CostOfProduction = cost_of_production
        self.r_and_d: RandD = r_and_d
        self.employment_expenses: EmploymentExpenses = employment_expenses
        self.interest_expenses: InterestExpenses = interest_expenses
        self.assets: Assets = assets
        self.net_assets: NetAssets = net_assets
        self.debt: Debt = debt
        self.cash: Cash = cash
        self.net_debt: NetDebt = net_debt
        self.common_share: CommonShare = common_share
        self.number_of_shares: NumberOfShares = number_of_shares
        self.free_float: FreeFloat = free_float
        self.market_cap: MarketCap = market_cap
        self.ev: EV = ev
        self.book_value: BookValue = book_value
        self.eps: Eps = eps
        self.fcf_share: FcfShare = fcf_share
        self.bv_share: BvShare = bv_share
        self.ebitda_margin: EbitdaMargin = ebitda_margin
        self.net_margin: NetMargin = net_margin
        self.fcf_yield: FcfYield = fcf_yield
        self.roe: Roe = roe
        self.roa: Roa = roa
        self.p_e: PE = p_e
        self.p_s: PS = p_s
        self.p_bv: PBV = p_bv
        self.ev_ebitda: EvEbitda = ev_ebitda
        self.debt_ebitda: DebtEbitda = debt_ebitda
        self.employees: Employees = employees
        self.labour_productivity: LabourProductivity = labour_productivity
        self.expenses_per_employee: ExpensesPerEmployee = expenses_per_employee
        self.r_and_d_capex: RDcapex = r_and_d_capex
        self.capex_revenue: CapexRevenue = capex_revenue
        self.irr = IRR = irr
        self.share_holders: ShareHolders = share_holders

    def __iter__(self):
        return iter(
            [
                self.years,
                self.currency,
                self.report_url,
                self.year_report_url,
                self.presentation_url,
                self.oil_production,
                self.oil_refining,
                self.gas_production,
                self.revenue,
                self.operating_income,
                self.ebitda,
                self.net_income,
                self.net_income_ns,
                self.ocf,
                self.capex,
                self.fcf,
                self.dividend_payout,
                self.dividend,
                self.div_yield,
                self.div_payout_ratio,
                self.opex,
                self.cost_of_production,
                self.r_and_d,
                self.employment_expenses,
                self.interest_expenses,
                self.assets,
                self.net_assets,
                self.debt,
                self.cash,
                self.net_debt,
                self.common_share,
                self.number_of_shares,
                self.free_float,
                self.market_cap,
                self.ev,
                self.book_value,
                self.eps,
                self.fcf_share,
                self.bv_share,
                self.ebitda_margin,
                self.net_margin,
                self.fcf_yield,
                self.roe,
                self.roa,
                self.p_e,
                self.p_s,
                self.p_bv,
                self.ev_ebitda,
                self.debt_ebitda,
                self.employees,
                self.labour_productivity,
                self.expenses_per_employee,
                self.r_and_d_capex,
                self.capex_revenue,
                self.irr,
                self.share_holders,
            ]
        )
