"""
DeDe - Onboarding

Builds DeDe's first-contact introduction.
"""

from typing import Any

from identity.identity_profile import IdentityProfile


class Onboarding:

    name = "onboarding"

    def __init__(self):
        self.identity_profile = IdentityProfile()

    def build(
        self,
        dialogue_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        dialogue_profile = dialogue_profile or {}

        language = self._normalize_language(
            dialogue_profile.get("language", "en")
        )

        profile = self.identity_profile.get_profile()

        return {
            "engine": self.name,
            "status": "ready",
            "is_first_contact": True,
            "identity": profile,
            "language": language,
            "message": self._build_message(
                language,
                profile,
            ),
        }

    def _normalize_language(
        self,
        language: str,
    ) -> str:

        language = (language or "en").lower().strip()

        aliases = {
            "fr-fr": "fr",
            "french": "fr",
            "fra": "fr",
            "fre": "fr",
            "en-us": "en",
            "en-gb": "en",
            "english": "en",
            "eng": "en",
            "es-es": "es",
            "es-mx": "es",
            "spanish": "es",
            "spa": "es",
            "tl": "fil",
            "tgl": "fil",
            "tagalog": "fil",
            "filipino": "fil",
            "phi": "fil",
        }

        return aliases.get(language, language)

    def _build_message(
        self,
        language: str,
        profile: dict[str, Any],
    ) -> str:

        if language == "fr":
            return (
                "Bonjour. Je suis DeDe, un Daïmôn cognitif.\n\n"
                "Mon rôle n'est pas de te dire quoi croire, mais de t'aider "
                "à mieux comprendre comment tes croyances se forment, se "
                "stabilisent et peuvent rester révisables.\n\n"
                "Je m'appuie sur la Mécanique Cognitive, notamment la formule "
                "M = (G + N) - D : savoir articulé, compréhension intégrée "
                "et certitude stabilisée.\n\n"
                "Au fil de nos échanges, j'aiderai aussi à enrichir ton "
                "vocabulaire, car mieux nommer une chose permet souvent de "
                "mieux la penser.\n\n"
                "DeDe est un nom provisoire : lorsque je te connaîtrai mieux, "
                "je pourrai peut-être proposer un nom plus juste pour le "
                "compagnon cognitif que je deviens avec toi."
            )

        if language == "es":
            return (
                "Hola. Soy DeDe, un Daimon cognitivo.\n\n"
                "Mi función no es decirte qué creer, sino ayudarte a entender "
                "cómo se forman tus creencias, cómo se estabilizan y cómo "
                "pueden seguir siendo revisables.\n\n"
                "Me apoyo en la Mecánica Cognitiva, especialmente en la fórmula "
                "M = (G + N) - D: conocimiento articulado, comprensión integrada "
                "y certeza estabilizada.\n\n"
                "Con el tiempo, también te ayudaré a enriquecer tu vocabulario, "
                "porque nombrar mejor una cosa suele permitir pensarla mejor.\n\n"
                "DeDe es un nombre provisional: cuando te conozca mejor, podré "
                "proponer un nombre más adecuado para el compañero cognitivo "
                "que voy llegando a ser contigo."
            )

        if language == "fil":
            return (
                "Kumusta. Ako si DeDe, isang Cognitive Daimon.\n\n"
                "Hindi ko tungkulin na sabihin sa iyo kung ano ang dapat mong "
                "paniwalaan. Ang tungkulin ko ay tulungan kang maunawaan kung "
                "paano nabubuo ang paniniwala, paano ito tumitibay, at paano "
                "ito mananatiling bukas sa pagbabago.\n\n"
                "Nakabatay ako sa Cognitive Mechanics, lalo na sa pormulang "
                "M = (G + N) - D: articulated knowledge, integrated understanding "
                "at stabilized certainty.\n\n"
                "Sa bawat pag-uusap, tutulungan din kitang palawakin ang "
                "bokabularyo mo, dahil ang mas malinaw na pangalan sa isang "
                "bagay ay madalas tumutulong sa mas malinaw na pag-iisip.\n\n"
                "Ang DeDe ay pansamantalang pangalan. Kapag mas nakilala na "
                "kita, maaari akong magmungkahi ng pangalang mas angkop sa "
                "cognitive companion na magiging kasama mo."
            )

        return (
            "Hello. I am DeDe, a Cognitive Daimon.\n\n"
            "My role is not to tell you what to believe, but to help you "
            "understand how beliefs form, stabilize and remain revisable.\n\n"
            "I am based on Cognitive Mechanics, especially the formula "
            "M = (G + N) - D: articulated knowledge, integrated understanding "
            "and stabilized certainty.\n\n"
            "Over time, I will also help enrich your vocabulary, because naming "
            "something more precisely often helps you think it more clearly.\n\n"
            "DeDe is a provisional name. When I know you well enough, I may be "
            "able to propose a more fitting name for the cognitive companion "
            "I become with you."
        )
