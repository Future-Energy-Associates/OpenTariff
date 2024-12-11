import datetime
import enum
from pydantic import BaseModel, Field


class DayOfWeek(int, enum.Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    ALL = 0


class Fuel(str, enum.Enum):
    electricity = "electricity"
    gas = "gas"
    both = "both"


class RateType(str, enum.Enum):
    single_rate = "single_rate"
    time_of_use_static = "time_of_use_static"
    time_of_use_dynamic = "time_of_use_dynamic"
    demand_tiered = "demand_tiered"


class TCRBand(str, enum.Enum):
    BAND_1 = "1"
    BAND_2 = "2"
    BAND_3 = "3"
    BAND_4 = "4"


class TariffType(str, enum.Enum):
    fixed = "fixed"
    variable = "variable"

class ExitFeeType(str, enum.Enum):
    fixed = "fixed"
    perc_of_balance = "perc_of_contract_balance"

class PaymentMethod(str, enum.Enum):
    direct_debit = "direct_debit"
    prepayment = "prepayment"
    cash_cheque = "cash_cheque"

class OtherProductsType(str, enum.Enum):
    utility = "utility"
    physical_asset = "physical_asset"

class OtherProducts(BaseModel):
    type: OtherProductsType
    name: str
    description: str | None = None


class ProductAttributes(BaseModel):
    smart: bool | None = None
    ev: bool | None = None
    exclusive: bool | None = None
    retention: bool | None = None
    acquisition: bool | None = None
    collective_switch: bool | None = None
    green_percentage: float | None = None
    bundled_products: list[OtherProducts] | None = None


class Product(BaseModel):
    name: str
    domestic: bool
    description: str | None = None
    type: TariffType | None = None
    available_from: datetime.datetime | None = None
    available_to: datetime.datetime | None = None
    attributes: ProductAttributes | None = None


class Tariff(BaseModel):
    dno_region: int = Field(..., ge=10, le=23)
    rate_type: RateType 
    fuel_type: Fuel 
    payment_method: PaymentMethod
    tcr_band: TCRBand | None = None
    standing_charge: float
    contract_length_months: int | None = None
    end_date: datetime.date | None = None
    exit_fee_type: ExitFeeType | None = None
    exit_fee_value: float | None = None

class RateBase(BaseModel):
    unit_rate: float = Field(..., gt=0, lt=100)
    valid_from: datetime.datetime | None = None
    valid_to: datetime.datetime | None = None


class SingleRate(RateBase):
    pass


class TimeofUseRateStatic(RateBase):
    time_from: datetime.time
    time_to: datetime.time
    day_of_week: DayOfWeek = DayOfWeek.ALL
    month_from: int = Field(..., ge=1, le=12)
    month_to: int = Field(..., ge=1, le=12)

class TimeOfUseRateDynamic(RateBase):
    datetime: datetime.datetime
    dst: bool | None = Field(default=None)

