"""
DeDe - Search Validator

Validates the topical relevance and technical integrity of web-search
results before they enter DeDe's cognitive reasoning pipeline.

This layer does not decide whether a source is true, neutral or reliable.
Those questions belong to the semantic source-analysis layer.
"""

from __future__ import annotations

import ipaddress
import re
import unicodedata
from typing import Any
from urllib.parse import urlparse


class SearchValidator:

    name = "search_validator"

    def validate(
        self,
        query: str,
        search_result: dict[str, Any],
        concepts: list[str] | None = None,
    ) -> dict[str, Any]:

        raw_results = search_result.get(
            "results",
            [],
        )

        concepts = concepts or []

        results = [
            item
            for item in raw_results
            if isinstance(item, dict)
        ]

        if not results:
            return self._empty_result(
                query=query,
                concepts=concepts,
                status="empty",
                summary="No search results to validate.",
            )

        anchors = self._anchors(
            query=query,
            concepts=concepts,
        )

        if not anchors:
            return self._empty_result(
                query=query,
                concepts=concepts,
                status="no_anchors",
                summary="No conceptual anchors available.",
            )

        scored_results = []
        accepted_results = []
        rejected_results = []

        for item in results:

            title = str(
                item.get("title", "")
                or ""
            ).strip()

            snippet = str(
                item.get("snippet", "")
                or ""
            ).strip()

            url = str(
                item.get("url", "")
                or ""
            ).strip()

            searchable_text = " ".join(
                [
                    title,
                    snippet,
                ]
            )

            normalized_text = self._normalize(
                searchable_text
            )

            matched = [
                anchor
                for anchor in anchors
                if self._normalize(anchor)
                in normalized_text
            ]

            topical_score = (
                len(matched) / len(anchors)
                if anchors
                else 0.0
            )

            url_validation = (
                self._validate_url(url)
            )

            topical_relevance = (
                topical_score >= 0.20
            )

            admissible = (
                url_validation["is_valid"]
                and topical_relevance
            )

            validation_reasons = []

            if not url_validation["is_valid"]:
                validation_reasons.append(
                    url_validation["reason"]
                )

            if not topical_relevance:
                validation_reasons.append(
                    "The result has insufficient topical relevance."
                )

            scored_item = {
                "title": title,
                "url": url,
                "score": round(
                    topical_score,
                    3,
                ),
                "topical_score": round(
                    topical_score,
                    3,
                ),
                "matched_concepts": matched,
                "url_valid": url_validation[
                    "is_valid"
                ],
                "hostname": url_validation[
                    "hostname"
                ],
                "admissible": admissible,
                "validation_reasons": (
                    validation_reasons
                ),
            }

            scored_results.append(
                scored_item
            )

            result_with_validation = {
                **item,
                "validation": {
                    "topical_score": round(
                        topical_score,
                        3,
                    ),
                    "matched_concepts": matched,
                    "url_valid": url_validation[
                        "is_valid"
                    ],
                    "hostname": url_validation[
                        "hostname"
                    ],
                    "admissible": admissible,
                    "reasons": validation_reasons,
                },
            }

            if admissible:
                accepted_results.append(
                    result_with_validation
                )
            else:
                rejected_results.append(
                    result_with_validation
                )

        accepted_scores = [
            item["topical_score"]
            for item in scored_results
            if item["admissible"]
        ]

        best_score = (
            max(accepted_scores)
            if accepted_scores
            else 0.0
        )

        average_score = (
            sum(accepted_scores)
            / len(accepted_scores)
            if accepted_scores
            else 0.0
        )

        relevance = max(
            best_score,
            average_score,
        )

        is_relevant = bool(
            accepted_results
            and (
                best_score >= 0.34
                or average_score >= 0.20
            )
        )

        # Critical pipeline protection:
        # only technically valid and topically relevant results
        # may continue toward summarization and final display.
        search_result["results"] = (
            accepted_results
        )

        search_result[
            "rejected_results"
        ] = rejected_results

        search_result[
            "raw_result_count"
        ] = len(results)

        search_result[
            "accepted_result_count"
        ] = len(accepted_results)

        search_result[
            "rejected_result_count"
        ] = len(rejected_results)

        return {
            "validator": self.name,
            "status": "ready",
            "query": query,
            "concepts": concepts,
            "anchors": anchors,
            "relevance": round(
                relevance,
                3,
            ),
            "is_relevant": is_relevant,
            "best_score": round(
                best_score,
                3,
            ),
            "average_score": round(
                average_score,
                3,
            ),
            "raw_result_count": len(
                results
            ),
            "accepted_result_count": len(
                accepted_results
            ),
            "rejected_result_count": len(
                rejected_results
            ),
            "scored_results": (
                scored_results
            ),
            "accepted_results": (
                accepted_results
            ),
            "rejected_results": (
                rejected_results
            ),
            "summary": (
                f"{len(accepted_results)} of "
                f"{len(results)} search results passed "
                "technical and topical validation. "
                "This validation does not establish "
                "the truth or neutrality of their claims."
            ),
        }

    # --------------------------------------------------
    # Empty Result
    # --------------------------------------------------

    def _empty_result(
        self,
        query: str,
        concepts: list[str],
        status: str,
        summary: str,
    ) -> dict[str, Any]:

        return {
            "validator": self.name,
            "status": status,
            "query": query,
            "concepts": concepts,
            "anchors": [],
            "relevance": 0.0,
            "is_relevant": False,
            "best_score": 0.0,
            "average_score": 0.0,
            "raw_result_count": 0,
            "accepted_result_count": 0,
            "rejected_result_count": 0,
            "scored_results": [],
            "accepted_results": [],
            "rejected_results": [],
            "summary": summary,
        }

    # --------------------------------------------------
    # Technical URL Validation
    # --------------------------------------------------

    def _validate_url(
        self,
        url: str,
    ) -> dict[str, Any]:

        if not url:
            return {
                "is_valid": False,
                "hostname": "",
                "reason": (
                    "The result has no URL."
                ),
            }

        try:
            parsed = urlparse(url)
        except Exception:
            return {
                "is_valid": False,
                "hostname": "",
                "reason": (
                    "The URL could not be parsed."
                ),
            }

        scheme = (
            parsed.scheme
            or ""
        ).lower()

        hostname = (
            parsed.hostname
            or ""
        ).lower().strip(".")

        if scheme not in {
            "http",
            "https",
        }:
            return {
                "is_valid": False,
                "hostname": hostname,
                "reason": (
                    "The URL does not use HTTP or HTTPS."
                ),
            }

        if not hostname:
            return {
                "is_valid": False,
                "hostname": "",
                "reason": (
                    "The URL has no valid hostname."
                ),
            }

        if hostname in {
            "localhost",
            "localhost.localdomain",
        }:
            return {
                "is_valid": False,
                "hostname": hostname,
                "reason": (
                    "Local addresses are not admissible "
                    "as external sources."
                ),
            }

        if self._is_private_ip(
            hostname
        ):
            return {
                "is_valid": False,
                "hostname": hostname,
                "reason": (
                    "Private or reserved network addresses "
                    "are not admissible as external sources."
                ),
            }

        if not self._valid_hostname(
            hostname
        ):
            return {
                "is_valid": False,
                "hostname": hostname,
                "reason": (
                    "The hostname is malformed."
                ),
            }

        if self._contains_embedded_url(
            parsed.path,
            parsed.query,
        ):
            return {
                "is_valid": False,
                "hostname": hostname,
                "reason": (
                    "The URL path contains another disguised "
                    "or embedded web address."
                ),
            }

        return {
            "is_valid": True,
            "hostname": hostname,
            "reason": "",
        }

    def _valid_hostname(
        self,
        hostname: str,
    ) -> bool:

        if len(hostname) > 253:
            return False

        labels = hostname.split(".")

        if len(labels) < 2:
            return False

        hostname_label = re.compile(
            r"^[a-z0-9]"
            r"(?:[a-z0-9-]{0,61}[a-z0-9])?$",
            flags=re.IGNORECASE,
        )

        return all(
            hostname_label.fullmatch(label)
            for label in labels
        )

    def _is_private_ip(
        self,
        hostname: str,
    ) -> bool:

        try:
            address = ipaddress.ip_address(
                hostname
            )
        except ValueError:
            return False

        return bool(
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        )

    def _contains_embedded_url(
        self,
        path: str,
        query: str,
    ) -> bool:

        combined = (
            f"{path} {query}"
        ).lower()

        embedded_patterns = [
            r"https?://",
            r"https?[-_:]+(?:www[.-])?",
            r"(?:^|[/=_-])www[.-]",
        ]

        return any(
            re.search(
                pattern,
                combined,
                flags=re.IGNORECASE,
            )
            for pattern in embedded_patterns
        )

    # --------------------------------------------------
    # Build Search Anchors
    # --------------------------------------------------

    def _anchors(
        self,
        query: str,
        concepts: list[str],
    ) -> list[str]:

        anchors = []

        for concept in concepts:
            concept = str(
                concept
            ).strip()

            if self._is_usable_anchor(
                concept
            ):
                anchors.append(
                    concept
                )

        if not anchors:
            anchors = (
                self._extract_query_terms(
                    query
                )
            )

        return self._deduplicate(
            anchors
        )[:5]

    # --------------------------------------------------
    # Extract Fallback Query Terms
    # --------------------------------------------------

    def _extract_query_terms(
        self,
        query: str,
    ) -> list[str]:

        normalized_query = (
            self._normalize(query)
        )

        words = re.findall(
            r"[a-z0-9][a-z0-9_-]*",
            normalized_query,
        )

        generic_search_terms = {
            # French
            "lien",
            "liens",
            "recherche",
            "rechercher",
            "resume",
            "trouve",
            "trouver",

            # English
            "find",
            "link",
            "links",
            "search",
            "summary",

            # Spanish
            "buscar",
            "busca",
            "enlace",
            "enlaces",
            "resumen",

            # Filipino / Tagalog
            "hanap",
            "hanapin",
            "link",
            "links",
            "buod",
            "tungkol",
            "magbigay",
            "bigyan",
        }

        candidates = [
            word
            for word in words
            if len(word) > 3
            and word not in generic_search_terms
        ]

        if not candidates:
            return []

        candidates = sorted(
            candidates,
            key=len,
            reverse=True,
        )

        return candidates[:5]

    # --------------------------------------------------
    # Anchor Validation
    # --------------------------------------------------

    def _is_usable_anchor(
        self,
        anchor: str,
    ) -> bool:

        cleaned = anchor.strip()

        if not cleaned:
            return False

        if len(cleaned) <= 2:
            return False

        if cleaned.lower().startswith(
            "claim:"
        ):
            return False

        return True

    # --------------------------------------------------
    # Text Normalization
    # --------------------------------------------------

    def _normalize(
        self,
        text: str,
    ) -> str:

        lowered = str(
            text
        ).lower().strip()

        decomposed = (
            unicodedata.normalize(
                "NFKD",
                lowered,
            )
        )

        without_accents = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(
                character
            )
        )

        return " ".join(
            without_accents.split()
        )

    # --------------------------------------------------
    # Anchor Deduplication
    # --------------------------------------------------

    def _deduplicate(
        self,
        items: list[str],
    ) -> list[str]:

        unique = []
        seen = set()

        for item in items:
            normalized = (
                self._normalize(item)
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            unique.append(item)

        return unique
