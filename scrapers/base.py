"""Common abstractions shared by real-estate scrapers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence


Record = Dict[str, Optional[str]]


@dataclass
class ScraperResult:
    """Container for scraper results and accompanying metadata."""

    records: List[Record] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def extend(self, other: "ScraperResult") -> None:
        self.records.extend(other.records)
        self.warnings.extend(other.warnings)
        self.errors.extend(other.errors)
        self.metadata.update(other.metadata)


class BaseScraper:
    """Base class for individual platform scrapers."""

    #: Identifier used in CLI.
    slug: str = "base"

    #: Human readable platform name.
    name: str = "Base platform"

    #: Short description used in help output.
    description: str = ""

    #: Information about polite crawling practices for the platform.
    rate_limit_info: str = "Neuvedeno"

    #: Whether the scraper natively supports crawling the entire catalogue.
    supports_full_scan: bool = False

    def scrape(
        self,
        *,
        max_pages: Optional[int] = None,
        full_scan: bool = False,
        **kwargs,
    ) -> ScraperResult:
        """Execute scraping job.

        Args:
            max_pages: Optional explicit page limit.
            full_scan: If ``True`` the scraper should attempt to walk the
                complete catalogue, ignoring default limits.

        Returns:
            :class:`ScraperResult` instance.
        """

        raise NotImplementedError

    @staticmethod
    def normalise_records(records: Iterable[Record]) -> List[Record]:
        """Normalise records to a common schema used across platforms."""

        normalised: List[Record] = []
        for record in records:
            normalised.append(
                {
                    "zdroj": record.get("zdroj"),
                    "jmeno_maklere": record.get("jmeno_maklere"),
                    "telefon": record.get("telefon"),
                    "email": record.get("email"),
                    "realitni_kancelar": record.get("realitni_kancelar"),
                    "kraj": record.get("kraj"),
                    "mesto": record.get("mesto"),
                    "specializace": record.get("specializace"),
                    "detailni_informace": record.get("detailni_informace"),
                    "odkazy": record.get("odkazy"),
                }
            )
        return normalised


def merge_results(results: Sequence[ScraperResult]) -> ScraperResult:
    """Merge multiple :class:`ScraperResult` instances into one."""

    merged = ScraperResult()
    for result in results:
        merged.extend(result)
    return merged
