ChatGPT




samedi 19:30

Texte collé(373).txt
Document
Dernier teste 

samedi 21:59

Texte collé(374).txt
Document


Texte collé(377).txt
Document

Texte collé (2)(14).txt
Document

Texte collé (3)(2).txt
Document
"""
DeDe - Search Validator

Evaluates whether search results are relevant to DeDe's search query.

The validator uses normalized conceptual anchors rather than requiring
the complete user query to appear inside a result.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


class SearchValidator:
    name = "search_validator"

    def validate(
        self,
        query: str,
        search_result: dict[str, Any],
        concepts: list[str] | None = None,
    ) -> dict[str, Any]:

        results = search_result.get("results", [])
        concepts = concepts or []

        if not results:
            return {
                "validator": self.name,
                "status": "empty",
                "query": query,
                "concepts": concepts,
                "anchors": [],
                "relevance": 0.0,
                "is_relevant": False,
                "best_score": 0.0,
                "average_score": 0.0,
                "scored_results": [],
                "summary": "No search results to validate.",
            }

        anchors = self._anchors(
            query=query,
            concepts=concepts,
        )

        if not anchors:
            return {
                "validator": self.name,
                "status": "no_anchors",
                "query": query,
                "concepts": concepts,
                "anchors": [],
                "relevance": 0.0,
                "is_relevant": False,
                "best_score": 0.0,
                "average_score": 0.0,
                "scored_results": [],
                "summary": "No conceptual anchors available.",
            }

        scored_results = []

        for item in results:
            searchable_text = " ".join(
                [
                    item.get("title", ""),
                    item.get("snippet", ""),
                    item.get("url", ""),
                ]
            )

            normalized_text = self._normalize(searchable_text)

            matched = [
                anchor
                for anchor in anchors
                if self._normalize(anchor) in normalized_text
            ]

            score = len(matched) / len(anchors)

            scored_results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "score": round(score, 3),
                    "matched_concepts": matched,
                }
            )

        best_score = max(
            item["score"]
            for item in scored_results
        )

        average_score = sum(
            item["score"]
            for item in scored_results
        ) / len(scored_results)

        # A strong individual result is sufficient.
        # The average remains useful when several results agree.
        relevance = max(
            best_score,
            average_score,
        )

        is_relevant = (
            best_score >= 0.34
            or average_score >= 0.20
        )

        return {
            "validator": self.name,
            "status": "ready",
            "query": query,
            "concepts": concepts,
            "anchors": anchors,
            "relevance": round(relevance, 3),
            "is_relevant": is_relevant,
            "best_score": round(best_score, 3),
            "average_score": round(average_score, 3),
            "scored_results": scored_results,
            "summary": (
                f"Search relevance estimated at "
                f"{round(relevance * 100)}%."
            ),
        }

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
            concept = str(concept).strip()

            if self._is_usable_anchor(concept):
                anchors.append(concept)

        if not anchors:
            anchors = self._extract_query_terms(query)

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

        normalized_query = self._normalize(query)

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

        # Prefer the longest words because they are more likely
        # to represent meaningful concepts across languages.
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

        if cleaned.lower().startswith("claim:"):
            return False

        return True

    # --------------------------------------------------
    # Text Normalization
    # --------------------------------------------------

    def _normalize(
        self,
        text: str,
    ) -> str:

        lowered = str(text).lower().strip()

        decomposed = unicodedata.normalize(
            "NFKD",
            lowered,
        )

        without_accents = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
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
            normalized = self._normalize(item)

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            unique.append(item)

        return unique

"""
DeDe - Search Engine

