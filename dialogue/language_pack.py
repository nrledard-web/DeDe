"""
DeDe - Language Pack

Centralized user-facing dialogue phrases.
"""

from typing import Any


class LanguagePack:

    name = "language_pack"

    PHRASES = {
        "fr": {
            "continue_with_reference": (
                "En continuité avec {reference_topic}, "
                "on peut appliquer la même mécanique à {current_topic}."
            ),
            "continue_with_topic": (
                "Oui, on peut prolonger la réflexion vers {current_topic}."
            ),
            "continue_generic": (
                "Oui, on peut poursuivre dans le même fil de réflexion."
            ),
            "follow_up_with_topic": (
                "Souhaites-tu maintenant comparer {current_topic} "
                "avec un autre domaine, ou approfondir ce cas précis ?"
            ),
            "follow_up_generic": (
                "Souhaites-tu continuer avec un autre domaine "
                "ou approfondir ce fil ?"
            ),
            "missing_dimension": (
                "Souhaites-tu préciser cette dimension : {dimension}"
            ),
            "clarification": (
                "Souhaites-tu une réponse courte, technique, "
                "philosophique ou orientée application ?"
            ),
        },
        "en": {
            "continue_with_reference": (
                "Continuing from {reference_topic}, "
                "we can apply the same mechanism to {current_topic}."
            ),
            "continue_with_topic": (
                "Yes, we can extend the reflection toward {current_topic}."
            ),
            "continue_generic": (
                "Yes, we can continue in the same line of thought."
            ),
            "follow_up_with_topic": (
                "Would you like to compare {current_topic} "
                "with another domain, or go deeper into this case?"
            ),
            "follow_up_generic": (
                "Would you like to continue with another domain, "
                "or go deeper into this thread?"
            ),
            "missing_dimension": (
                "Would you like to clarify this dimension: {dimension}?"
            ),
            "clarification": (
                "Would you like a short, technical, philosophical, "
                "or application-oriented answer?"
            ),
        },
        "es": {
            "continue_with_reference": (
                "En continuidad con {reference_topic}, "
                "podemos aplicar la misma mecánica a {current_topic}."
            ),
            "continue_with_topic": (
                "Sí, podemos prolongar la reflexión hacia {current_topic}."
            ),
            "continue_generic": (
                "Sí, podemos continuar en la misma línea de reflexión."
            ),
            "follow_up_with_topic": (
                "¿Quieres comparar ahora {current_topic} "
                "con otro dominio, o profundizar este caso?"
            ),
            "follow_up_generic": (
                "¿Quieres continuar con otro dominio "
                "o profundizar esta línea?"
            ),
            "missing_dimension": (
                "¿Quieres precisar esta dimensión: {dimension}?"
            ),
            "clarification": (
                "¿Quieres una respuesta breve, técnica, filosófica "
                "u orientada a la aplicación?"
            ),
        },
        "fil": {
            "continue_with_reference": (
                "Sa pagpapatuloy ng usapan tungkol sa {reference_topic}, "
                "maaari nating ilapat ang parehong mekanismo sa {current_topic}."
            ),
            "continue_with_topic": (
                "Oo, maaari nating palawakin ang pagtalakay tungkol sa {current_topic}."
            ),
            "continue_generic": (
                "Oo, maaari nating ipagpatuloy ang parehong linya ng pag-iisip."
            ),
            "follow_up_with_topic": (
                "Gusto mo bang ihambing ang {current_topic} "
                "sa ibang larangan, o palalimin pa natin ito?"
            ),
            "follow_up_generic": (
                "Gusto mo bang magpatuloy sa ibang larangan "
                "o palalimin pa natin ang usaping ito?"
            ),
            "missing_dimension": (
                "Gusto mo bang linawin ang aspektong ito: {dimension}?"
            ),
            "clarification": (
                "Gusto mo ba ng maikli, teknikal, pilosopikal, "
                "o praktikal na paliwanag?"
            ),
        },
    }

    def get(
        self,
        language: str,
        key: str,
        **kwargs: Any,
    ) -> str:

        language = language or "en"

        phrases = self.PHRASES.get(
            language,
            self.PHRASES["en"],
        )

        template = phrases.get(
            key,
            self.PHRASES["en"].get(
                key,
                "",
            ),
        )

        return template.format(**kwargs)
