from __future__ import annotations

import contextlib
from typing import Any, TypeAlias, TypeVar

from helpy._interfaces.asset.decimal_converter import (
    DecimalConversionNotANumberError,
    DecimalConverter,
)
from helpy.exceptions import HelpyError
from schemas.fields.assets import (
    AssetHbdHF26,
    AssetHbdLegacy,
    AssetHiveHF26,
    AssetHiveLegacy,
    AssetVestsHF26,
    AssetVestsLegacy,
)

AssetAmountT = int | float | str


class AssetError(HelpyError):
    """Base class for all asset related errors."""


class AssetLegacyInvalidFormatError(HelpyError):
    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid asset format: {value}")


class AssetAmountInvalidFormatError(HelpyError):
    def __init__(self, value: str) -> None:
        self.message = f"Invalid asset amount format: '{value}'. Should be a number."
        super().__init__(self.message)


class Asset:
    Hive: TypeAlias = AssetHiveHF26
    Test: TypeAlias = Hive
    Hbd: TypeAlias = AssetHbdHF26
    Tbd: TypeAlias = Hbd
    Vests: TypeAlias = AssetVestsHF26
    AnyT: TypeAlias = Hive | Hbd | Vests
    AssetPredicateT = TypeVar("AssetPredicateT", bound=Hive | Hbd | Vests)

    @classmethod
    def hive(cls, amount: AssetAmountT) -> Asset.Hive:
        """
        Create Hive asset.

        Args:
        ----
        amount: Amount of Hive.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Hive, amount)

    @classmethod
    def test(cls, amount: AssetAmountT) -> Asset.Test:
        """
        Create testnet Hive asset.

        Args:
        ----
        amount: Amount of Tests.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Test, amount)

    @classmethod
    def hbd(cls, amount: AssetAmountT) -> Asset.Hbd:
        """
        Create Hbd asset.

        Args:
        ----
        amount: Amount of Hbd.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Hbd, amount)

    @classmethod
    def tbd(cls, amount: AssetAmountT) -> Asset.Tbd:
        """
        Create testnet Hbd asset.

        Args:
        ----
        amount: Amount of TBD.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Tbd, amount)

    @classmethod
    def vests(cls, amount: AssetAmountT) -> Asset.Vests:
        """
        Create Vests asset.

        Args:
        ----
        amount: Amount of Vests.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        return cls.__create(Asset.Vests, amount)

    @classmethod
    def __create(cls, asset: type[AssetPredicateT] | type[AnyT], amount: AssetAmountT) -> AssetPredicateT:
        """
        Create asset.

        Args:
        ----
        asset: Asset type.
        amount: Amount of asset.

        Raises:
        ------
        AssetAmountInvalidFormatError: Raised when given amount is in invalid format.
        """
        try:
            amount = cls.__convert_amount_to_internal_representation(amount, asset)  # type: ignore[arg-type]
            return asset(amount=amount)  # type: ignore[return-value]
        except DecimalConversionNotANumberError as error:
            raise AssetAmountInvalidFormatError(str(amount)) from error

    @classmethod
    def resolve_symbol(cls, symbol: str) -> type[Asset.AnyT]:
        upper_symbol = symbol.upper()
        if upper_symbol in Asset.Hive.get_asset_information().symbol:
            return Asset.Hive
        if upper_symbol in Asset.Hbd.get_asset_information().symbol:
            return Asset.Hbd
        if upper_symbol in Asset.Vests.get_asset_information().symbol:
            return Asset.Vests
        raise ValueError(f"Unknown asset type: '{symbol}'")

    @classmethod
    def from_legacy(cls, value: str) -> Asset.AnyT:
        with contextlib.suppress(TypeError):
            return cls.Hive.from_legacy(value)
        with contextlib.suppress(TypeError):
            return cls.Hbd.from_legacy(value)
        with contextlib.suppress(TypeError):
            return cls.Vests.from_legacy(value)
        raise AssetLegacyInvalidFormatError(value)

    @classmethod
    def to_legacy(cls, asset: Asset.AnyT) -> str:
        return asset.as_legacy()

    @classmethod
    def pretty_amount(cls, asset: Asset.AnyT) -> str:
        return asset.pretty_amount()

    @staticmethod
    def __convert_amount_to_internal_representation(amount: AssetAmountT, precision: int | type[Asset.AnyT]) -> int:
        """
        Convert given amount to internal representation of integer value.

        Raises
        ------
        DecimalConversionNotANumberError: If given amount is not a valid number.
        """
        precision = precision if isinstance(precision, int) else precision.get_asset_information().precision
        amount_decimal = DecimalConverter.convert(amount, precision=precision)
        return int(amount_decimal * 10**precision)

    @staticmethod
    def assert_same_token(first: AnyT, other: AnyT, *, error_detail: str) -> None:
        if first.get_asset_information() != other.get_asset_information():
            raise TypeError(
                f"Can't {error_detail} assets with different tokens: `{first.get_asset_information()}` and"
                f" `{other.get_asset_information()}`."
            )

    @classmethod
    def assert_is_asset(cls, *other: Any, error_detail: str) -> None:
        for asset in other:
            if not isinstance(asset, cls.AnyT):  # type: ignore[arg-type]
                raise TypeError(f"Can't {error_detail} objects of type `{type(asset)}`.")

    class Range:
        """
        Represents a range of assets by providing the upper and lower bounds for a given value.

        It functions similarly to the built-in python `range(100, 110)` function, providing a convenient way to
        represent a range of assets within a specified value range.

        Usage:
            Asset.Range(lower_limit=Asset.hive(100), upper_limit=Asset.hive(110))

        :param lower_limit is required. When tolerance is given it acts as the value to which we refer when specifying
        the percentage range.
        :param tolerance: is defined as a positive number, which is a percentage of the upper and lower deviations e.g:
            asset = Asset.hive(100)
            Asset.Range(asset, tolerance=10) -> the range of this asset is from Asset.hive(90) to inclusive (100)

        Upper limit and tolerance should be used interchangeably.
        """

        def __init__(
            self,
            lower_limit: Asset.AnyT,
            upper_limit: Asset.AnyT | None = None,
            *,
            tolerance: int | float | None = None,
        ) -> None:
            if not upper_limit and not tolerance:
                raise TypeError("Range has to be specified with either `upper_limit` or `tolerance`")

            if upper_limit and tolerance:
                raise TypeError("Please choose only one option from `upper_limit` or `tolerance`")

            if tolerance and tolerance < 0:
                raise TypeError("`tolerance` should be given as an positive number")

            self.__lower_limit = lower_limit if upper_limit else lower_limit - (lower_limit * tolerance / 100)
            self.__upper_limit = upper_limit if upper_limit else lower_limit + (lower_limit * tolerance / 100)
            Asset.assert_is_asset(self.__lower_limit, self.__upper_limit, error_detail="create range on")
            Asset.assert_same_token(self.__lower_limit, self.__upper_limit, error_detail="create range on")
            assert self.__lower_limit < self.__upper_limit, "The upper limit cannot be greater than the lower limit"

        def __contains__(self, item: Asset.AnyT) -> bool:
            Asset.assert_is_asset(item, error_detail="check if asset is in range when")
            Asset.assert_same_token(item, self.__lower_limit, error_detail="check if asset is in range when")
            return self.__lower_limit <= item <= self.__upper_limit


class Hf26Asset(Asset):
    pass


class LegacyAsset(Asset):
    Hive: TypeAlias = AssetHiveLegacy
    Test: TypeAlias = Hive
    Hbd: TypeAlias = AssetHbdLegacy
    Tbd: TypeAlias = Hbd
    Vests: TypeAlias = AssetVestsLegacy
    AnyT: TypeAlias = Hive | Hbd | Vests


def convert_hf26_to_legacy(asset: type[Hf26Asset.AssetPredicateT]) -> Hf26Asset.AssetPredicateT:
    return Hf26Asset.to_legacy(asset)  # type: ignore


def convert_legacy_to_hf26(asset: LegacyAsset.AnyT) -> Hf26Asset.AnyT:
    return LegacyAsset.from_legacy(asset)
