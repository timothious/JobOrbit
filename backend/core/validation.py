from typing import Annotated
from zoneinfo import available_timezones

from pydantic import AfterValidator, StringConstraints

CountryCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]
CurrencyCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]


def _valid_timezone(value: str) -> str:
    if value not in available_timezones():
        raise ValueError("must be a valid IANA timezone, e.g. Europe/Berlin")
    return value


Timezone = Annotated[str, AfterValidator(_valid_timezone)]
