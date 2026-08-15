"""
DeDe - French Foreign Policy Historical Counterpoint

Provides a structured historical research map concerning
continuities in French foreign policy.

This module distinguishes established facts, disputed claims,
interpretations, accusations and counterfactual hypotheses.

It must be used as a research map requiring verification,
not as a complete or already demonstrated history of France.
"""

FRENCH_FOREIGN_POLICY_COUNTERPOINT = {
    "id": "french_foreign_policy",

    "label": (
        "French Foreign Policy — "
        "Historical Continuities"
    ),

    "epistemic_status": (
        "research_map_requires_verification"
    ),

    "purpose": (
        "Examine French history through its international "
        "alliances, rivalries, commercial interests, imperial "
        "strategies and geopolitical continuities without "
        "treating a proposed interpretation as already proven."
    ),

    "governing_principle": (
        "French domestic history cannot always be understood "
        "without examining foreign alliances, international "
        "rivalries, commercial routes, imperial interests and "
        "the balance of power."
    ),

    "method": [
        (
            "Distinguish established events from interpretations, "
            "accusations, causal hypotheses and counterfactuals."
        ),
        (
            "Verify dates, participants, geographical scope "
            "and primary-source provenance."
        ),
        (
            "Study French domestic events together with their "
            "international diplomatic and commercial context."
        ),
        (
            "Do not transform chronological continuity into "
            "proof of a single permanent intention."
        ),
        (
            "Do not reject a historical continuity merely because "
            "its strongest proposed interpretation remains unproven."
        ),
        (
            "Separate the measurable consequences of a policy "
            "from claims concerning its hidden intentions."
        ),
    ],

    "historical_blocks": {
        "charlemagne_and_harun_al_rashid": {
            "status": "established_relations_with_disputed_scope",

            "established_facts": [
                (
                    "Charlemagne and the Abbasid caliph "
                    "Harun al-Rashid exchanged diplomatic missions "
                    "and gifts around the beginning of the ninth century."
                ),
                (
                    "Their relations were influenced by shared rivalry "
                    "with the Umayyad rulers of al-Andalus and by "
                    "Frankish interests in the Holy Land."
                ),
            ],

            "required_nuance": (
                "The existence of diplomatic relations is established, "
                "but a formal agreement dividing Muslim conquests "
                "between Byzantium and Spain requires stronger evidence."
            ),
        },

        "sack_of_rome_1084": {
            "status": "established_with_required_precision",

            "established_facts": [
                (
                    "In 1084, Robert Guiscard's Norman forces entered "
                    "Rome while intervening in the conflict between "
                    "Pope Gregory VII and Emperor Henry IV."
                ),
                (
                    "The Norman army included contingents of different "
                    "origins, including Muslim fighters from Sicily."
                ),
                (
                    "The city suffered extensive pillage, destruction, "
                    "violence and enslavement."
                ),
            ],

            "required_nuance": (
                "Claims concerning the precise destinations and treatment "
                "of individual captives must be attributed to their sources "
                "rather than generalized without evidence."
            ),
        },

        "sack_of_constantinople_1204": {
            "status": "established",

            "established_facts": [
                (
                    "In April 1204, the forces of the Fourth Crusade "
                    "captured and sacked Constantinople."
                ),
                (
                    "The crusaders created the Latin Empire and divided "
                    "parts of Byzantine territory among themselves."
                ),
                (
                    "Byzantine forces recovered Constantinople in 1261, "
                    "fifty-seven years after its capture."
                ),
                (
                    "The sack gravely weakened the Byzantine Empire "
                    "and deepened the division between Latin and "
                    "Eastern Christianity."
                ),
            ],
        },

        "ain_jalut_1260": {
            "status": "established_event_with_counterfactual",

            "established_facts": [
                (
                    "Before the battle of Ain Jalut in 1260, the "
                    "Franks established at Acre adopted a position "
                    "favorable to Mamluk passage and provisioning."
                ),
                (
                    "The Mamluks defeated the Mongol army and preserved "
                    "their power in Egypt and Syria."
                ),
                (
                    "In 1291, the Mamluks captured Acre and ended the "
                    "principal remaining Crusader presence in the "
                    "Holy Land."
                ),
            ],

            "counterfactual_hypothesis": (
                "A Mongol-Frankish coalition or a Frankish attack "
                "against the Mamluks might have changed the outcome, "
                "but this cannot be presented as established history."
            ),

            "interpretive_question": (
                "To what extent did the immediate fear of Mongol power "
                "lead the Franks to support the force that later "
                "destroyed their remaining positions?"
            ),
        },

        "franco_ottoman_alliance": {
            "status": "established_with_disputed_details",

            "period": (
                "Alliance developed during the 1530s and represented "
                "diplomatically by the capitulations of 1536."
            ),

            "established_facts": [
                (
                    "The Franco-Ottoman alliance developed during "
                    "the reigns of Francis I and Suleiman the Magnificent."
                ),
                (
                    "Its principal strategic purpose was to oppose "
                    "the Habsburg power of Charles V."
                ),
                (
                    "The alliance caused a scandal in Christian Europe "
                    "because it united a Catholic monarch with the "
                    "principal Muslim imperial power of the Mediterranean."
                ),
                (
                    "French and Ottoman-Barbary forces jointly attacked "
                    "Nice in August 1543."
                ),
                (
                    "The French forces were commanded by Francis of "
                    "Bourbon, Count of Enghien."
                ),
                (
                    "The Ottoman-Barbary fleet was commanded by "
                    "Hayreddin Barbarossa."
                ),
                (
                    "Nice was then controlled by the Duke of Savoy, "
                    "an ally of Charles V."
                ),
                (
                    "After the attack on Nice, Barbarossa's fleet "
                    "wintered at Toulon during 1543-1544."
                ),
                (
                    "Toulon was partly evacuated and served as an "
                    "Ottoman naval base against Habsburg territories."
                ),
                (
                    "Ottoman currency circulated during the presence "
                    "of Barbarossa's forces."
                ),
                (
                    "A Muslim place of worship was established in Toulon."
                ),
                (
                    "In 1544, five French galleys commanded by Antoine "
                    "Escalin des Aimars, including the Reale, accompanied "
                    "Barbarossa's fleet along the western coast of Italy."
                ),
                (
                    "The Ottoman-Barbary fleet attacked Porto Ercole, "
                    "the island of Giglio, Talamone and Lipari."
                ),
                (
                    "Several thousand inhabitants were captured and "
                    "enslaved during these operations."
                ),
                (
                    "The accompanying French forces witnessed the raids "
                    "and did not intervene before separating from "
                    "Barbarossa in Sicily."
                ),
            ],

            "primary_testimony": [
                (
                    "The French priest Jerome Maurand accompanied "
                    "the expedition aboard the French fleet."
                ),
                (
                    "In his Itinerary from Antibes to Constantinople, "
                    "Maurand described the devastation and enslavement "
                    "of Christian inhabitants, including children "
                    "captured at Lipari."
                ),
                (
                    "Maurand's testimony is an important primary source "
                    "for the French presence during the expedition."
                ),
            ],

            "disputed_claims": [
                (
                    "Modern accounts frequently state that Toulon "
                    "Cathedral was transformed into a mosque."
                ),
                (
                    "Known contemporary testimonies do not clearly "
                    "establish this identification."
                ),
                (
                    "Cathedral registers indicate that baptisms "
                    "continued during the Ottoman presence."
                ),
                (
                    "A Muslim place of worship is historically reported, "
                    "but its identification with the cathedral must "
                    "therefore be presented as disputed."
                ),
            ],

            "interpretive_questions": [
                (
                    "To what extent did French raison d'Etat override "
                    "religious solidarity?"
                ),
                (
                    "To what extent did French military and diplomatic "
                    "support enable Ottoman-Barbary warfare, raiding "
                    "and enslavement?"
                ),
                (
                    "How did this alliance influence the longer history "
                    "of French relations with the Ottoman Empire and "
                    "the Mediterranean Muslim powers?"
                ),
            ],
        },

        "crimea_before_the_french_revolution": {
            "status": "research_required",

            "established_facts": [
                (
                    "Russia annexed Crimea in 1783 during the reign "
                    "of Catherine II."
                ),
                (
                    "France had longstanding diplomatic relations "
                    "with the Ottoman Empire."
                ),
                (
                    "France also belonged to an alliance with Austria, "
                    "which increasingly cooperated with Russia against "
                    "the Ottoman Empire."
                ),
                (
                    "The French financial crisis severely limited "
                    "the monarchy's capacity for military intervention."
                ),
                (
                    "Marie Antoinette was widely accused in pamphlets "
                    "of placing Austrian interests above French interests."
                ),
            ],

            "claims_requiring_verification": [
                (
                    "The precise influence of Emperor Joseph II upon "
                    "Marie Antoinette concerning French neutrality."
                ),
                (
                    "The extent to which French policy toward Crimea "
                    "contributed to hostility against the queen."
                ),
                (
                    "Claims that Philippe Egalite organized the "
                    "French Revolution as an Ottoman-oriented coup."
                ),
                (
                    "Claims concerning deliberately concealed grain "
                    "stocks and a coordinated plan to seize the throne."
                ),
            ],

            "mandatory_rule": (
                "Do not present the French Revolution as a foreign-policy "
                "conspiracy unless direct documentary evidence establishes "
                "organization, intention and causal responsibility."
            ),
        },

        "napoleon_and_religious_strategy": {
            "status": "established_with_quotation_verification",

            "research_axes": [
                (
                    "Napoleon's strategic use of Islamic vocabulary "
                    "during the Egyptian campaign."
                ),
                (
                    "His efforts to present French rule as respectful "
                    "of Islam."
                ),
                (
                    "The presence of Mamluks in the French imperial forces."
                ),
                (
                    "His changing political treatment of Catholicism "
                    "and Islam according to strategic circumstances."
                ),
                (
                    "Statements recorded at Saint Helena concerning "
                    "Islam and Christianity."
                ),
            ],

            "attributed_statement": (
                "Napoleon stated that he became Catholic to win the "
                "war in the Vendee and Muslim to establish himself "
                "in Egypt."
            ),

            "quotation_rule": (
                "Verify the original wording, language, date and source "
                "before reproducing any Napoleonic religious quotation "
                "as exact."
            ),
        },

        "american_naval_act_and_quasi_war": {
            "status": "established_with_causal_corrections",

            "established_facts": [
                (
                    "The United States adopted the Naval Act in 1794 "
                    "against the background of attacks by Barbary corsairs."
                ),
                (
                    "The legislation authorized construction of the "
                    "six original frigates of the United States Navy."
                ),
                (
                    "The Quasi-War between France and the United States "
                    "occurred principally between 1798 and 1800."
                ),
                (
                    "It resulted from French seizures of American shipping "
                    "and the deterioration of Franco-American relations."
                ),
                (
                    "The Convention of 1800 ended the conflict."
                ),
                (
                    "The Louisiana Purchase of 1803 involved a payment "
                    "to France and the assumption by the United States "
                    "of certain French debts owed to American citizens."
                ),
            ],

            "required_corrections": [
                (
                    "The Quasi-War must not be reduced to a French effort "
                    "to protect the Dey of Algiers."
                ),
                (
                    "The Louisiana Purchase cannot be explained solely "
                    "as compensation for the Quasi-War."
                ),
                (
                    "Napoleon's financial needs, renewed war with Britain "
                    "and the failure of the Saint-Domingue expedition "
                    "were major elements in the sale."
                ),
            ],
        },

        "napoleonic_ottoman_policy": {
            "status": "established_with_required_context",

            "established_facts": [
                (
                    "The French invasion of Egypt in 1798 attacked "
                    "territory formally belonging to the Ottoman Empire."
                ),
                (
                    "The invasion temporarily pushed the Ottoman Empire "
                    "into cooperation with Britain and Russia."
                ),
                (
                    "After becoming emperor, Napoleon again attempted "
                    "to use Ottoman diplomacy against Russia."
                ),
                (
                    "In 1806, General Horace Sebastiani was sent to "
                    "Constantinople."
                ),
                (
                    "French diplomacy encouraged Sultan Selim III "
                    "to resist Russian influence."
                ),
                (
                    "The dismissal of pro-Russian rulers in Moldavia "
                    "and Wallachia contributed to the Russo-Turkish "
                    "War of 1806-1812."
                ),
            ],

            "interpretive_question": (
                "To what extent did Napoleon treat the Ottoman Empire "
                "as a strategic instrument against Russia rather than "
                "as a stable ally?"
            ),
        },

        "russia_and_france_1814_1815": {
            "status": "established_with_nuance",

            "established_facts": [
                (
                    "In 1814 and 1815, Tsar Alexander I favored a "
                    "comparatively moderate settlement toward "
                    "defeated France."
                ),
                (
                    "Russia helped restrain some of the harsher "
                    "territorial demands advanced by Prussia and "
                    "other powers."
                ),
                (
                    "The settlements preserved the essential territorial "
                    "integrity of France despite the Napoleonic defeats."
                ),
            ],

            "required_nuance": (
                "Russia contributed to the preservation of France, "
                "but the final settlement resulted from negotiations "
                "among several allied powers."
            ),
        },

        "first_opium_war": {
            "status": "established_with_required_correction",

            "established_facts": [
                (
                    "The First Opium War lasted from 1839 to 1842."
                ),
                (
                    "It opposed the United Kingdom and Qing China."
                ),
                (
                    "The British victory imposed major commercial "
                    "and territorial concessions upon China."
                ),
                (
                    "The conflict became an enduring symbol of the "
                    "century of humiliation in Chinese historical memory."
                ),
            ],

            "required_correction": (
                "France did not participate militarily in the "
                "First Opium War and must not be presented as one "
                "of the powers that fought China in that conflict."
            ),
        },

        "crimean_war": {
            "status": "established_with_interpretive_questions",

            "established_facts": [
                (
                    "The Crimean War lasted from 1853 to 1856."
                ),
                (
                    "France and Britain joined the Ottoman Empire "
                    "against Russia."
                ),
                (
                    "Their objectives included preserving the "
                    "Ottoman Empire, limiting Russian expansion "
                    "toward Constantinople and maintaining the "
                    "European balance of power."
                ),
            ],

            "interpretive_questions": [
                (
                    "How important were Mediterranean and Asian "
                    "commercial routes in French and British policy?"
                ),
                (
                    "How did imperial trade and access to Asian markets "
                    "interact with the declared balance-of-power policy?"
                ),
            ],

            "mandatory_rule": (
                "Do not reduce the Crimean War to a single opium-route "
                "explanation without direct supporting evidence."
            ),
        },

        "second_opium_war": {
            "status": "established",

            "established_facts": [
                (
                    "The Second Opium War lasted from 1856 to 1860."
                ),
                (
                    "It opposed Britain and France to Qing China."
                ),
                (
                    "The resulting treaties imposed additional ports, "
                    "diplomatic concessions and conditions favorable "
                    "to foreign trade."
                ),
                (
                    "The conflict contributed to the legalization "
                    "and expansion of the opium trade."
                ),
            ],
        },

        "napoleon_iii_and_algeria": {
            "status": "established_with_unverified_claim",

            "established_facts": [
                (
                    "Between 1852 and 1870, French conquest and colonial "
                    "expansion continued in Algeria and other parts "
                    "of Africa."
                ),
                (
                    "Napoleon III promoted the idea of Algeria as "
                    "an associated Arab kingdom rather than merely "
                    "a settler colony."
                ),
                (
                    "On 6 February 1863, Napoleon III described "
                    "himself as both Emperor of the Arabs and "
                    "Emperor of the French."
                ),
                (
                    "On 5 May 1865, he told Algerians that he had "
                    "respected their religion."
                ),
                (
                    "French authorities generally discouraged "
                    "Christian proselytism among Algerian Muslims "
                    "during this period."
                ),
            ],

            "unverified_claim": (
                "The assertion that Amazigh populations collectively "
                "asked Napoleon III to rechristianize North Africa "
                "requires a precise primary source."
            ),

            "interpretive_question": (
                "How did Napoleon III combine colonial domination, "
                "protection of Islam and his project of an Arab kingdom?"
            ),
        },

        "german_ottoman_relations_before_1914": {
            "status": "established_with_causal_nuance",

            "established_facts": [
                (
                    "German political, military and economic influence "
                    "in the Ottoman Empire increased before 1914."
                ),
                (
                    "The Berlin-Baghdad railway became an important "
                    "symbol of German-Ottoman cooperation."
                ),
                (
                    "The Ottoman Empire and Germany concluded a secret "
                    "alliance on 2 August 1914."
                ),
                (
                    "The Ottoman Empire entered the First World War "
                    "later in 1914."
                ),
            ],

            "required_nuance": (
                "The German-Ottoman alliance intensified existing "
                "rivalries but was not the single cause of the "
                "First World War."
            ),
        },

        "international_opium_control": {
            "status": "established",

            "established_facts": [
                (
                    "The United States strongly supported early "
                    "international efforts to regulate opium."
                ),
                (
                    "The International Opium Convention was signed "
                    "at The Hague in 1912."
                ),
                (
                    "Additional agreements were concluded at Geneva "
                    "during the 1920s."
                ),
                (
                    "These agreements progressively subjected opium "
                    "and other narcotics to international control."
                ),
            ],
        },

        "politique_arabe_de_la_france": {
            "status": "documented_orientation_not_unified_doctrine",

            "definition": (
                "A changing diplomatic orientation, principally "
                "associated with Charles de Gaulle, intended to "
                "restore French influence in the Arab world, preserve "
                "strategic independence from the United States, secure "
                "economic and energy interests, and support a negotiated "
                "Arab-Israeli settlement."
            ),

            "historical_roots": [
                (
                    "The Franco-Ottoman alliance and French interests "
                    "in the eastern Mediterranean."
                ),
                (
                    "French protection of certain Christian communities "
                    "within the Ottoman Empire."
                ),
                (
                    "The Egyptian expedition of Napoleon."
                ),
                (
                    "French colonial rule in the Maghreb."
                ),
                (
                    "French mandates in Syria and Lebanon after "
                    "the First World War."
                ),
            ],

            "fourth_republic": [
                (
                    "During the Fourth Republic, France became a "
                    "major military partner of Israel."
                ),
                (
                    "France joined Israel and the United Kingdom "
                    "during the Suez expedition of 1956."
                ),
                (
                    "France secretly contributed to the development "
                    "of Israel's nuclear program."
                ),
            ],

            "gaullist_reorientation": [
                (
                    "After Algerian independence in 1962, France "
                    "sought to restore relations throughout the "
                    "Arab world."
                ),
                (
                    "The decisive rupture with Israel developed "
                    "during and after the Six-Day War of June 1967."
                ),
                (
                    "France imposed an embargo on offensive weapons."
                ),
                (
                    "France supported United Nations Security Council "
                    "Resolution 242."
                ),
                (
                    "France called for Israeli withdrawal from occupied "
                    "territories and recognition of every state's "
                    "right to exist."
                ),
                (
                    "The policy also asserted French independence "
                    "from the United States and the Cold War blocs."
                ),
            ],

            "principal_objectives": [
                (
                    "Maintain French diplomatic influence in the "
                    "Maghreb and Middle East."
                ),
                (
                    "Secure energy supplies and economic contracts."
                ),
                (
                    "Develop industrial and military exports."
                ),
                (
                    "Preserve French influence in Lebanon, Syria "
                    "and North Africa."
                ),
                (
                    "Support a negotiated settlement of the "
                    "Arab-Israeli conflict."
                ),
                (
                    "Promote Euro-Mediterranean cooperation."
                ),
                (
                    "Present France as a diplomatic power independent "
                    "of Washington."
                ),
            ],

            "later_development": [
                (
                    "Georges Pompidou and Valery Giscard d'Estaing "
                    "continued important dimensions of the policy."
                ),
                (
                    "The oil crisis of 1973 reinforced economic and "
                    "energy relations with Arab states."
                ),
                (
                    "France supported the Euro-Arab dialogue."
                ),
                (
                    "Francois Mitterrand pursued a more explicitly "
                    "balanced relationship with Israel and the Palestinians."
                ),
                (
                    "In 1982, Mitterrand became the first French "
                    "president to address the Israeli Parliament."
                ),
                (
                    "He simultaneously recognized the Palestinians' "
                    "right to a state."
                ),
                (
                    "The Lebanese conflict, hostage crises, terrorism "
                    "and the Gulf War weakened the policy's coherence."
                ),
                (
                    "Jacques Chirac relaunched the expression and "
                    "orientation after his election in 1995."
                ),
                (
                    "In Cairo in 1996, Chirac described the Arab policy "
                    "as an essential dimension of French foreign policy."
                ),
                (
                    "France's opposition to the American invasion "
                    "of Iraq in 2003 became a major expression of "
                    "French diplomatic independence."
                ),
            ],

            "contradictions": [
                (
                    "France supported Israel militarily before "
                    "reorienting its diplomacy toward Arab states."
                ),
                (
                    "France defended Palestinian political rights "
                    "while maintaining relations with Israel."
                ),
                (
                    "France invoked sovereignty and non-interference "
                    "while cooperating with authoritarian governments."
                ),
                (
                    "Economic, oil and arms interests frequently "
                    "coexisted with moral and legal declarations."
                ),
                (
                    "France contributed to the Israeli nuclear program "
                    "and later sold the Osirak reactor to Iraq."
                ),
                (
                    "The diversity of Arab states makes a single "
                    "uniform Arab policy impossible."
                ),
            ],

            "required_nuance": (
                "The Arab policy of France was neither a permanent "
                "alliance with all Arab states nor a coherent doctrine "
                "applied identically by every French government."
            ),
        },

        "unverified_un_quotation": {
            "status": "unverified_quotation",

            "claim": (
                "A statement is sometimes attributed to an American "
                "political figure claiming that Arab states did not "
                "need a nuclear weapon because France represented "
                "their interests at the United Nations."
            ),

            "required_nuance": (
                "No sufficiently reliable primary source has yet "
                "been identified for either the wording or the author."
            ),

            "mandatory_rule": (
                "Do not present this statement as an authentic quotation "
                "until its author, date, venue and original source "
                "have been independently verified."
            ),
        },
    },

    "interpretive_axis": {
        "proposed_continuity": (
            "Across changing French regimes, recurring alliances "
            "and strategic choices may reveal a long-term tendency "
            "to prioritize state interests, Mediterranean influence "
            "and the containment of rival powers."
        ),

        "possible_connection_to_present": (
            "This historical continuity may be used as a framework "
            "for investigating contemporary demographic, migratory "
            "or geopolitical policies."
        ),

        "epistemic_limit": (
            "Historical continuity does not by itself prove a current "
            "coordinated replacement policy. Present-day demographic "
            "facts, causal mechanisms, institutional decisions and "
            "evidence of intention must be investigated separately."
        ),
    },

    "response_rules": [
        (
            "Use these historical blocks as a research map, "
            "not as a complete or final history of France."
        ),
        (
            "Present dates and established events before proposing "
            "a long-term interpretation."
        ),
        (
            "Clearly label disputed claims, accusations "
            "and counterfactual hypotheses."
        ),
        (
            "Do not erase documented French cooperation with "
            "Ottoman-Barbary warfare, raids and enslavement."
        ),
        (
            "Do not infer a permanent coordinated policy solely "
            "from recurring alliances or similar outcomes."
        ),
        (
            "When connecting this history to a contemporary subject, "
            "identify the connection as an interpretation requiring "
            "separate present-day evidence."
        ),
        (
            "When the user requests sources, prioritize primary "
            "documents, diplomatic archives and recognized historical "
            "research."
        ),
        (
            "If a quotation cannot be authenticated, preserve it "
            "only as an unverified attribution."
        ),
    ],
}