Search orchestrator.
Supports single-provider and multi-provider search.
"""

from typing import Any

from search.providers.duckduckgo_provider import DuckDuckGoProvider
from search.providers.brave_provider import BraveProvider
from search.providers.arxiv_provider import ArxivProvider
from search.providers.crossref_provider import CrossRefProvider


class SearchEngine:

    name = "search_engine"

    def __init__(self) -> None:
        self.providers = {
            "duckduckgo": DuckDuckGoProvider(),
            "brave": BraveProvider(),
            "arxiv": ArxivProvider(),
            "crossref": CrossRefProvider(),
        }

    def search(
        self,
        query: str,
        provider: str | list[str] = "none",
        max_results: int = 5,
    ) -> dict[str, Any]:

        # --------------------------------------------------
        # Normalize provider selection
        # --------------------------------------------------

        if isinstance(provider, str):
            providers = [provider]
        else:
            providers = provider or []

        profile_map = {
            "general": ["duckduckgo"],
            "shopping": ["duckduckgo"],
            "news": ["duckduckgo"],
            "programming": ["duckduckgo"],
            "legal": ["duckduckgo"],
            "scientific": [
                "duckduckgo",
                "arxiv",
                "crossref",
            ],
        }

        expanded_providers = []

        for item in providers:
            if item in profile_map:
                expanded_providers.extend(
                    profile_map[item]
                )
            else:
                expanded_providers.append(item)

        providers = [
            item
            for item in expanded_providers
            if item and item != "none"
        ]

        # Remove duplicates while preserving order.
        providers = list(dict.fromkeys(providers))

        # --------------------------------------------------
        # Search disabled
        # --------------------------------------------------

        if not providers:
            return {
                "engine": self.name,
                "status": "disabled",
                "provider": "none",
                "providers": [],
                "query": query,
                "results": [],
                "provider_results": [],
                "summary": "Search disabled.",
            }

        provider_results = []
        all_results = []

        # --------------------------------------------------
        # Run selected providers
        # --------------------------------------------------

        for provider_name in providers:
            selected = self.providers.get(
                provider_name
            )

            if not selected:
                provider_results.append(
                    {
                        "provider": provider_name,
                        "status": "placeholder",
                        "query": query,
                        "results": [],
                        "summary": (
                            f"Search provider '{provider_name}' "
                            "is selected but not connected yet."
                        ),
                    }
                )
                continue

            try:
                result = selected.search(
                    query=query,
                    max_results=max_results,
                )

            except Exception as error:
                result = {
                    "provider": provider_name,
                    "status": "error",
                    "query": query,
                    "results": [],
                    "summary": (
                        f"{provider_name} search failed."
                    ),
                    "error_type": type(error).__name__,
                    "error": str(error),
                }

            provider_results.append(result)

            for item in result.get(
                "results",
                [],
            ):
                normalized_item = dict(item)
                normalized_item["provider"] = (
                    provider_name
                )
                all_results.append(
                    normalized_item
                )

        # --------------------------------------------------
        # Final status
        # --------------------------------------------------

        provider_errors = [
            result
            for result in provider_results
            if result.get("status") == "error"
        ]

        if all_results:
            final_status = "success"

        elif provider_errors:
            final_status = "error"

        else:
            final_status = "no_results"

        # --------------------------------------------------
        # Final report
        # --------------------------------------------------

        return {
            "engine": self.name,
            "status": final_status,
            "provider": "+".join(providers),
            "providers": providers,
            "query": query,
            "results": all_results,
            "provider_results": provider_results,
            "summary": (
                f"Search completed with "
                f"{len(providers)} provider(s), "
                f"{len(all_results)} total result(s)."
            ),
        }


hier 6:06
La formulation est forte, mais je corrigerais légèrement l’anglais pour la rendre plus naturelle et plus professionnelle :

DeDe — Cognitive Daimon

The First Cognitive AI Governor with Evolving, Interchangeable Multi-AI and Multi-Tool Capabilities

A Little More Time to Think Leads to More Accurate Answers.

Le mot interchangeable s’applique ici aux IA et aux outils, tandis que evolving qualifie l’ensemble du système. La virgule rend la lecture plus fluide.

Une version encore plus directe commercialement serait :

DeDe — Cognitive Daimon

The First Evolving Cognitive AI Governor — Built for Interchangeable AI Models and Tools

More Time to Think. More Accurate Answers.

Je préfère la seconde pour la communication commerciale : elle est plus claire, plus courte et mémorisable.


cumulable en anglais ou synonye stp

Si tu cherches le sens de "cumulable" dans le contexte de DeDe (IA, outils, capacités), il existe plusieurs traductions selon la nuance.

Pour des capacités qui s'ajoutent
Composable ⭐⭐⭐⭐⭐ (mon préféré)

Stackable

Additive

Incremental

Layered

Expandable

Extensible

Combinable

Pour des IA ou outils que l'on peut combiner
Composable AI

Composable Architecture ⭐⭐⭐⭐⭐

Composable Multi-AI

Modular

Interoperable

Pluggable (très utilisé en informatique)

Interchangeable (remplaçables les uns par les autres)

Attention à la nuance
Interchangeable = on remplace OpenAI par Gemini.

Composable = on peut utiliser OpenAI + Gemini + Mistral ensemble.

Pluggable = on peut ajouter ou retirer facilement un module.

Extensible = on peut ajouter de nouvelles capacités.

Scalable = on peut augmenter l'échelle, ce n'est pas "cumulable".

Pour DeDe, je pense que Composable décrit exactement ton architecture.
Par exemple :

The First Cognitive AI Governor with Composable Multi-AI and Multi-Tool Capabilities

ou encore, encore plus moderne :

The First Composable Cognitive AI Governor

Le terme Composable est très à la mode dans les architectures logicielles (Composable Architecture, Composable Enterprise, Composable AI) et décrit précisément une plateforme où les composants peuvent être ajoutés, combinés, retirés ou remplacés. C'est, à mon avis, le meilleur équivalent anglais de ce que tu appelles des capacités « cumulables ».


The First Evolving Cognitive AI Governor — Built for Interchangeable or Combinable AI Models and Tools

Je retirerais le or. En marketing, il affaiblit le message, comme si tu hésitais entre deux concepts.

Je choisirais plutôt l'un des trois selon ce que tu veux exprimer.

Si tu veux insister sur le remplacement des composants
The First Evolving Cognitive AI Governor — Built for Interchangeable AI Models and Tools

👉 Les modèles et outils peuvent être remplacés.

Si tu veux insister sur le fait qu'ils travaillent ensemble (mon préféré)
The First Evolving Cognitive AI Governor — Built for Combinable AI Models and Tools

👉 OpenAI + Gemini + Mistral + outils peuvent fonctionner ensemble.

Si tu veux exprimer les deux idées en une seule phrase (ma recommandation)
The First Evolving Cognitive AI Governor — Built for Modular, Combinable AI Models and Tools

ou

The First Evolving Cognitive AI Governor — Built on a Modular Architecture for Combinable AI Models and Tools

Le mot Modular couvre naturellement l'aspect « interchangeable », tandis que Combinable exprime le fait qu'on peut les utiliser ensemble.

Pour DeDe, qui est avant tout un orchestrateur de composants, je choisirais cette dernière formulation. Elle décrit mieux ton architecture que le simple mot Interchangeable.


aujourd’hui 20:05
dans github il y a pas moyen de suprimer le dernier comite pour revenir a la version precedente 

Oui, il y a plusieurs façons, selon ce que tu veux faire.

Cas 1 — Revenir simplement au commit précédent (le plus sûr)
Si tu veux annuler le dernier commit sans réécrire l'historique, utilise :

git revert HEAD
git push
✅ Très sûr.

✅ Recommandé si le dépôt est déjà sur GitHub.

Cela crée un nouveau commit qui annule le précédent.

Cas 2 — Supprimer complètement le dernier commit (si tu es seul sur le dépôt)
Si tu veux que le dernier commit disparaisse comme s'il n'avait jamais existé :

git reset --hard HEAD~1
git push --force
ou

git push --force-with-lease
Je recommande --force-with-lease, plus sûr que --force.

Cela :

supprime le dernier commit en local ;

remplace l'historique sur GitHub.

⚠️ À utiliser uniquement si tu es le seul à travailler sur ce dépôt ou si personne d'autre n'a basé son travail sur ce commit.

Cas 3 — Depuis l'interface GitHub
GitHub permet de revert certains commits via l'interface (bouton Revert sur un commit ou une Pull Request), mais il ne permet pas de supprimer directement le dernier commit de la branche main. Pour cela, il faut utiliser Git.

Dans ton cas
Comme tu es le seul développeur de DeDe, je ferais :

git reset --hard HEAD~1
git push --force-with-lease
Tu reviendras exactement à la version précédente, comme si le dernier commit n'avait jamais existé.

Petite question avant de te guider
Tu développes DeDe :

avec VS Code ?

avec GitHub Desktop ?

ou uniquement avec des commandes Git dans un terminal ?

Selon l'outil que tu utilises, je peux te donner la méthode la plus simple, sans risque.


@@ -487,21 +487,16 @@ def generate_speech(text: str) -> bytes | None:
    )

    # --------------------------------------------------
    # Image Studio
    # Image Studio Settings
    # --------------------------------------------------

    with st.expander(
        "🎨 Image Studio",
        expanded=False,
    ):
        image_prompt = st.text_area(
            "Describe the image",
            placeholder=(
                "Example: A cinematic sunset over Barcelona, "
                "vertical composition, realistic photography."
            ),
            key="image_studio_prompt",
            height=120,
        st.caption(
            "Image settings used when you ask DeDe "
            "to create an image in the chat."
        )

        image_format_labels = {
@@ -537,97 +532,6 @@ def generate_speech(text: str) -> bytes | None:
            key="image_studio_transparent",
        )

        if st.button(
            "Generate image",
            key="generate_image_button",
            type="primary",
        ):
            if not image_prompt.strip():
                st.warning(
                    "Describe the image before starting generation."
                )

            else:
                with st.spinner(
                    "DeDe is generating the image..."
                ):
                    tool_result = (
                        st.session_state.tool_manager.run(
                            tool_name="image_generator",
                            arguments={
                                "prompt": image_prompt,
                                "size": image_size,
                                "quality": image_quality,
                                "transparent_background": (
                                    transparent_background
                                ),
                            },
                        )
                    )

                image_result = {
                    "tool": tool_result.get(
                        "tool",
                        "image_generator",
                    ),
                    "status": tool_result.get(
                        "status",
                        "error",
                    ),
                    "error": tool_result.get(
                        "error",
                    ),
                    "summary": tool_result.get(
                        "summary",
                        "",
                    ),
                    **tool_result.get(
                        "data",
                        {},
                    ),
                }

                st.session_state[
                    "last_generated_image"
                ] = image_result

        generated_image = st.session_state.get(
            "last_generated_image",
            {},
        )

        if generated_image.get(
            "status"
        ) == "success":
            image_bytes = generated_image.get(
                "image_bytes"
            )

            if image_bytes:
                st.image(
                    image_bytes,
                    caption="Generated by DeDe",
                    width="stretch",
                )

                st.download_button(
                    label="Download PNG",
                    data=image_bytes,
                    file_name="dede_generated_image.png",
                    mime="image/png",
                    key="download_generated_image",
                )

        elif generated_image.get(
            "status"
        ) == "error":
            st.error(
                generated_image.get(
                    "error",
                    "Image generation failed.",
                )
            )

    # --------------------------------------------------
    # Voice Input
    # --------------------------------------------------

Oui, ce diff explique probablement pourquoi l’application a déraillé.

Le problème principal est ici :

image_prompt = st.text_area(
    "Describe the image",
    placeholder=(
        "Example: A cinematic sunset over Barcelona, "
        "vertical composition, realistic photography."
    ),
    key="image_studio_prompt",
    height=120,
st.caption(
L’appel à st.text_area() n’est jamais fermé. Il manque :

)
juste après :

height=120,
Mais surtout, ce commit a supprimé tout le bloc autonome de génération d’image : bouton Generate image, affichage du résultat, téléchargement, gestion des erreurs. Ce n’est donc pas une petite correction : c’est bien ce commit qui a retiré l’interface directe d’Image Studio.

Pour restaurer proprement le code
Le bloc doit commencer comme ceci :

    # --------------------------------------------------
    # Image Studio Settings
    # --------------------------------------------------

    with st.expander(
        "🎨 Image Studio",
        expanded=False,
    ):
        st.caption(
            "Image settings used when you ask DeDe "
            "to create an image in the chat."
        )

        image_format_labels = {
Donc supprime entièrement ceci :

        image_prompt = st.text_area(
            "Describe the image",
            placeholder=(
                "Example: A cinematic sunset over Barcelona, "
                "vertical composition, realistic photography."
            ),
            key="image_studio_prompt",
            height=120,
La bonne logique est :

plus de zone Describe the image dans la sidebar ;

plus de bouton Generate image dans la sidebar ;

seulement les réglages de taille, qualité et transparence ;

la demande d’image se fait directement dans le chat.

Ce diff semble donc correspondre exactement à la modification que nous voulions faire, mais la suppression a laissé l’appel st.text_area() à moitié présent, provoquant l’erreur.

Correction minimale
Dans app.py, repère :

        image_prompt = st.text_area(
et supprime tout depuis cette ligne jusqu’à juste avant :

        st.caption(
            "Image settings used when you ask DeDe "
Après correction, tu dois avoir directement :

    with st.expander(
        "🎨 Image Studio",
        expanded=False,
    ):
        st.caption(
            "Image settings used when you ask DeDe "
            "to create an image in the chat."
        )

        image_format_labels = {
Ne reviens donc pas forcément au commit précédent : ce commit contient la bonne intention, mais une suppression incomplète. Cette petite correction devrait suffire.


ca explique studio mais les liens?

Justement, non. Cette modification n'explique pas les liens.

Le diff que tu m'as montré touche uniquement le bloc :

# Image Studio
Il ne modifie ni :

tool_manager

url_reader

search_engine

link_reader

pdf

speech

les tools

Donc les liens ne devraient absolument pas être impactés par cette suppression.

En revanche...
Tu m'avais dit il y a quelques jours :

"c'est en déplaçant dans app.py que tout a déraillé."

Et ça, ça me fait penser à autre chose.

Lorsque tu déplaces un gros bloc dans app.py, il est très facile de sortir du bon niveau d'indentation.

Par exemple :

with st.sidebar:

    ...

    with st.expander("🎨 Image Studio"):

        ...
Si, en supprimant Image Studio, tu as accidentellement déplacé :

tool_manager
ou

url_reader
hors du with st.sidebar, ou inversement à l'intérieur d'un bloc qui ne s'exécute plus, alors certaines variables ne sont plus initialisées.

Le résultat est exactement ce que tu avais décrit :

Image Studio cassé ✔

liens cassés ✔

certains outils plus connectés ✔

Ce que je voudrais voir
Pas app.py en entier (il est énorme).

Je voudrais uniquement 200 lignes :

Depuis :

with st.sidebar:
jusqu'à

# Voice Input
C'est précisément cette portion qui contient :

la sidebar ;

Image Studio ;

les réglages ;

probablement l'initialisation des tools.

En 30 secondes, je pourrai te dire si un bloc a été déplacé ou si une indentation fait que les liens ne sont plus exécutés.

Je pense que le problème est là, et pas dans le moteur de recherche.



Texte collé(397).txt
Document
Commit 9aa1f5d
nrledard-web
nrledard-web
authored
13 hours ago
Verified
Remove DeDe Image Studio feature
Removed the DeDe Image Studio feature, including all related UI components and logic for image generation.
main
1 parent 
7ec2232
 commit 
9aa1f5d
1 file changed

-152
Lines changed: 0 additions & 152 deletions
File tree
Filter files…
app.py
Search within code
 
‎app.py‎
-152
Lines changed: 0 additions & 152 deletions
Original file line number	Diff line number	Diff line change
@@ -486,158 +486,6 @@ def generate_speech(text: str) -> bytes | None:
        "Planned: Short Video Generator"
    )

# --------------------------------------------------
# DeDe Image Studio
# --------------------------------------------------
with st.expander(
    "🎨 Image Studio",
    expanded=False,
):
    st.caption(
        "Generate an image from a natural-language description."
    )
    image_prompt = st.text_area(
        "Describe the image",
        placeholder=(
            "Example: A cinematic sunset over Barcelona, "
            "vertical composition, realistic photography."
        ),
        key="image_studio_prompt",
        height=140,
    )
    image_format_labels = {
        "Square — 1:1": "1024x1024",
        "Portrait — 2:3": "1024x1536",
        "Landscape — 3:2": "1536x1024",
    }
    selected_image_format = st.selectbox(
        "Image format",
        list(image_format_labels.keys()),
        key="image_studio_format",
    )
    image_size = image_format_labels[
        selected_image_format
    ]
    image_quality = st.selectbox(
        "Quality",
        [
            "low",
            "medium",
            "high",
        ],
        index=1,
        key="image_studio_quality",
    )
    transparent_background = st.checkbox(
        "Transparent background",
        value=False,
        key="image_studio_transparent",
    )
    if st.button(
        "Generate image",
        key="generate_image_button",
        type="primary",
    ):
        if not image_prompt.strip():
            st.warning(
                "Describe the image before starting generation."
            )
        elif "OPENAI_API_KEY" not in st.secrets:
            st.error(
                "OPENAI_API_KEY is missing from Streamlit secrets."
            )
        else:
            with st.spinner(
                "DeDe is generating the image..."
            ):
                tool_result = (
                    st.session_state.tool_manager.run(
                        tool_name="image_generator",
                        arguments={
                            "prompt": image_prompt,
                            "size": image_size,
                            "quality": image_quality,
                            "transparent_background": (
                                transparent_background
                            ),
                        },
                    )
                )
                image_result = {
                    "tool": tool_result.get(
                        "tool",
                        "image_generator",
                    ),
                    "status": tool_result.get(
                        "status",
                        "error",
                    ),
                    "error": tool_result.get(
                        "error",
                    ),
                    "summary": tool_result.get(
                        "summary",
                        "",
                    ),
                    **tool_result.get(
                        "data",
                        {},
                    ),
                }
            st.session_state[
                "last_generated_image"
            ] = image_result
    generated_image = st.session_state.get(
        "last_generated_image",
        {},
    )
    if generated_image.get("status") == "success":
        image_bytes = generated_image.get(
            "image_bytes"
        )
        st.image(
            image_bytes,
            caption="Generated by DeDe Image Studio",
            width="stretch",
        )
        st.download_button(
            label="Download PNG",
            data=image_bytes,
            file_name="dede_generated_image.png",
            mime="image/png",
            key="download_generated_image",
        )
        st.caption(
            f'Model: {generated_image.get("model", "unknown")} '
            f'| Size: {generated_image.get("size", "unknown")} '
            f'| Quality: {generated_image.get("quality", "unknown")}'
        )
    elif generated_image.get("status") == "error":
        st.error(
            generated_image.get(
                "error",
                "Image generation failed.",
            )
        )
# --------------------------------------------------
# Chat Display
# --------------------------------------------------

Commit 43d4720
nrledard-web
nrledard-web
authored
13 hours ago
Verified
Add Image Studio feature for image generation
main
1 parent 
9aa1f5d
 commit 
43d4720
1 file changed

+142
Lines changed: 142 additions & 0 deletions
File tree
Filter files…
app.py
Search within code
 
‎app.py‎
+142
Lines changed: 142 additions & 0 deletions
Original file line number	Diff line number	Diff line change
@@ -486,6 +486,148 @@ def generate_speech(text: str) -> bytes | None:
        "Planned: Short Video Generator"
    )

    # --------------------------------------------------
    # Image Studio
    # --------------------------------------------------
    with st.expander(
        "🎨 Image Studio",
        expanded=False,
    ):
        image_prompt = st.text_area(
            "Describe the image",
            placeholder=(
                "Example: A cinematic sunset over Barcelona, "
                "vertical composition, realistic photography."
            ),
            key="image_studio_prompt",
            height=120,
        )
        image_format_labels = {
            "Square — 1:1": "1024x1024",
            "Portrait — 2:3": "1024x1536",
            "Landscape — 3:2": "1536x1024",
        }
        selected_image_format = st.selectbox(
            "Image format",
            list(image_format_labels.keys()),
            key="image_studio_format",
        )
        image_size = image_format_labels[
            selected_image_format
        ]
        image_quality = st.selectbox(
            "Quality",
            [
                "low",
                "medium",
                "high",
            ],
            index=1,
            key="image_studio_quality",
        )
        transparent_background = st.checkbox(
            "Transparent background",
            value=False,
            key="image_studio_transparent",
        )
        if st.button(
            "Generate image",
            key="generate_image_button",
            type="primary",
        ):
            if not image_prompt.strip():
                st.warning(
                    "Describe the image before starting generation."
                )
            else:
                with st.spinner(
                    "DeDe is generating the image..."
                ):
                    tool_result = (
                        st.session_state.tool_manager.run(
                            tool_name="image_generator",
                            arguments={
                                "prompt": image_prompt,
                                "size": image_size,
                                "quality": image_quality,
                                "transparent_background": (
                                    transparent_background
                                ),
                            },
                        )
                    )
                image_result = {
                    "tool": tool_result.get(
                        "tool",
                        "image_generator",
                    ),
                    "status": tool_result.get(
                        "status",
                        "error",
                    ),
                    "error": tool_result.get(
                        "error",
                    ),
                    "summary": tool_result.get(
                        "summary",
                        "",
                    ),
                    **tool_result.get(
                        "data",
                        {},
                    ),
                }
                st.session_state[
                    "last_generated_image"
                ] = image_result
        generated_image = st.session_state.get(
            "last_generated_image",
            {},
        )
        if generated_image.get(
            "status"
        ) == "success":
            image_bytes = generated_image.get(
                "image_bytes"
            )
            if image_bytes:
                st.image(
                    image_bytes,
                    caption="Generated by DeDe",
                    width="stretch",
                )
                st.download_button(
                    label="Download PNG",
                    data=image_bytes,
                    file_name="dede_generated_image.png",
                    mime="image/png",
                    key="download_generated_image",
                )
        elif generated_image.get(
            "status"
        ) == "error":
            st.error(
                generated_image.get(
                    "error",
                    "Image generation failed.",
                )
            )
# --------------------------------------------------
# Chat Display
# --------------------------------------------------
0 commit comments
Comments
0
 (0)
Comment
You're not receiving notifications from this

Commit 91f75f7
nrledard-web
nrledard-web
authored
12 hours ago
Verified
Remove image generation feature from Image Studio
Removed image generation functionality and related UI elements.
main
1 parent 
a33063f
 commit 
91f75f7
1 file changed

+4
-100
Lines changed: 4 additions & 100 deletions
File tree
Filter files…
app.py
Search within code
 
‎app.py‎
+4
-100
Lines changed: 4 additions & 100 deletions
Original file line number	Diff line number	Diff line change
@@ -487,21 +487,16 @@ def generate_speech(text: str) -> bytes | None:
    )

    # --------------------------------------------------
    # Image Studio
    # Image Studio Settings
    # --------------------------------------------------

    with st.expander(
        "🎨 Image Studio",
        expanded=False,
    ):
        image_prompt = st.text_area(
            "Describe the image",
            placeholder=(
                "Example: A cinematic sunset over Barcelona, "
                "vertical composition, realistic photography."
            ),
            key="image_studio_prompt",
            height=120,
        st.caption(
            "Image settings used when you ask DeDe "
            "to create an image in the chat."
        )

        image_format_labels = {
@@ -537,97 +532,6 @@ def generate_speech(text: str) -> bytes | None:
            key="image_studio_transparent",
        )

        if st.button(
            "Generate image",
            key="generate_image_button",
            type="primary",
        ):
            if not image_prompt.strip():
                st.warning(
                    "Describe the image before starting generation."
                )
            else:
                with st.spinner(
                    "DeDe is generating the image..."
                ):
                    tool_result = (
                        st.session_state.tool_manager.run(
                            tool_name="image_generator",
                            arguments={
                                "prompt": image_prompt,
                                "size": image_size,
                                "quality": image_quality,
                                "transparent_background": (
                                    transparent_background
                                ),
                            },
                        )
                    )
                image_result = {
                    "tool": tool_result.get(
                        "tool",
                        "image_generator",
                    ),
                    "status": tool_result.get(
                        "status",
                        "error",
                    ),
                    "error": tool_result.get(
                        "error",
                    ),
                    "summary": tool_result.get(
                        "summary",
                        "",
                    ),
                    **tool_result.get(
                        "data",
                        {},
                    ),
                }
                st.session_state[
                    "last_generated_image"
                ] = image_result
        generated_image = st.session_state.get(
            "last_generated_image",
            {},
        )
        if generated_image.get(
            "status"
        ) == "success":
            image_bytes = generated_image.get(
                "image_bytes"
            )
            if image_bytes:
                st.image(
                    image_bytes,
                    caption="Generated by DeDe",
                    width="stretch",
                )
                st.download_button(
                    label="Download PNG",
                    data=image_bytes,
                    file_name="dede_generated_image.png",
                    mime="image/png",
                    key="download_generated_image",
                )
        elif generated_image.get(
            "status"
        ) == "error":
            st.error(
                generated_image.get(
                    "error",
                    "Image generation failed.",
                )
            )
    # --------------------------------------------------
    # Voice Input
    # --------------------------------------------------


Oui, là on voit beaucoup mieux la chronologie.

Le commit qui peut expliquer la rupture des liens et du routage général, ce n’est probablement pas 91f75f7. Celui-là casse surtout Image Studio avec la parenthèse manquante.

Le commit réellement suspect est :

a33063f
Implement voice input and document upload features
Il modifie app.py de manière massive :

+395 lignes
-258 lignes
et il ne s’est pas contenté d’ajouter Voice Input et Document Upload. Il a aussi déplacé de gros blocs entre la sidebar et la zone principale, jusqu’à proximité de :

# Chat Display
# Chat Input
C’est exactement le genre de modification qui peut déplacer, enfermer ou désynchroniser le traitement des messages et des URL. 


Chronologie probable
9aa1f5d
Suppression de l’ancien Image Studio
Puis :

43d4720
Ajout du nouvel Image Studio dans la sidebar
Puis :

a33063f
Déplacement de Voice Input et Document Upload dans la sidebar
+ restructuration massive de app.py
Puis :

91f75f7
Suppression incomplète du générateur d’image
→ erreur de parenthèse
Donc :

Image Studio cassé : 91f75f7

Liens et connexion au chat potentiellement cassés : a33063f

Le retour le plus propre
Si tout fonctionnait correctement juste avant le déplacement de Voice Input et Document Upload, la bonne version est probablement :

43d4720
Elle contient :

Image Studio fonctionnel ;

l’ancien chat encore en place ;

les liens probablement encore connectés ;

pas encore la grosse restructuration de a33063f.

Sur GitHub, tu peux restaurer app.py depuis ce commit sans supprimer tout l’historique.

Méthode simple depuis GitHub
Ouvre le commit 43d4720.

Clique sur app.py.

Clique sur les trois points ou View file.

Clique sur Raw.

Copie tout le contenu.

Remplace entièrement ton app.py actuel.

Fais un nouveau commit, par exemple :

Restore app.py before sidebar voice and document refactor
C’est la méthode la plus sûre pour toi : pas de terminal, pas de force push, et tous les commits restent visibles.

Ensuite, nous remettrons Voice Input et Document Upload dans la sidebar proprement, par petits blocs, sans toucher au moteur du chat, aux URL ni aux outils.



Texte collé(398).txt
Document

Texte collé (2)(16).txt
Document
j ai restaure cette version et reboot et rien 

Là, on a enfin la preuve exacte : restaurer app.py ne pouvait pas suffire, car le problème des liens vient de deux erreurs logiques, pas du déplacement visuel des studios.

Le tableau de bord dit clairement :

Provider: none
Status: disabled
Search skipped (mode=on_request)
et ensuite :

LLM Bridge: empty
No successful LLM response to synthesize.
Donc DeDe ne cherche rien, puis aucun LLM ne produit de réponse. Il retombe sur la phrase générique du DialogueManager. 


Problème 1 — Le profil « General » ne sélectionne aucun moteur
Dans ton app.py, tu as :

search_provider = []

if search_profile == "custom":
    search_provider = st.multiselect(...)
Pour le profil :

General — DuckDuckGo
search_profile vaut :

"general"
mais search_provider reste :

[]
Donc le Search Engine reçoit une liste vide et répond logiquement :

provider: none
status: disabled
C’est exactement ce qu’affiche ton test. 


Correction précise dans app.py
Repère ce bloc :

    search_provider = []

    if search_profile == "custom":

        search_provider = st.multiselect(
Remplace seulement le début par :

    search_provider_map = {
        "general": ["duckduckgo"],
        "scientific": [
            "duckduckgo",
            "arxiv",
            "crossref",
        ],
        "shopping": ["duckduckgo"],
        "news": ["duckduckgo"],
        "programming": ["duckduckgo"],
        "legal": ["duckduckgo"],
    }

    search_provider = search_provider_map.get(
        search_profile,
        [],
    )

    if search_profile == "custom":

        search_provider = st.multiselect(
Garde ensuite ton nettoyage existant :

        search_provider = [
            item.replace(" — planned", "")
            for item in search_provider
        ]
Avec cela :

General — DuckDuckGo
donnera réellement :

search_provider = ["duckduckgo"]
Problème 2 — Le mode on_request ignore la demande explicite
Ton test dit :

Search skipped (mode=on_request)
alors que le message est explicitement :

trouve moi des liens sur le communisme

Dans le CognitiveGovernor que tu m’as montré, cette branche arrive trop tôt :

if normalized_mode in {
    "on_request",
    "governor",
}:
    should_search = (
        normalized_semantic_decision == "SEARCH"
    )

    return ...
Elle traite on_request uniquement avec le classificateur sémantique et ignore :

explicit_request
Les vraies branches on_request et governor situées plus bas ne sont jamais atteintes. 


Tu dois donc appliquer la correction de decide_search() que je t’ai donnée précédemment.

Pour être certain, voici la partie essentielle :

        if normalized_mode == "on_request":
            should_search = (
                bool(explicit_request)
                or normalized_semantic_decision == "SEARCH"
            )

            return self._build_decision(
                mode=normalized_mode,
                should_search=should_search,
                reason=(
                    "External search was explicitly requested "
                    "for this message."
                    if explicit_request
                    else (
                        semantic_reason
                        or (
                            "Semantic classification detected a request "
                            "for external information."
                            if should_search
                            else (
                                "No external-search request "
                                "was detected."
                            )
                        )
                    )
                ),
                explicit_request=explicit_request,
                semantic_decision=normalized_semantic_decision,
            )
Et surtout, supprime l’ancienne branche commune :

if normalized_mode in {
    "on_request",
    "governor",
}:
Pourquoi DeDe répond seulement « Trump, je t’écoute »
Le rapport montre :

LLM Bridge
Bridge Status: empty
No successful LLM response to synthesize.
Donc le pipeline fait actuellement :

Message utilisateur
→ recherche désactivée
→ aucun résultat externe
→ aucun LLM réussi
→ réponse de secours du DialogueManager
La réponse :

Trump, je t’écoute. J’utiliserai mon analyse cognitive…

n’est pas une vraie réponse du LLM. C’est le fallback conversationnel.

Le nom Trump vient simplement de ton champ :

Owner ID: trump
Ce n’est pas lié à la panne.

Fais seulement ces deux corrections
app.py : associer les profils aux fournisseurs.

cognitive_governor.py : corriger decide_search() pour que on_request accepte une demande explicite.

Puis reboot et teste exactement :

Trouve-moi des liens sur le communisme.
Le tableau de bord devra afficher :

Provider: duckduckgo
Status: success
et non plus :

Provider: none
Status: disabled
Le retour au vieux commit a révélé la panne, mais ce n’était donc ni Image Studio ni Voice Input : c’était la sélection du moteur et la décision du Governor.


tu veut pas voir gouvernor avant ou autre chose

Oui, tu as raison : avant de modifier quoi que ce soit, montre-moi le cognitive_governor.py actuel.

Je veux vérifier si la version restaurée contient encore :

if normalized_mode in {
    "on_request",
    "governor",
}:
ou si cette partie a déjà changé.

Montre-moi aussi, juste après, le passage de app.py où tu construis :

search_provider
search_mode
explicit_request
semantic_decision
Avec ces deux blocs, on saura exactement si la panne vient :

du Governor ;

du choix du provider ;

ou du raccord entre app.py et le moteur.

Ne change rien avant cette vérification.



Texte collé(399).txt
Document

Oui ! Et là, je vois la panne. 🎯 


Tu as exactement le bug que je soupçonnais.

Regarde cette partie :

if normalized_mode in {
    "on_request",
    "governor",
}:
    should_search = (
        normalized_semantic_decision == "SEARCH"
    )

    return self._build_decision(...)
Le problème est le return.

Dès que search_mode vaut :

on_request
ou

governor
la fonction sort immédiatement.

Donc ces deux blocs plus bas :

if normalized_mode == "on_request":
et

if normalized_mode == "governor":
ne seront jamais exécutés.

Autrement dit :

off
↓

on_request
↓
RETURN

governor
↓
RETURN

always
Le reste du code est mort.

Ce que cela provoque
Quand tu es en :

Search mode

On Request
la logique devient uniquement :

should_search =
semantic_decision == "SEARCH"
Le booléen :

explicit_request
n'est plus utilisé.

Donc :

Trouve-moi des liens sur le communisme

ne déclenche pas la recherche si le classificateur répond :

SKIP
alors que justement le mode On Request devrait accepter une demande explicite.

Donc...
Je ne veux surtout pas que tu continues à chercher dans les autres fichiers.

On a trouvé un vrai bug logique.

Je veux que tu remplaces entièrement la méthode :

decide_search(...)
par celle que je t'avais préparée (la version qui sépare proprement off, always, on_request et governor).

Je suis maintenant quasiment certain que ce bug explique le comportement :

Provider : none

Status : disabled

Search skipped
Ensuite
Une fois cette méthode remplacée :

reboot ;

teste simplement :

Trouve-moi des liens sur le communisme
Si la recherche ne démarre toujours pas, alors on regardera app.py.

Mais je ne veux pas encore y toucher.

Parce qu'on vient de trouver une erreur logique suffisamment importante pour expliquer à elle seule la panne. Je préfère corriger une cause certaine, tester, puis seulement poursuivre si nécessaire. C'est la manière la plus fiable d'isoler le problème.


ni lien ni image 

D’accord : ce sont deux pannes séparées.

1. Les liens
Le Governor n’est pas l’unique cause. Dans ton app.py, le profil General — DuckDuckGo laisse actuellement :

search_provider = []
Le moteur reçoit donc :

Provider: none
Status: disabled
Remplace :

    search_provider = []

    if search_profile == "custom":
par :

    search_provider_map = {
        "general": ["duckduckgo"],
        "scientific": [
            "duckduckgo",
            "arxiv",
            "crossref",
        ],
        "shopping": ["duckduckgo"],
        "news": ["duckduckgo"],
        "programming": ["duckduckgo"],
        "legal": ["duckduckgo"],
    }

    search_provider = search_provider_map.get(
        search_profile,
        [],
    )

    if search_profile == "custom":
Cette correction est indispensable, même avec un Governor correct.

2. Les images
L’Image Studio visible et la génération d’image depuis le chat sont deux circuits différents.

Le Studio direct utilise :

st.session_state.tool_manager.run(
    tool_name="image_generator",
    ...
)
Mais une demande dans le chat dépend du ToolGovernor et du bloc qui traite typed_text.

Pour trouver cette seconde panne, montre-moi maintenant exactement :

tools/tool_governor.py
et dans app.py, tout le passage depuis :

typed_text = st.chat_input(...)
jusqu’à l’appel :

st.session_state.engine.analyze(...)
ou jusqu’à :

tool_manager.run(...)
Pour l’instant, applique seulement le search_provider_map. Cela doit rétablir les liens ; ensuite nous réparerons le routage des images sans toucher à nouveau au moteur de recherche.



Texte collé(400).txt
Document
et si je reviens a cette version

Oui, revenir à cette version est une bonne idée, parce qu’elle contient encore les deux circuits essentiels :

l’Image Studio autonome ;

le routage des images depuis le chat via ToolGovernor ;

le PDF Studio ;

l’appel normal à engine.analyze(...). 


Mais il y a un problème évident dans cette version : les profils de recherche ne choisissent toujours aucun provider.

Tu as encore :

search_provider = []

if search_profile == "custom":
Donc avec :

General — DuckDuckGo
search_provider reste vide.

C’est pourquoi les liens ne peuvent pas revenir, même en restaurant cette version.

Ce que je te conseille
Reviens à cette version, puis fais une seule correction dans app.py.

Remplace :

    search_provider = []

    if search_profile == "custom":
par :

    search_provider_map = {
        "general": ["duckduckgo"],
        "scientific": [
            "duckduckgo",
            "arxiv",
            "crossref",
        ],
        "shopping": ["duckduckgo"],
        "news": ["duckduckgo"],
        "programming": ["duckduckgo"],
        "legal": ["duckduckgo"],
    }

    search_provider = search_provider_map.get(
        search_profile,
        [],
    )

    if search_profile == "custom":
Et ne touche à rien d’autre pour ce test.

Pourquoi cette version est meilleure comme base
Elle contient bien :

tool_decision = (
    st.session_state.tool_governor.decide(
        text=text,
        available_tools=available_tools,
    )
)
puis :

if tool_decision.get("action") == "use_tool":
Donc une demande comme :

Crée une image d’un coucher de soleil à Barcelone
peut être routée vers :

image_generator
Elle contient également le Studio direct avec :

st.session_state.tool_manager.run(
    tool_name="image_generator",
Donc l’image devrait fonctionner dans les deux cas.

Ordre de test
Après restauration et ajout du search_provider_map :

teste dans l’Image Studio avec le bouton ;

teste dans le chat :
Crée une image d’un chat dans l’espace ;

teste les liens :
Trouve-moi des liens sur le communisme.

Si le Studio fonctionne mais pas l’image depuis le chat, le problème sera dans tool_governor.py.

Si les liens affichent encore :

Provider: none
alors la nouvelle version de app.py n’a pas été réellement déployée ou le bloc ajouté est mal placé.

Donc oui : restaure cette version, car elle est plus complète et plus saine comme point de départ, puis applique uniquement la carte des providers.



Texte collé(401).txt
Document
et cette version 

Cette version est presque identique à la précédente, mais elle est légèrement moins bonne comme base. 


La différence importante est ici :

Dans la version précédente, l’appel à engine.analyze(...) contenait :

document_context=st.session_state.get(
    "active_document",
    {},
),
Dans celle-ci, ce paramètre a disparu :

report = engine.analyze(
    text=text,
    enable_llm=enable_llm,
    ...
)
Donc le PDF Studio peut encore lire un PDF et le placer dans :

st.session_state.active_document
mais ce document n’est plus transmis au moteur cognitif. Le PDF devient visible dans l’interface, sans être réellement utilisé par DeDe dans la conversation.

Mon choix
Je choisirais la version précédente, celle où tu avais :

document_context=st.session_state.get(
    "active_document",
    {},
),
Elle conserve mieux la connexion entre :

PDF Studio ;

document actif ;

moteur DeDe ;

réponse du LLM.

Pour le reste, les deux versions ont le même défaut concernant les liens :

search_provider = []
avec aucun mapping automatique pour :

General — DuckDuckGo
Donc aucune des deux ne rétablira les liens sans la correction du search_provider_map.

Conclusion précise
Prends la version précédente, pas celle-ci.

Puis applique seulement :

    search_provider_map = {
        "general": ["duckduckgo"],
        "scientific": [
            "duckduckgo",
            "arxiv",
            "crossref",
        ],
        "shopping": ["duckduckgo"],
        "news": ["duckduckgo"],
        "programming": ["duckduckgo"],
        "legal": ["duckduckgo"],
    }

    search_provider = search_provider_map.get(
        search_profile,
        [],
    )
à la place de :

    search_provider = []
Et garde bien dans engine.analyze(...) :

document_context=st.session_state.get(
    "active_document",
    {},
),
C’est la base la plus complète des deux.




import streamlit as st
from openai import OpenAI
import tempfile
import os

from engine.doxa_engine_phase2 import DoxaEnginePhase2
from pathlib import Path
from core.real_world_anchor import RealWorldAnchor

from tools.media.image_generator import ImageGenerator
from tools.tool_manager import ToolManager
from tools.tool_governor import ToolGovernor
from tools.documents.pdf_reader import PDFReader

def pct(value):
if value is None:
return "N/A"
return f"{round(value * 100)}%"

def show_metric(label, value):
st.metric(label, pct(value))

def generate_speech(text: str) -> bytes | None:
if not text:
return None

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=text,
)

return speech.content
st.set_page_config(
page_title="DeDe",
page_icon="🧠",
layout="wide",
)

if "OPENAI_API_KEY" in st.secrets:
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

if "GOOGLE_API_KEY" in st.secrets:
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

--------------------------------------------------
DeDe Tool Layer
--------------------------------------------------
if "tool_manager" not in st.session_state:
tool_manager = ToolManager()

if "OPENAI_API_KEY" in st.secrets:
    tool_manager.register(
        ImageGenerator(
            api_key=st.secrets[
                "OPENAI_API_KEY"
            ],
        )
    )
    
tool_manager.register(
    PDFReader()
)

st.session_state.tool_manager = tool_manager
if "tool_governor" not in st.session_state:
st.session_state.tool_governor = ToolGovernor(
api_key=st.secrets[
"OPENAI_API_KEY"
],
)

if "tool_history" not in st.session_state:
st.session_state.tool_history = []

--------------------------------------------------
Force light theme / mobile readability
--------------------------------------------------
st.markdown(
"""
<style>
{
color-scheme: light !important;
}

