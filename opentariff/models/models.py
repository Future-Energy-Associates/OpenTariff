from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class EnumBase:
    """Base class for enums to ensure consistent string representation"""

    @classmethod
    def values(cls) -> list:
        return [member.value for member in cls]


class DayOfWeek(int, EnumBase):
    ALL = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class ProductEnums:
    """Group product-related enums"""

    class TariffType(str, EnumBase):
        FIXED = "fixed"
        VARIABLE = "variable"

    class OtherProductsType(str, EnumBase):
        UTILITY = "utility"
        PHYSICAL_ASSET = "physical_asset"


class TariffEnums:
    """Group tariff-related enums"""

    class Fuel(str, EnumBase):
        ELECTRICITY = "electricity"
        GAS = "gas"
        BOTH = "both"

    class RateType(str, EnumBase):
        SINGLE_RATE = "single_rate"
        TIME_OF_USE_STATIC = "time_of_use_static"
        TIME_OF_USE_DYNAMIC = "time_of_use_dynamic"
        DEMAND_TIERED = "demand_tiered"

    class TCRBand(str, EnumBase):
        BAND_1 = "1"
        BAND_2 = "2"
        BAND_3 = "3"
        BAND_4 = "4"

    class ExitFeeType(str, EnumBase):
        FIXED = "fixed"
        PERC_OF_BALANCE = "perc_of_contract_balance"

    class PaymentMethod(str, EnumBase):
        DIRECT_DEBIT = "direct_debit"
        PREPAYMENT = "prepayment"
        CASH_CHEQUE = "cash_cheque"


class OtherProduct(BaseModel):
    """Represents additional products that can be bundled with tariffs"""

    model_config = ConfigDict(frozen=True)

    type: ProductEnums.OtherProductsType
    name: str
    description: Optional[str] = None


class ProductAttributes(BaseModel):
    """Product-specific attributes"""

    model_config = ConfigDict(frozen=True)

    smart: Optional[bool] = None
    ev: Optional[bool] = None
    exclusive: Optional[bool] = None
    retention: Optional[bool] = None
    acquisition: Optional[bool] = None
    collective_switch: Optional[bool] = None
    green_percentage: Optional[float] = Field(None, ge=0, le=100)
    bundled_products: Optional[list[OtherProduct]] = None


class Product(BaseModel):
    """Core product information"""

    model_config = ConfigDict(frozen=True)

    name: str
    domestic: bool
    description: Optional[str] = None
    type: Optional[ProductEnums.TariffType] = None
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None
    attributes: Optional[ProductAttributes] = None

    @field_validator("available_to")
    @classmethod
    def validate_available_to(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v and info.data.get("available_from") and v <= info.data["available_from"]:
            raise ValueError("available_to must be after available_from")
        return v


class Rate(BaseModel):
    """Unified rate model for all rate types"""

    model_config = ConfigDict(frozen=True)

    rate_type: TariffEnums.RateType
    unit_rate: Decimal = Field(..., gt=0, lt=100)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None

    # Fields for time-of-use static rates
    time_from: Optional[time] = None
    time_to: Optional[time] = None
    day_of_week: Optional[DayOfWeek] = None
    month_from: Optional[int] = Field(None, ge=1, le=12)
    month_to: Optional[int] = Field(None, ge=1, le=12)

    # Fields for dynamic rates
    rate_datetime: Optional[datetime] = None
    dst: Optional[bool] = None

    @field_validator("valid_to")
    @classmethod
    def validate_valid_to(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v and info.data.get("valid_from") and v <= info.data["valid_from"]:
            raise ValueError("valid_to must be after valid_from")
        return v

    @field_validator("time_to")
    @classmethod
    def validate_time_to(cls, v: Optional[time], info) -> Optional[time]:
        if v and info.data.get("time_from") and v <= info.data["time_from"]:
            raise ValueError("time_to must be after time_from")
        return v

    @field_validator("month_to")
    @classmethod
    def validate_month_to(cls, v: Optional[int], info) -> Optional[int]:
        if v and info.data.get("month_from") and v < info.data["month_from"]:
            raise ValueError("month_to must be after or equal to month_from")
        return v

    @field_validator("rate_type")
    @classmethod
    def validate_rate_fields(
        cls, v: TariffEnums.RateType, info
    ) -> TariffEnums.RateType:
        """Validate that required fields are present based on rate type"""
        if v == TariffEnums.RateType.TIME_OF_USE_STATIC:
            if not all(
                [
                    info.data.get("time_from"),
                    info.data.get("time_to"),
                    info.data.get("month_from"),
                    info.data.get("month_to"),
                ]
            ):
                raise ValueError(
                    "time_of_use_static rates require time_from, time_to, month_from, and month_to"
                )
        elif v == TariffEnums.RateType.TIME_OF_USE_DYNAMIC:
            if not info.data.get("rate_datetime"):
                raise ValueError("time_of_use_dynamic rates require rate_datetime")
        return v


class Tariff(BaseModel):
    """Core tariff information"""

    model_config = ConfigDict(frozen=True)

    dno_region: int = Field(..., ge=10, le=23)
    rate_type: TariffEnums.RateType
    fuel_type: TariffEnums.Fuel
    payment_method: TariffEnums.PaymentMethod
    tcr_band: Optional[TariffEnums.TCRBand] = None
    standing_charge: Decimal = Field(..., ge=0)
    contract_length_months: Optional[int] = Field(None, gt=0)
    end_date: Optional[date] = None
    exit_fee_type: Optional[TariffEnums.ExitFeeType] = None
    exit_fee_value: Optional[Decimal] = Field(None, ge=0)
    rates: list[Rate]

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date]) -> Optional[date]:
        if v and v < date.today():
            raise ValueError("end_date cannot be in the past")
        return v

    @field_validator("rates")
    @classmethod
    def validate_rates(cls, v: list[Rate], info) -> list[Rate]:
        if not v:
            raise ValueError("tariff must have at least one rate")
        if "rate_type" in info.data:
            for rate in v:
                if rate.rate_type != info.data["rate_type"]:
                    raise ValueError("all rates must match tariff rate_type")
        return v

    @field_validator("exit_fee_value")
    @classmethod
    def validate_exit_fee(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        if v is not None and not info.data.get("exit_fee_type"):
            raise ValueError(
                "exit_fee_type is required when exit_fee_value is provided"
            )
        return v
