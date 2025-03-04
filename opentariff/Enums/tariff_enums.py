from opentariff.Enums.base_enums import EnumBase


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

    class TCRBandType(str, EnumBase):
        line_loss = "line_loss"
        consumption = "consumption"