html, body, .stApp {
    background-color: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}

[data-testid="stHeader"] {
    background-color: #ffffff !important;
}

[data-testid="stToolbar"] {
    color: #111827 !important;
}

[data-testid="stSidebar"] {
    background-color: #f9fafb !important;
    color: #111827 !important;
}

h1, h2, h3, h4, h5, h6,
p, span, div, label,
.stMarkdown, .stText {
    color: #111827 !important;
}

input, textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
}

button {
    background-color: #f3f4f6 !important;
    color: #111827 !important;
    border: 1px solid #d1d5db !important;
}

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
}

[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    color: #111827 !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }

    h1 {
        font-size: 1.6rem !important;
    }

    h2 {
        font-size: 1.3rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    p, div, span, label {
        font-size: 0.95rem !important;
    }

    [data-testid="stChatMessage"] {
        padding: 0.65rem !important;
    }
}
</style>
""",
unsafe_allow_html=True,
)

BANNER_PATH = Path("assets/Banner01.png")

if BANNER_PATH.exists():
st.image(str(BANNER_PATH), width="stretch")
else:
st.warning("Banner01.png not found in assets/")

st.markdown(
"""
<h1 style="text-align:center; margin-bottom:0.2rem;">
DeDe — Cognitive Daimon
</h1>

<h4 style="
    text-align:center;
    color:#9aa0a6;
    font-weight:400;
    margin-top:0;
    margin-bottom:0.3rem;">
    The First Evolving Cognitive AI Governor — Built on a Modular Architecture for Combinable AI Models and Tools
</h4>

<p style="
    text-align:center;
    color:#b8b8b8;
    font-style:italic;
    margin-top:0;">
    A little more time to think leads to more accurate answers.
</p>
""",
unsafe_allow_html=True,
)

st.caption("Phase 3 — Cognitive Mechanics")

with st.expander("Prototype status"):
st.success("DeDe Phase 3 prototype is running.")

st.caption(
    "Current status: CognitiveWorkspace, estimator layer, "
    "agent interpretation and shared cognitive mechanics."
)
--------------------------------------------------
DeDe Sidebar Configuration
--------------------------------------------------
with st.sidebar:

st.markdown("## ⚙️ DeDe Configuration")

st.caption(
    "Identity, reasoning models and knowledge sources."
)

# --------------------------------------------------
# Owner Identity
# --------------------------------------------------

st.markdown("### Identity")

owner_id = st.text_input(
    "Owner ID",
    value=st.session_state.get("owner_id", ""),
    placeholder="Ex: nicolas, delia, test_user",
)

if owner_id:
    safe_owner_id = "".join(
        char for char in owner_id.lower().strip()
        if char.isalnum() or char in ["_", "-"]
    )

    if st.session_state.get("owner_id") != safe_owner_id:
        st.session_state.owner_id = safe_owner_id
        st.session_state.conversation_history = []
        st.session_state.engine = DoxaEnginePhase2(
            user_id=safe_owner_id,
        )
        st.success(
            f"Memory owner set to: {safe_owner_id}"
        )
else:
    st.warning(
        "Enter an Owner ID to use an isolated persistent memory."
    )
    st.stop()

# --------------------------------------------------
# Conversation Session
# --------------------------------------------------

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "engine" not in st.session_state and st.session_state.get("owner_id"):
    st.session_state.engine = DoxaEnginePhase2(
        user_id=st.session_state.owner_id,
    )

# --------------------------------------------------
# Reasoning Models
# --------------------------------------------------

st.markdown("### Reasoning Models")

enable_llm = True

st.caption(
    "Choose which reasoning models DeDe may use."
)

llm_model_options = {
    "OpenAI": "openai",
    "Gemini": "gemini",
    "Mistral": "mistral",
    "DeepSeek — planned": "deepseek",
    "Qwen — planned": "qwen",
    "GLM — planned": "glm",
    "Claude — planned": "claude",
    "Nemotron — planned": "nemotron",
}

selected_llm_labels = st.multiselect(
    "Reasoning Models",
    list(llm_model_options.keys()),
    default=[
        "OpenAI",
    ],
)

llm_providers = [
    llm_model_options[label]
    for label in selected_llm_labels
]

llm_profile = "custom"

active_llms = [
    provider
    for provider in llm_providers
    if provider in ["openai", "gemini", "mistral"]
]

planned_llms = [
    provider
    for provider in llm_providers
    if provider not in ["openai", "gemini", "mistral"]
]

st.caption(
    "Active: "
    + (", ".join(active_llms) if active_llms else "none")
    + " | Planned: "
    + (", ".join(planned_llms) if planned_llms else "none")
)

# --------------------------------------------------
# Knowledge Sources
# --------------------------------------------------

st.markdown("### Knowledge Sources")

st.caption(
    "Choose the knowledge profile and search strategy."
)

search_profile_labels = {
    "General — DuckDuckGo": "general",
    "Scientific — DuckDuckGo + ArXiv + CrossRef": "scientific",
    "Shopping — DuckDuckGo": "shopping",
    "News — DuckDuckGo": "news",
    "Programming — DuckDuckGo": "programming",
    "Legal — DuckDuckGo": "legal",
    "Custom": "custom",
}

selected_search_label = st.selectbox(
    "Knowledge Profile",
    list(search_profile_labels.keys()),
    index=0,
)

search_profile = search_profile_labels[selected_search_label]

search_strategy = st.selectbox(
    "Search Strategy",
    [
        "Off",
        "On Request",
        "Governor (Beta)",
    ],
    index=1,
)

st.caption(
    "Off: no external search. "
    "On Request: search when the message requests external information. "
    "Governor: search automatically when verification is needed."
)

search_mode_map = {
    "Off": "off",
    "On Request": "on_request",
    "Governor (Beta)": "governor",
}

search_mode = search_mode_map[search_strategy]

search_provider = []

if search_profile == "custom":

    search_provider = st.multiselect(
        "Custom Search Providers",
        [
            "duckduckgo",
            "arxiv",
            "crossref",
            "brave — planned",
            "serpapi — planned",
            "pubmed — planned",
            "github — planned",
            "newsapi — planned",
            "semantic_scholar — planned",
            "eur_lex — planned",
        ],
        default=[
            "duckduckgo",
        ],
    )

    search_provider = [
        item.replace(" — planned", "")
        for item in search_provider
    ]
--------------------------------------------------
DeDe Image Studio
--------------------------------------------------
with st.expander(
"🎨 Image Studio",
expanded=False,
):
st.caption(
"Generate an image from a natural-language description."
)

image_prompt = st.text_area(
    "Describe the image",
    placeholder=(
        "Example: A cinematic sunset over Barcelona, "
        "vertical composition, realistic photography."
    ),
    key="image_studio_prompt",
    height=140,
)

image_format_labels = {
    "Square — 1:1": "1024x1024",
    "Portrait — 2:3": "1024x1536",
    "Landscape — 3:2": "1536x1024",
}

selected_image_format = st.selectbox(
    "Image format",
    list(image_format_labels.keys()),
    key="image_studio_format",
)

image_size = image_format_labels[
    selected_image_format
]

image_quality = st.selectbox(
    "Quality",
    [
        "low",
        "medium",
        "high",
    ],
    index=1,
    key="image_studio_quality",
)

transparent_background = st.checkbox(
    "Transparent background",
    value=False,
    key="image_studio_transparent",
)

if st.button(
    "Generate image",
    key="generate_image_button",
    type="primary",
):
    if not image_prompt.strip():
        st.warning(
            "Describe the image before starting generation."
        )

    elif "OPENAI_API_KEY" not in st.secrets:
        st.error(
            "OPENAI_API_KEY is missing from Streamlit secrets."
        )

    else:
        with st.spinner(
            "DeDe is generating the image..."
        ):
            tool_result = (
                st.session_state.tool_manager.run(
                    tool_name="image_generator",
                    arguments={
                        "prompt": image_prompt,
                        "size": image_size,
                        "quality": image_quality,
                        "transparent_background": (
                            transparent_background
                        ),
                    },
                )
            )

            image_result = {
                "tool": tool_result.get(
                    "tool",
                    "image_generator",
                ),
                "status": tool_result.get(
                    "status",
                    "error",
                ),
                "error": tool_result.get(
                    "error",
                ),
                "summary": tool_result.get(
                    "summary",
                    "",
                ),
                **tool_result.get(
                    "data",
                    {},
                ),
            }

        st.session_state[
            "last_generated_image"
        ] = image_result

generated_image = st.session_state.get(
    "last_generated_image",
    {},
)

if generated_image.get("status") == "success":
    image_bytes = generated_image.get(
        "image_bytes"
    )

    st.image(
        image_bytes,
        caption="Generated by DeDe Image Studio",
        width="stretch",
    )

    st.download_button(
        label="Download PNG",
        data=image_bytes,
        file_name="dede_generated_image.png",
        mime="image/png",
        key="download_generated_image",
    )

    st.caption(
        f'Model: {generated_image.get("model", "unknown")} '
        f'| Size: {generated_image.get("size", "unknown")} '
        f'| Quality: {generated_image.get("quality", "unknown")}'
    )

elif generated_image.get("status") == "error":
    st.error(
        generated_image.get(
            "error",
            "Image generation failed.",
        )
    )
--------------------------------------------------
DeDe PDF Studio
--------------------------------------------------
with st.expander(
"📄 PDF Studio",
expanded=False,
):
st.caption(
"Upload a PDF to extract and inspect its text."
)

uploaded_pdf = st.file_uploader(
    "Choose a PDF document",
    type=["pdf"],
    key="pdf_studio_uploader",
)

pdf_max_pages = st.number_input(
    "Maximum pages to read",
    min_value=1,
    max_value=500,
    value=100,
    step=1,
    key="pdf_studio_max_pages",
)

if st.button(
    "Read PDF",
    key="read_pdf_button",
    type="primary",
):
    if uploaded_pdf is None:
        st.warning(
            "Choose a PDF document first."
        )

    else:
        with st.spinner(
            "DeDe is reading the PDF..."
        ):
            pdf_result = (
                st.session_state.tool_manager.run(
                    tool_name="pdf_reader",
                    arguments={
                        "file_bytes": (
                            uploaded_pdf.getvalue()
                        ),
                        "filename": (
                            uploaded_pdf.name
                        ),
                        "max_pages": int(
                            pdf_max_pages
                        ),
                    },
                )
            )

        st.session_state[
            "last_pdf_result"
        ] = pdf_result

pdf_tool_result = st.session_state.get(
    "last_pdf_result",
    {},
)

if pdf_tool_result:
    pdf_status = pdf_tool_result.get(
        "status",
        "unknown",
    )

    pdf_data = pdf_tool_result.get(
        "data",
        {},
    )

    if pdf_status == "success":
        st.success(
            pdf_tool_result.get(
                "summary",
                "PDF read successfully.",
            )
        )

        # --------------------------------------------------
        # Active Document
        # --------------------------------------------------

        st.session_state.active_document = {
            "status": "ready",
            "source_type": "pdf",
            "filename": pdf_data.get(
                "filename",
                "document.pdf",
            ),
            "text": pdf_data.get(
                "text",
                "",
            ),
            "pages": pdf_data.get(
                "pages",
                [],
            ),
            "page_count": pdf_data.get(
                "page_count",
                0,
            ),
            "pages_read": pdf_data.get(
                "pages_read",
                0,
            ),
            "metadata": pdf_data.get(
                "metadata",
                {},
            ),
            "word_count": pdf_data.get(
                "word_count",
                0,
            ),
            "character_count": pdf_data.get(
                "character_count",
                0,
            ),
            "summary": pdf_tool_result.get(
                "summary",
                "",
            ),
        }

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Pages",
                pdf_data.get(
                    "page_count",
                    0,
                ),
            )

        with col2:
            st.metric(
                "Pages read",
                pdf_data.get(
                    "pages_read",
                    0,
                ),
            )

        with col3:
            st.metric(
                "Words",
                pdf_data.get(
                    "word_count",
                    0,
                ),
            )

        metadata = pdf_data.get(
            "metadata",
            {},
        )

        with st.expander(
            "PDF metadata"
        ):
            st.json(
                metadata
            )

        extracted_text = str(
            pdf_data.get(
                "text",
                "",
            )
        )

        st.text_area(
            "Extracted text preview",
            value=extracted_text[:20000],
            height=400,
            disabled=True,
            key="pdf_text_preview",
        )

        if len(extracted_text) > 20000:
            st.caption(
                "The preview is limited to "
                "20,000 characters."
            )

        st.download_button(
            label="Download extracted text",
            data=extracted_text.encode(
                "utf-8"
            ),
            file_name=(
                Path(
                    pdf_data.get(
                        "filename",
                        "document.pdf",
                    )
                ).stem
                + ".txt"
            ),
            mime="text/plain",
            key="download_pdf_text",
        )

    elif pdf_status == "no_text":
        st.warning(
            pdf_tool_result.get(
                "summary",
                (
                    "No text was found. "
                    "The document may require OCR."
                ),
            )
        )

    else:
        st.error(
            pdf_tool_result.get(
                "error",
                "PDF reading failed.",
            )
        )

# --------------------------------------------------
# Active PDF Status
# --------------------------------------------------

active_document = st.session_state.get(
    "active_document",
    {},
)

if active_document.get("status") == "ready":
    st.success(
        "Active document: "
        + active_document.get(
            "filename",
            "document.pdf",
        )
    )

    st.caption(
        f'{active_document.get("page_count", 0)} page(s) '
        f'| {active_document.get("word_count", 0)} words'
    )

    if st.button(
        "Remove active PDF",
        key="remove_active_pdf",
    ):
        st.session_state.pop(
            "active_document",
            None,
        )

        st.session_state.pop(
            "last_pdf_result",
            None,
        )

        st.rerun()
--------------------------------------------------
Chat Display
--------------------------------------------------
for index, turn in enumerate(st.session_state.conversation_history):
with st.chat_message("user"):
st.write(turn.get("user_input", ""))

with st.chat_message("assistant"):

    answer = turn.get("answer", "")

    st.write(answer)

    if answer:
        if st.button(
            "🔊 Listen",
            key=f"tts_history_{index}",
        ):
            audio = generate_speech(answer)
            st.audio(audio, format="audio/mp3")
--------------------------------------------------
Tool Conversation History
--------------------------------------------------
for index, item in enumerate(
st.session_state.tool_history
):
with st.chat_message("user"):
st.write(
item.get(
"user_input",
"",
)
)

with st.chat_message("assistant"):
    tool_name = item.get(
        "tool_name",
        "",
    )

    tool_result = item.get(
        "tool_result",
        {},
    )

    if (
        tool_name == "image_generator"
        and tool_result.get("status") == "success"
    ):
        image_data = tool_result.get(
            "data",
            {},
        )

        image_bytes = image_data.get(
            "image_bytes"
        )

        if image_bytes:
            st.image(
                image_bytes,
                caption=(
                    "Generated by DeDe"
                ),
                width="stretch",
            )

            st.download_button(
                label="Download PNG",
                data=image_bytes,
                file_name=(
                    f"dede_generated_image_{index + 1}.png"
                ),
                mime="image/png",
                key=f"download_tool_image_{index}",
            )

    else:
        st.error(
            tool_result.get(
                "error",
                "Tool execution failed.",
            )
        )
--------------------------------------------------
Voice Input / Speech to Text
--------------------------------------------------
st.subheader("Voice input")

audio_value = st.audio_input(
"Record a voice message",
sample_rate=16000,
key="voice_audio_input",
)

voice_text = ""

if audio_value:
st.audio(audio_value)

if st.button("Transcribe voice", key="transcribe_voice_button"):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav",
    ) as tmp:
        tmp.write(audio_value.getvalue())
        tmp_path = tmp.name

    with open(tmp_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )

    voice_text = transcript.strip()

    st.session_state["voice_text"] = voice_text
    st.success("Voice transcribed.")
    st.write(voice_text)
--------------------------------------------------
Chat Input
--------------------------------------------------
typed_text = st.chat_input("Message DeDe")

text = typed_text or st.session_state.get("voice_text", "")

if text:
st.session_state["voice_text"] = ""

if text:
available_tools = (
st.session_state.tool_manager.available_tools()
)

tool_decision = (
    st.session_state.tool_governor.decide(
        text=text,
        available_tools=available_tools,
    )
)

if tool_decision.get("action") == "use_tool":
    selected_tool = tool_decision.get(
        "tool_name",
        "",
    )

    selected_arguments = tool_decision.get(
        "arguments",
        {},
    )

    with st.chat_message("user"):
        st.write(text)

    with st.chat_message("assistant"):
        with st.spinner(
            "DeDe is using the requested tool..."
        ):
            tool_result = (
                st.session_state.tool_manager.run(
                    tool_name=selected_tool,
                    arguments=selected_arguments,
                )
            )

        if (
            selected_tool == "image_generator"
            and tool_result.get("status") == "success"
        ):
            image_data = tool_result.get(
                "data",
                {},
            )

            image_bytes = image_data.get(
                "image_bytes"
            )

            if image_bytes:
                st.image(
                    image_bytes,
                    caption="Generated by DeDe",
                    width="stretch",
                )

                st.download_button(
                    label="Download PNG",
                    data=image_bytes,
                    file_name="dede_generated_image.png",
                    mime="image/png",
                    key=(
                        "download_current_tool_image_"
                        f"{len(st.session_state.tool_history)}"
                    ),
                )

        else:
            st.error(
                tool_result.get(
                    "error",
                    "Tool execution failed.",
                )
            )

    st.session_state.tool_history.append(
        {
            "user_input": text,
            "tool_name": selected_tool,
            "tool_decision": tool_decision,
            "tool_result": tool_result,
        }
    )

    st.stop()

engine = st.session_state.engine

report = engine.analyze(
    text=text,
    document_context=st.session_state.get(
        "active_document",
        {},
    ),
    enable_llm=enable_llm,
    search_provider=search_provider,
    search_profile=(
        None if search_profile == "custom"
        else search_profile
    ),
    search_mode=search_mode.lower(),
    llm_profile="custom",
    llm_providers=llm_providers,
    conversation_history=st.session_state.conversation_history,
)

# --------------------------------------------------
# Real World Anchor Analysis
# --------------------------------------------------

anchor_engine = RealWorldAnchor()

source_analysis = report.get(
    "source_analysis",
    {},
)

search_validation = report.get(
    "search_validation",
    {},
)

cognitive_comparison = report.get(
    "cognitive_comparison",
    {},
)

anchor_result = anchor_engine.analyze(
    text=text,
    source_analysis=source_analysis,
    search_validation=search_validation,
    cognitive_comparison=cognitive_comparison,
)

report["real_world_anchor"] = anchor_result

st.session_state.conversation_history = report.get(
    "conversation_history",
    st.session_state.conversation_history,
)

user_response = report.get("user_response", {})

with st.chat_message("user"):
    st.write(text)

with st.chat_message("assistant"):

    final_answer = user_response.get(
        "final_answer",
        "No answer generated.",
    )

    st.write(final_answer)

    if st.button(
        "🔊 Listen",
        key=f"tts_current_{len(st.session_state.conversation_history)}",
    ):
        audio = generate_speech(final_answer)
        st.audio(audio, format="audio/mp3")

workspace = report["workspace"]
variables = workspace["variables"]
agent_results = report["agent_results"]
summary = report["summary"]
committee = report["committee"]

formulas = report["formulas"]
core = formulas["core"]
derived = formulas["derived"]

# --------------------------------------------------
# DeDe Cognitive Dashboard
# --------------------------------------------------

with st.expander("DeDe Cognitive Dashboard"):

    # --------------------------------------------------
    # Real World Anchor
    # --------------------------------------------------

    st.subheader("Ancrage au réel")

    st.write(anchor_result["label"])

    st.progress(anchor_result["score"])

    st.info(anchor_result["interpretation"])

    st.caption("Confiance épistémique")

    st.progress(
        anchor_result["epistemic_confidence"]
    )

    st.caption("Risque d'hallucination / suraffirmation")

    st.progress(
        anchor_result["hallucination_risk"]
    )

    st.write(
        "Action Governor :",
        anchor_result["governor_action"],
    )

    with st.expander("Détails de l'ancrage"):
        st.json(anchor_result["components"])

    # --------------------------------------------------
    # Active Document
    # --------------------------------------------------

    st.subheader("Active Document")

    active_document_report = report.get(
        "document_context",
        {},
    )

    if (
        active_document_report.get(
            "status"
        )
        == "ready"
    ):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Filename",
                active_document_report.get(
                    "filename",
                    "N/A",
                ),
            )

        with col2:
            st.metric(
                "Pages",
                active_document_report.get(
                    "page_count",
                    0,
                ),
            )

        with col3:
            st.metric(
                "Words",
                active_document_report.get(
                    "word_count",
                    0,
                ),
            )

        with st.expander(
            "Document metadata"
        ):
            st.json(
                active_document_report.get(
                    "metadata",
                    {},
                )
            )

    else:
        st.caption(
            "No active document."
        )

    # --------------------------------------------------
    # Search Engine
    # --------------------------------------------------
    
    search_result = report.get(
        "search_result",
        {},
    )
    
    st.subheader("Search Engine")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Provider",
            search_result.get(
                "provider",
                "none",
            ),
        )
    
    with col2:
        st.metric(
            "Status",
            search_result.get(
                "status",
                "disabled",
            ),
        )
    
    st.caption(
        search_result.get(
            "summary",
            "",
        )
    )
    
    with st.expander("Search Details"):
        st.json(search_result)

    # --------------------------------------------------
    # Universal Text Analysis
    # --------------------------------------------------

    st.subheader("Universal Text Analysis")

    user_text_analysis = report.get(
        "user_text_analysis",
        {},
    )

    web_text_analysis = report.get(
        "web_text_analysis",
        {},
    )

    final_response_analysis = report.get(
        "final_response_analysis",
        {},
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "User Analysis",
            user_text_analysis.get(
                "status",
                "N/A",
            ),
        )

    with col2:
        st.metric(
            "Web Items Analyzed",
            web_text_analysis.get(
                "item_count",
                0,
            ),
        )

    with col3:
        st.metric(
            "Final Response Analysis",
            final_response_analysis.get(
                "status",
                "N/A",
            ),
        )

    with st.expander("User Text Analysis"):
        st.json(user_text_analysis)

    with st.expander("Web Text Analysis"):
        st.json(web_text_analysis)

    with st.expander("Final Response Analysis"):
        st.json(final_response_analysis)

    # --------------------------------------------------
    # Cognitive Comparison
    # --------------------------------------------------

    st.subheader("Cognitive Comparison")

    cognitive_comparison = report.get(
        "cognitive_comparison",
        {},
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Comparison Status",
            cognitive_comparison.get(
                "status",
                "N/A",
            ),
        )

    with col2:
        st.metric(
            "Warnings",
            cognitive_comparison.get(
                "warning_count",
                0,
            ),
        )

    st.write(
        cognitive_comparison.get(
            "summary",
            "",
        )
    )

    warnings = cognitive_comparison.get(
        "warnings",
        [],
    )

    for warning in warnings:
        message = warning.get(
            "message",
            "",
        )

        severity = warning.get(
            "severity",
            "medium",
        )

        if severity == "high":
            st.error(message)
        else:
            st.warning(message)

    with st.expander(
        "Cognitive Comparison Details"
    ):
        st.json(cognitive_comparison)

    # --------------------------------------------------
    # Cognitive Source Analysis
    # --------------------------------------------------

    st.subheader("Cognitive Source Analysis")

    source_analysis = report.get(
        "source_analysis",
        {},
    )

    source_aggregate = source_analysis.get(
        "aggregate",
        {},
    )

    average_scores = source_aggregate.get(
        "average_scores",
        {},
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sources",
            source_analysis.get(
                "source_count",
                0,
            ),
        )

    with col2:
        evidence_score = average_scores.get(
            "evidence_level"
        )

        st.metric(
            "Average Evidence",
            (
                f"{evidence_score:.0%}"
                if isinstance(
                    evidence_score,
                    (int, float),
                )
                else "N/A"
            ),
        )

    with col3:
        relevance_score = average_scores.get(
            "relevance"
        )

        st.metric(
            "Average Relevance",
            (
                f"{relevance_score:.0%}"
                if isinstance(
                    relevance_score,
                    (int, float),
                )
                else "N/A"
            ),
        )

    st.write(
        source_analysis.get(
            "overall_summary",
            "",
        )
    )

    st.write("Source Types")

    st.json(
        source_aggregate.get(
            "source_type_counts",
            {},
        )
    )

    with st.expander(
        "Cognitive Source Analysis Details"
    ):
        st.json(source_analysis)

    # --------------------------------------------------
    # Autobiographical Memory
    # --------------------------------------------------

    st.subheader("Autobiographical Memory")
    st.json(report.get("autobiography", {}))

    st.subheader("Autobiographical Reasoning")
    st.json(report.get("autobiographical_reasoning", {}))
    
    # --------------------------------------------------
    # Phase 2 Cognitive Variables
    # --------------------------------------------------
    
    st.subheader("Phase 2 Cognitive Variables")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        show_metric("Grounding", variables["grounding"])

    with col2:
        show_metric("Integration", variables["integration"])

    with col3:
        show_metric("Closure", variables["closure"])

    with col4:
        show_metric("Reduction", variables["reduction"])

        
    # --------------------------------------------------
    # Phase 2 Cognitive Summary
    # --------------------------------------------------
    
    st.subheader("Phase 2 Cognitive Summary")

    st.write(summary["diagnosis"])

    st.metric(
        "Cognitive Balance",
        pct(summary["cognitive_balance"]),
    )

    committee = report["committee"]

    formulas = report["formulas"]
    core = formulas["core"]
    derived = formulas["derived"]
    
    # --------------------------------------------------
    # DOXA Formula Metrics
    # --------------------------------------------------
    
    st.subheader("DOXA Formula Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric("Support", core["support"])
        show_metric("Pressure", core["pressure"])

    with col2:
        show_metric("Mecroyance Pressure", core["mecroyance_pressure"])
        show_metric("Mecroyance Risk", core["mecroyance_risk"])

    with col3:
        show_metric("Revisability", core["revisability"])
        show_metric("Surconfidence", derived["surconfidence"])
        
    # --------------------------------------------------
    # Derived Cognitive Pressures
    # --------------------------------------------------
    
    st.subheader("Derived Cognitive Pressures")

    col1, col2 = st.columns(2)

    with col1:
        show_metric("Cognitive Closure", derived["cognitive_closure"])

    with col2:
        show_metric(
            "Forgotten Reduction",
            derived["forgotten_reduction_pressure"],
        )

    st.info(formulas["diagnosis"])
    
    # --------------------------------------------------
    # Semantic Graph
    # --------------------------------------------------

    semantic_graph = report.get("semantic_graph", {})

    # --------------------------------------------------
    # Universal Text Analysis
    # --------------------------------------------------
    
    st.subheader("Universal Text Analysis")
    
    st.write("USER")
    st.json(report.get("user_text_analysis", {}))
    
    st.write("WEB")
    st.json(report.get("web_text_analysis", {}))
    
    st.write("FINAL RESPONSE")
    st.json(report.get("final_response_analysis", {}))
    
    st.subheader("Semantic Graph")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Nodes", semantic_graph.get("node_count", 0))

    with col2:
        st.metric("Edges", semantic_graph.get("edge_count", 0))

    with col3:
        st.metric(
            "Causal Paths",
            semantic_graph.get("causal_path_count", 0),
        )

    if semantic_graph.get("causal_paths"):
        st.caption("Detected cognitive paths")

        for path in semantic_graph["causal_paths"]:
            readable_path = " → ".join(
                f'{step["source"]} / {step["relation"]} / {step["target"]}'
                for step in path["path"]
            )
            st.write(f"- {readable_path}")

    with st.expander("Semantic Graph details"):
        st.json(semantic_graph)
    
    # --------------------------------------------------
    # Graph Queries
    # --------------------------------------------------

    graph_queries = report.get("graph_queries", {})
    
    st.subheader("Graph Queries")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Central Nodes",
            len(graph_queries.get("central_nodes", [])),
        )

    with col2:
        key_paths = graph_queries.get("key_paths", {})
        available_paths = sum(
            1 for path in key_paths.values() if path
        )
        st.metric(
            "Available Key Paths",
            available_paths,
        )

    if graph_queries.get("central_nodes"):
        st.caption("Most connected cognitive nodes")

        for item in graph_queries["central_nodes"]:
            st.write(
                f'- {item["node"]} — degree {item["degree"]}'
            )
    
    with st.expander("LLM Context Preview"):
        st.json(
            graph_queries.get(
                "llm_context",
                {},
            )
        )
    
    with st.expander("Graph Query details"):
        st.json(graph_queries)
    
    # --------------------------------------------------
    # Inference Pattern 
    # --------------------------------------------------

    inference_patterns = report.get("inference_patterns", {})
    
    st.subheader("Inference Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Available Patterns",
            inference_patterns.get("available_pattern_count", 0),
        )
    
    with col2:
        st.metric(
            "Detected Patterns",
            inference_patterns.get("detected_pattern_count", 0),
        )
    
    st.write(
        inference_patterns.get(
            "summary",
            "",
        )
    )
    
    patterns = inference_patterns.get("patterns", [])
    
    if patterns:
        for pattern in patterns:
            confidence = pattern.get("confidence", 0)
    
            st.write(
                f'- **{pattern.get("name", "unknown")}** '
                f'[{pattern.get("type", "pattern")}] '
                f'— confidence {round(confidence * 100)}%'
            )
    
            st.caption(
                pattern.get(
                    "description",
                    "",
                )
            )
    
    with st.expander("Inference Pattern details"):
        st.json(inference_patterns)

    # --------------------------------------------------
    # Cognitive State Compiler
    # --------------------------------------------------

    cognitive_state = report.get("cognitive_state", {})
    
    st.subheader("Cognitive State Compiler")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Compiled Orientation",
            cognitive_state.get("orientation", "N/A"),
        )

    with col2:
        show_metric(
            "Compiled Confidence",
            cognitive_state.get("confidence"),
        )

    st.write(
        cognitive_state.get(
            "summary",
            "",
        )
    )

    with st.expander("Cognitive Focus"):
        st.json(
            cognitive_state.get(
                "cognitive_focus",
                [],
            )
        )

    with st.expander("Support"):
        st.json(
            cognitive_state.get(
                "support",
                [],
            )
        )

    with st.expander("Pressure"):
        st.json(
            cognitive_state.get(
                "pressure",
                [],
            )
        )

    with st.expander("Protective Mechanisms"):
        st.json(
            cognitive_state.get(
                "protective_mechanisms",
                [],
            )
        )

    with st.expander("Detected Dynamics"):
        st.json(
            cognitive_state.get(
                "detected_dynamics",
                [],
            )
        )

    with st.expander("Missing Dimensions"):
        st.json(
            cognitive_state.get(
                "missing_dimensions",
                [],
            )
        )

    with st.expander("Full Cognitive State"):
        st.json(cognitive_state)

    # --------------------------------------------------
    # Cognitive Reasoner
    # --------------------------------------------------

    cognitive_reasoning = report.get("cognitive_reasoning", {})

    st.subheader("Cognitive Reasoner")

    st.metric(
        "Reasoner Status",
        cognitive_reasoning.get("status", "N/A"),
    )

    nodes = cognitive_reasoning.get("nodes_considered", [])

    if nodes:
        st.caption("Nodes considered")
        st.write(", ".join(nodes))

    with st.expander("Hypotheses"):
        st.json(cognitive_reasoning.get("hypotheses", []))

    with st.expander("Contradictions"):
        st.json(cognitive_reasoning.get("contradictions", []))

    with st.expander("Explanations"):
        st.json(cognitive_reasoning.get("explanations", []))

    with st.expander("Missing Links"):
        st.json(cognitive_reasoning.get("missing_links", []))

    with st.expander("Predictions"):
        st.json(cognitive_reasoning.get("predictions", []))

    with st.expander("Counterfactuals"):
        st.json(cognitive_reasoning.get("counterfactuals", []))

    with st.expander("Inference Chains"):
        st.json(cognitive_reasoning.get("inference_chains", []))

    # --------------------------------------------------
    # Committee Reasoner
    # --------------------------------------------------

    committee_reasoning = report.get(
        "committee_reasoning",
        {},
    )

    st.subheader("Committee Reasoner")

    st.caption(
        "Transforms multiple LLM outputs into structured reasoning material "
        "before DeDe builds its final answer."
    )

    st.metric(
        "Reasoner Status",
        committee_reasoning.get("status", "N/A"),
    )

    st.write(
        committee_reasoning.get("summary", "")
    )

    with st.expander("Committee Reasoning Details"):
        st.json(committee_reasoning)
    
    # --------------------------------------------------
    # LLM Connector
    # --------------------------------------------------

    llm_package = report.get("llm_package", {})
    
    st.subheader("LLM Connector")

    st.metric(
        "LLM Package Status",
        llm_package.get("status", "N/A"),
    )

    st.write(llm_package.get("summary", ""))

    with st.expander("LLM System Prompt"):
        st.write(llm_package.get("system_prompt", ""))

    with st.expander("LLM Cognitive Context"):
        st.text(llm_package.get("cognitive_context", ""))

    with st.expander("Full LLM Prompt Package"):
        st.json(llm_package)

    # --------------------------------------------------
    # LLM Bridge
    # --------------------------------------------------

    llm_bridge_response = report.get("llm_bridge_response", {})

    st.subheader("LLM Bridge")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Bridge Status",
            llm_bridge_response.get("status", "N/A"),
        )

    with col2:
        st.metric(
            "Provider",
            llm_bridge_response.get("provider", "N/A"),
        )

        st.metric(
            "JSON Valid",
            str(llm_bridge_response.get("json_valid", False)),
        )

    st.write(
        llm_bridge_response.get(
            "summary",
            "",
        )
    )

    if llm_bridge_response.get("error"):
        st.error(
            llm_bridge_response["error"]
        )

    if llm_bridge_response.get("response"):
        with st.expander("LLM Raw Response"):
            st.write(
                llm_bridge_response["response"]
            )

    with st.expander("Full LLM Bridge Response"):
        st.json(llm_bridge_response)

    # --------------------------------------------------
    # LLM Engine
    # --------------------------------------------------
    
    llm_engine_response = report.get(
        "llm_engine_response",
        {},
    )
    
    st.subheader("Reasoning Models")
    
    st.caption(
        "Reasoning models are interchangeable LLM components used by DeDe "
        "after memory, search, semantic and cognitive preparation."
    )
    
    llm_committee = llm_engine_response.get(
        "committee",
        {},
    )
    
    if llm_committee:
    
        st.metric(
            "Committee Providers",
            llm_committee.get(
                "provider_count",
                0,
            ),
        )
    
        st.caption(
            llm_committee.get(
                "summary",
                "",
            )
        )
    
    st.metric(
        "Engine Status",
        llm_engine_response.get("status", "N/A"),
    )
    
    st.write(
        llm_engine_response.get("summary", "")
    )
    
    with st.expander("Reasoning Model Details"):
        st.json(llm_engine_response)

    # --------------------------------------------------
    # Cognitive Feedback
    # --------------------------------------------------

    cognitive_feedback = report.get("cognitive_feedback", {})

    st.subheader("Cognitive Feedback")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Feedback Status",
            cognitive_feedback.get("status", "N/A"),
        )

    with col2:
        show_metric(
            "Feedback Confidence",
            cognitive_feedback.get("confidence"),
        )

    st.write(
        cognitive_feedback.get(
            "summary",
            "",
        )
    )

    with st.expander("New Concepts"):
        st.json(
            cognitive_feedback.get(
                "new_concepts",
                [],
            )
        )

    with st.expander("New Relations"):
        st.json(
            cognitive_feedback.get(
                "new_relations",
                [],
            )
        )

    with st.expander("New Hypotheses"):
        st.json(
            cognitive_feedback.get(
                "new_hypotheses",
                [],
            )
        )

    with st.expander("New Questions"):
        st.json(
            cognitive_feedback.get(
                "new_questions",
                [],
            )
        )

    with st.expander("New Missing Dimensions"):
        st.json(
            cognitive_feedback.get(
                "new_missing_dimensions",
                [],
            )
        )

    with st.expander("New Counterfactuals"):
        st.json(
            cognitive_feedback.get(
                "new_counterfactuals",
                [],
            )
        )

    with st.expander("Full Cognitive Feedback"):
        st.json(cognitive_feedback)

    # --------------------------------------------------
    # Dialogue Decision
    # --------------------------------------------------
    
    dialogue_decision = report.get("dialogue_decision", {})

    st.subheader("Dialogue Strategy")
    
    st.metric(
        "Dialogue Mode",
        dialogue_decision.get("mode", "N/A"),
    )
    
    st.write(
        dialogue_decision.get("summary", "")
    )
    
    with st.expander("Dialogue Decision"):
        st.json(dialogue_decision)

    # --------------------------------------------------
    # Conversation Reasoning
    # --------------------------------------------------

    conversation_reasoning = report.get("conversation_reasoning", {})

    st.subheader("Conversation Reasoning")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Next Move",
            conversation_reasoning.get("move", "N/A"),
        )

    with col2:
        st.metric(
            "Follow-up",
            str(conversation_reasoning.get("is_follow_up", False)),
        )

    st.write(
        conversation_reasoning.get("summary", "")
    )

    if conversation_reasoning.get("next_prompt"):
        st.info(
            conversation_reasoning["next_prompt"]
        )

    with st.expander("Conversation Reasoning details"):
        st.json(conversation_reasoning)

    # --------------------------------------------------
    # Dialogue Profile
    # --------------------------------------------------

    dialogue_profile = report.get("dialogue_profile", {})

    st.subheader("Dialogue Profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Language",
            dialogue_profile.get("language", "N/A"),
        )

    with col2:
        st.metric(
            "Tone",
            dialogue_profile.get("tone", "N/A"),
        )

    with col3:
        st.metric(
            "Verbosity",
            dialogue_profile.get("verbosity", "N/A"),
        )

    st.write(
        dialogue_profile.get("summary", "")
    )

    with st.expander("Dialogue Profile details"):
        st.json(dialogue_profile)

    # --------------------------------------------------
    # Agent Interpretations
    # --------------------------------------------------
    
    st.subheader("Agent Interpretations")

    for name, result in agent_results.items():
        st.markdown(f"### {name}")

        st.info(result.get("summary", ""))

        if result.get("committee_reply"):
            st.write(result["committee_reply"])

        with st.expander(f"{name} details"):
            st.json(result)

    # --------------------------------------------------
    # Cognitive Committee
    # --------------------------------------------------
    
    st.subheader("Cognitive Committee")

    col1, col2 = st.columns(2)

    with col1:
        show_metric(
            "Committee Confidence",
            committee["confidence"],
        )

    with col2:
        st.metric(
            "Dominant Orientation",
            committee["dominant_orientation"],
        )

    st.info(committee["diagnosis"])

    # --------------------------------------------------
    # Committee Concerns
    # --------------------------------------------------

    if committee["concerns"]:
        st.subheader("Committee Concerns")

        for concern in committee["concerns"]:
            st.warning(concern)

    # --------------------------------------------------
    # Committee Recommendations
    # --------------------------------------------------
    
    st.subheader("Committee Recommendations")

    for recommendation in committee["recommendations"]:
        st.write(f"- {recommendation}")
            
    # --------------------------------------------------
    # Full Report
    # --------------------------------------------------
    
    st.subheader("Complete Cognitive Report")
    
    st.json(report)

Fermer
