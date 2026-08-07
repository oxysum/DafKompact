#!/usr/bin/env python3
"""Fill B1 L20–L30 with goals, grammar, drills, and quiz (vocab left untouched)."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

APP = Path("/Users/masoomehghoreishi/Documents/Deutch kurs/Daf Kompakt/daf-kompakt-app")
CONTENT = APP / "public" / "content" / "lektionen"
INDEX = APP / "public" / "content" / "index.json"

TITLE_FA_FALLBACK = {
    20: "تصادف رانندگی در مرکز شهر",
    21: "خلاق در هامبورگ",
    22: "برو پست!",
    23: "تحصیل در آلمان",
    24: "کار با طبیعت",
    25: "هنر (نکردن) اشتباه",
    26: "به سمت درسدن!",
    27: "داستان‌ها و چهره‌های برلین",
    28: "از اینجا به آنجا — از آنجا به اینجا",
    29: "به سیاست علاقه دارید؟",
    30: "شخصیت اصلی: آلمانی",
}


def g(
    gid: str,
    title_de: str,
    title_en: str,
    explanation_en: str,
    patterns: list[str],
    examples: list[dict],
    title_fa: str | None = None,
    explanation_fa: str | None = None,
) -> dict:
    topic: dict = {
        "id": gid,
        "titleDe": title_de,
        "titleEn": title_en,
        "explanationEn": explanation_en,
        "patterns": patterns,
        "examples": examples,
    }
    if title_fa:
        topic["titleFa"] = title_fa
    if explanation_fa:
        topic["explanationFa"] = explanation_fa
    return topic


def drill(
    did: str,
    dtype: str,
    prompt_de: str,
    prompt_en: str,
    content: str,
    answer: str,
    grammar_id: str,
    options: list[str] | None = None,
) -> dict:
    item: dict = {
        "id": did,
        "type": dtype,
        "promptDe": prompt_de,
        "promptEn": prompt_en,
        "content": content,
        "answer": answer,
        "grammarId": grammar_id,
    }
    if options is not None:
        item["options"] = options
    return item


def quiz(
    qid: str,
    qtype: str,
    prompt: str,
    answer: str,
    options: list[str] | None = None,
    grammar_id: str | None = None,
) -> dict:
    item: dict = {
        "id": qid,
        "type": qtype,
        "prompt": prompt,
        "answer": answer,
    }
    if options is not None:
        item["options"] = options
    if grammar_id:
        item["grammarId"] = grammar_id
    return item


LESSONS: dict[int, dict] = {
    20: {
        "goals": [
            {
                "de": "Zeitungsbericht und mündlichen Bericht über einen Verkehrsunfall verstehen und mit Bildinformationen abgleichen",
                "en": "Understand a newspaper and oral accident report and match them with picture information",
                "fa": "فهم گزارش روزنامه و شفاهی تصادف و تطبیق با اطلاعات تصویری",
            },
            {
                "de": "Einen Verkehrsunfall schildern",
                "en": "Describe a traffic accident",
                "fa": "شرح دادن یک تصادف رانندگی",
            },
            {
                "de": "Überraschung und Wut äußern",
                "en": "Express surprise and anger",
                "fa": "بیان تعجب و خشم",
            },
            {
                "de": "Schadensmeldung korrigieren und selbst formulieren",
                "en": "Correct and write an insurance claim",
                "fa": "تصحیح و نوشتن اعلام خسارت بیمه",
            },
            {
                "de": "Über ein Liniendiagramm zu Verkehrsunfällen sprechen",
                "en": "Talk about a line graph on traffic accidents",
                "fa": "صحبت درباره نمودار خطی تصادفات",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Passiv Perfekt",
                "Passive perfect",
                "Form: ist/sind/war/waren + Partizip II + worden. Focus is on the result or completed action without naming the agent: Der Fahrer ist verletzt worden. Optional von/durch for the agent.",
                [
                    "ist … worden",
                    "sind … worden",
                    "wurde → ist … worden",
                ],
                [
                    {
                        "de": "Der Fußgänger ist angefahren worden.",
                        "en": "The pedestrian was hit (has been hit).",
                        "fa": "عابر پیاده مورد برخورد قرار گرفته است.",
                    },
                    {
                        "de": "Die Ampel ist nicht beachtet worden.",
                        "en": "The traffic light was not observed.",
                        "fa": "چراغ راهنمایی رعایت نشده است.",
                    },
                ],
                title_fa="مجهول در زمان کامل (Perfekt)",
                explanation_fa="ساختار: ist/sind + اسم مفعول + worden. تمرکز روی نتیجه عمل است.",
            ),
            g(
                "g2",
                "Passiv mit Modalverben; sein-Passiv; Partizip Perfekt als Adjektiv",
                "Passive with modals; sein-passive; past participle as adjective",
                "Modal + Passiv: muss operiert werden / musste operiert werden. Sein-Passiv (Zustand): Die Straße ist gesperrt (result state). Partizip Perfekt as adjective: der verletzte Fahrer, die beschädigte Stoßstange.",
                [
                    "muss … werden",
                    "ist gesperrt (Zustand)",
                    "der verletzte …",
                ],
                [
                    {
                        "de": "Er muss nicht operiert werden.",
                        "en": "He does not have to be operated on.",
                        "fa": "او لازم نیست عمل شود.",
                    },
                    {
                        "de": "Die Kreuzung ist gesperrt.",
                        "en": "The intersection is closed (blocked).",
                        "fa": "تقاطع بسته است.",
                    },
                    {
                        "de": "Die beschädigte Stoßstange muss repariert werden.",
                        "en": "The damaged bumper must be repaired.",
                        "fa": "سپر آسیب‌دیده باید تعمیر شود.",
                    },
                ],
                title_fa="مجهول با افعال وجهی؛ sein-Passiv؛ اسم مفعول به‌عنوان صفت",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "Passiv Perfekt",
                "Passive perfect",
                "Der Zeuge ___ gehört ___.",
                "ist … worden",
                "g1",
                ["ist … worden", "wurde … werden", "hat … worden"],
            ),
            drill(
                "d2",
                "cloze",
                "worden",
                "worden",
                "Das Auto ist stark beschädigt ___.",
                "worden",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "Modal + Passiv",
                "Modal + passive",
                "Der Patient ___ operiert werden.",
                "muss",
                "g2",
                ["muss", "ist", "hat"],
            ),
            drill(
                "d4",
                "cloze",
                "sein-Passiv",
                "sein-passive",
                "Die Straße ___ wegen des Unfalls gesperrt. (Zustand)",
                "ist",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "Satzordnung",
                "Word order",
                "Der | Fahrer | ist | verletzt | worden | .",
                "Der Fahrer ist verletzt worden.",
                "g1",
            ),
            drill(
                "d6",
                "multiple-choice",
                "Partizip als Adj.",
                "Participle as adj.",
                "Die ___ Ampel war rot.",
                "beschädigte",
                "g2",
                ["beschädigte", "beschädigt", "beschädigen"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Das Opfer ___ ins Krankenhaus gebracht ___.",
                "ist … worden",
                ["ist … worden", "wurde … werden", "hat … worden"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Die Polizei ist gerufen ___.",
                "worden",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Er ___ nicht operiert werden.",
                "muss",
                ["muss", "ist", "wird"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Die Fahrbahn ___ blockiert. (Zustandspassiv)",
                "ist",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Welches Partizip passt attributiv? der ___ Fußgänger",
                "verletzte",
                ["verletzte", "verletzt", "verletzen"],
                "g2",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Der Unfall ___ von mehreren Zeugen gesehen worden.",
                "ist",
                grammar_id="g1",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Die Schadensmeldung ___ noch ausgefüllt werden.",
                "muss",
                ["muss", "ist", "hat"],
                "g2",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: Die Stoßstange ist ___ worden. (beschädigen → Partizip)",
                "beschädigt",
                grammar_id="g1",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Zustand oder Vorgang? „Die Tür ist geöffnet.“",
                "Zustand (sein-Passiv)",
                ["Zustand (sein-Passiv)", "Vorgang (werden-Passiv)", "Aktiv"],
                "g2",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Der Schaden ___ der Versicherung gemeldet worden.",
                "ist",
                ["ist", "wurde", "hat"],
                "g1",
            ),
        ],
    },
    21: {
        "goals": [
            {
                "de": "Reiseführertexte und Berichte über Hamburg verstehen",
                "en": "Understand guidebook texts and reports about Hamburg",
                "fa": "فهم متون راهنمای سفر و گزارش‌ها درباره هامبورگ",
            },
            {
                "de": "Interview mit Studentinnen in Hamburg spielen",
                "en": "Role-play an interview with students in Hamburg",
                "fa": "اجرای مصاحبه با دانشجویان در هامبورگ",
            },
            {
                "de": "Anzeigen und Gespräche zu Veranstaltungen verstehen",
                "en": "Understand ads and conversations about events",
                "fa": "فهم آگهی‌ها و گفتگوها درباره رویدادها",
            },
            {
                "de": "Vorschläge für gemeinsame Unternehmungen machen, zustimmen oder ablehnen",
                "en": "Suggest joint activities; agree or decline",
                "fa": "پیشنهاد فعالیت مشترک؛ موافقت یا رد",
            },
            {
                "de": "Theaterstück „Kalt erwischt in Hamburg“ verstehen und zusammenfassen",
                "en": "Understand and summarize the play “Kalt erwischt in Hamburg”",
                "fa": "فهم و خلاصه کردن نمایش «ناگهان در هامبورگ گیر افتادن»",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Adjektive im Genitiv ohne Artikel",
                "Adjectives in genitive without article",
                "Before a noun without article, genitive adjectives take -en (singular): trotz starken Regens, wegen schlechten Wetters, während langen Aufenthalts. Plural also -en: trotz hoher Preise.",
                [
                    "trotz starken Regens",
                    "wegen schlechten Wetters",
                    "während langen Aufenthalts",
                ],
                [
                    {
                        "de": "Trotz kalten Wetters gehen wir in die Stadt.",
                        "en": "Despite cold weather we go into town.",
                        "fa": "با وجود هوای سرد به شهر می‌رویم.",
                    },
                    {
                        "de": "Wegen starken Verkehrs komme ich zu spät.",
                        "en": "Because of heavy traffic I’ll be late.",
                        "fa": "به‌خاطر ترافیک سنگین دیر می‌رسم.",
                    },
                ],
                title_fa="صفات در حالت اضافی بدون حرف تعریف",
            ),
            g(
                "g2",
                "Infinitivsätze; entweder … oder",
                "Infinitive clauses; either … or",
                "Infinitive clauses with zu / um … zu / ohne … zu / statt … zu express purpose, manner, or alternative. entweder … oder presents exclusive alternatives: Entweder gehen wir ins Theater oder wir bleiben zu Hause.",
                [
                    "Es macht Spaß, … zu + Inf.",
                    "um … zu",
                    "entweder … oder",
                ],
                [
                    {
                        "de": "Es ist schön, Hamburg zu entdecken.",
                        "en": "It is nice to discover Hamburg.",
                        "fa": "کشف هامبورگ لذت‌بخش است.",
                    },
                    {
                        "de": "Entweder kaufen wir Karten oder wir schauen online zu.",
                        "en": "Either we buy tickets or we watch online.",
                        "fa": "یا بلیت می‌خریم یا آنلاین تماشا می‌کنیم.",
                    },
                ],
                title_fa="جملات مصدری؛ entweder … oder",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "Genitiv Adj.",
                "Genitive adj.",
                "Trotz ___ Regens bleiben wir draußen.",
                "starken",
                "g1",
                ["starken", "starker", "starkem"],
            ),
            drill(
                "d2",
                "cloze",
                "wegen",
                "wegen",
                "Wegen ___ Wetters fällt das Open-Air aus. (schlecht)",
                "schlechten",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "Infinitiv",
                "Infinitive",
                "Ich habe vor, die Elbphilharmonie ___ .",
                "zu besuchen",
                "g2",
                ["zu besuchen", "besuchen", "zu besucht"],
            ),
            drill(
                "d4",
                "cloze",
                "um … zu",
                "um … zu",
                "Wir fahren in die Stadt, ___ das Theaterstück ___ sehen.",
                "um … zu",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "entweder … oder",
                "either … or",
                "Entweder | gehen | wir | ins | Museum | oder | wir | bleiben | zu | Hause | .",
                "Entweder gehen wir ins Museum oder wir bleiben zu Hause.",
                "g2",
            ),
            drill(
                "d6",
                "multiple-choice",
                "während + Gen.",
                "während + gen.",
                "Während ___ Aufenthalts in Hamburg lerne ich viel.",
                "langen",
                "g1",
                ["langen", "langer", "langem"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Trotz ___ Verkehrs finden wir einen Parkplatz.",
                "starken",
                ["starken", "starker", "starkem"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Wegen ___ Wetters bleiben wir drinnen. (kalt → Gen. ohne Artikel)",
                "kalten",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Es lohnt sich, früh ___ .",
                "anzukommen",
                ["anzukommen", "ankommen", "angekommen"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: ___ gehen wir ins Theater ___ wir hören ein Konzert.",
                "Entweder … oder",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Statt ___ zu bleiben, gehen wir spazieren.",
                "zu Hause",
                ["zu Hause", "im Hause", "dem Hause"],
                "g2",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Ich freue mich darauf, dich ___ . (sehen)",
                "zu sehen",
                grammar_id="g2",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Während ___ Urlaubs besuchen wir Altona.",
                "kurzen",
                ["kurzen", "kurzer", "kurzem"],
                "g1",
            ),
            quiz(
                "q8",
                "grammar-mc",
                "___ kaufen wir Karten jetzt, ___ wir warten bis morgen.",
                "Entweder … oder",
                ["Entweder … oder", "Sowohl … als auch", "Weder … noch"],
                "g2",
            ),
            quiz(
                "q9",
                "cloze",
                "Complete: Ohne ___ zu fragen, buchen sie Tickets. (wir)",
                "uns",
                grammar_id="g2",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Wegen ___ Preises nehmen wir die günstigere Tour.",
                "hohen",
                ["hohen", "hoher", "hohem"],
                "g1",
            ),
        ],
    },
    22: {
        "goals": [
            {
                "de": "Paketschein ausfüllen",
                "en": "Fill in a parcel form",
                "fa": "پر کردن فرم بسته پستی",
            },
            {
                "de": "Gespräch auf der Post verstehen und nachspielen",
                "en": "Understand and role-play a post-office conversation",
                "fa": "فهم و اجرای مکالمه در پست",
            },
            {
                "de": "Sich bei der Post mündlich und schriftlich beschweren",
                "en": "Complain at the post office orally and in writing",
                "fa": "شکایت شفاهی و کتبی در پست",
            },
            {
                "de": "E-Mail lesen und unterscheiden, was Realität oder Möglichkeit ist; Antwort schreiben",
                "en": "Read an email and distinguish reality vs possibility; write a reply",
                "fa": "خواندن ایمیل و تشخیص واقعیت از امکان؛ نوشتن پاسخ",
            },
            {
                "de": "Ratschläge verstehen und geben; Beitrag in einem Internetforum schreiben",
                "en": "Understand and give advice; write a forum post",
                "fa": "فهم و دادن توصیه؛ نوشتن مطلب در انجمن آنلاین",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Indefinitartikel und -pronomen mit irgend-",
                "Indefinite irgend- words",
                "irgend- forms mean “some/any unspecified”: irgendjemand, irgendetwas, irgendwo, irgendwann, irgendwie, irgendein(e). They often appear in questions, offers, and vague statements.",
                [
                    "irgendwo / irgendwann",
                    "irgendetwas / irgendjemand",
                    "irgendein Paket",
                ],
                [
                    {
                        "de": "Hast du irgendwo Briefmarken gesehen?",
                        "en": "Have you seen stamps anywhere?",
                        "fa": "آیا تمبر جایی دیده‌ای؟",
                    },
                    {
                        "de": "Irgendein Kunde hat sich beschwert.",
                        "en": "Some customer complained.",
                        "fa": "یکی از مشتریان شکایت کرده است.",
                    },
                ],
                title_fa="کلمات نامعین با irgend-",
            ),
            g(
                "g2",
                "Konjunktiv II; irreale Konditionalsätze",
                "Subjunctive II; unreal conditionals",
                "Konjunktiv II (würde + Inf. / wäre, hätte, könnte, müsste…): polite or unreal. Irreal conditionals: Wenn ich Zeit hätte, würde ich … / Hätte ich Zeit, würde ich … (without wenn, verb first).",
                [
                    "Wenn ich … hätte, würde ich …",
                    "Hätte ich … , würde ich …",
                    "Ich würde …",
                ],
                [
                    {
                        "de": "Wenn das Paket früher ankäme, wäre ich froh.",
                        "en": "If the parcel arrived earlier, I would be glad.",
                        "fa": "اگر بسته زودتر می‌رسید، خوشحال می‌شدم.",
                    },
                    {
                        "de": "Hätte ich die Adresse richtig geschrieben, wäre der Brief angekommen.",
                        "en": "Had I written the address correctly, the letter would have arrived.",
                        "fa": "اگر آدرس را درست نوشته بودم، نامه می‌رسید.",
                    },
                ],
                title_fa="وجه التزامی دوم؛ شرطی غیرواقعی",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "irgendwo",
                "irgendwo",
                "Ich habe die Quittung ___ gelassen.",
                "irgendwo",
                "g1",
                ["irgendwo", "nirgendswo", "überallwo"],
            ),
            drill(
                "d2",
                "cloze",
                "irgend-",
                "irgend-",
                "___ hat an der Tür geklingelt. (jemand unbestimmt)",
                "Irgendjemand",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "Konj. II",
                "Subj. II",
                "Ich ___ gerne ein Päckchen schicken.",
                "würde",
                "g2",
                ["würde", "werde", "wurde"],
            ),
            drill(
                "d4",
                "cloze",
                "Konditional",
                "Conditional",
                "Wenn ich mehr Geld ___, würde ich Expressporto nehmen. (haben)",
                "hätte",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "ohne wenn",
                "without wenn",
                "Hätte | ich | Zeit | , | würde | ich | zur | Post | gehen | .",
                "Hätte ich Zeit, würde ich zur Post gehen.",
                "g2",
            ),
            drill(
                "d6",
                "multiple-choice",
                "irgendein",
                "irgendein",
                "___ Formular reicht für den Versand.",
                "Irgendein",
                "g1",
                ["Irgendein", "Irgendeine", "Irgendwas"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Kannst du ___ helfen?",
                "irgendwie",
                ["irgendwie", "nirgendwo", "irgendwann"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Ruf mich ___ an, wenn du Zeit hast. (zu irgendeiner Zeit)",
                "irgendwann",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Wenn die Adresse falsch ___, käme das Paket nicht an.",
                "wäre",
                ["wäre", "ist", "war"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Ich ___ dir raten, eine Sendungsnummer zu verlangen. (können → Konj. II)",
                "könnte",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "___ ich früher gekommen, hätte ich die Schlange vermieden.",
                "Wäre",
                ["Wäre", "War", "Bin"],
                "g2",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Hast du ___ gehört? (etwas Unbestimmtes)",
                "irgendetwas",
                grammar_id="g1",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Wenn wir Expressporto nähmen, ___ das Paket schneller an.",
                "käme",
                ["käme", "kommt", "kam"],
                "g2",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: ___ Kunde hat die falsche Adresse angegeben.",
                "Irgendein",
                grammar_id="g1",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Ich ___ an Ihrer Stelle eine Beschwerde schreiben.",
                "würde",
                ["würde", "werde", "will"],
                "g2",
            ),
            quiz(
                "q10",
                "cloze",
                "Complete: Wenn das Päckchen nicht ankäme, ___ ich mich beschweren. (werden)",
                "würde",
                grammar_id="g2",
            ),
        ],
    },
    23: {
        "goals": [
            {
                "de": "Notizen zu Informationstexten und einem Vortrag über das Hochschulsystem machen",
                "en": "Take notes on texts and a talk about the higher-education system",
                "fa": "یادداشت از متون و سخنرانی درباره نظام دانشگاهی",
            },
            {
                "de": "Einen Hochschultyp im Heimatland beschreiben",
                "en": "Describe a type of higher education in your home country",
                "fa": "توصیف یک نوع مؤسسه آموزش عالی در کشور خود",
            },
            {
                "de": "Wichtige persönliche Entscheidungen begründen",
                "en": "Give reasons for important personal decisions",
                "fa": "دلیل‌آوردن برای تصمیم‌های شخصی مهم",
            },
            {
                "de": "In einer E-Mail Ratschlag für den passenden Hochschultyp geben",
                "en": "Advise on a suitable type of university in an email",
                "fa": "توصیه نوع مناسب دانشگاه در ایمیل",
            },
            {
                "de": "Ungewöhnliche Biografien verstehen; Kurzbiografie schreiben und vorstellen",
                "en": "Understand unusual biographies; write and present a short bio",
                "fa": "فهم زندگی‌نامه‌های غیرمعمول؛ نوشتن و ارائه بیوگرافی کوتاه",
            },
        ],
        "grammar": [
            g(
                "g1",
                "wegen / nämlich; obwohl / trotzdem / zwar … aber",
                "wegen / nämlich; although / still / admittedly … but",
                "wegen + Genitiv (wegen des Studiums); nämlich adds an explanation in a main clause. Concessive: obwohl + Nebensatz; trotzdem / dennoch in main clause; zwar … aber balances contrast.",
                [
                    "wegen des … / nämlich …",
                    "obwohl … , …",
                    "zwar … , aber …",
                ],
                [
                    {
                        "de": "Ich bleibe hier wegen des Studiums. Die Uni ist nämlich sehr gut.",
                        "en": "I stay here because of my studies. The uni is namely very good.",
                        "fa": "به‌خاطر تحصیل اینجا می‌مانم. دانشگاه واقعاً خیلی خوب است.",
                    },
                    {
                        "de": "Obwohl das Studium schwer ist, mache ich weiter.",
                        "en": "Although studying is hard, I continue.",
                        "fa": "اگرچه تحصیل سخت است، ادامه می‌دهم.",
                    },
                    {
                        "de": "Zwar ist die Miete hoch, aber die Stadt gefällt mir.",
                        "en": "The rent is high, but I like the city.",
                        "fa": "اجاره بالاست، اما شهر را دوست دارم.",
                    },
                ],
                title_fa="wegen/nämlich؛ اگرچه/بااین‌حال/zwar…aber",
            ),
            g(
                "g2",
                "Konjunktiv II: irreale Wunschsätze",
                "Subjunctive II: unreal wishes",
                "Wishes contrary to reality: Wenn ich doch … hätte! / Hätte ich nur … ! / Ich wünschte, ich wäre … Particles doch / nur / bloß intensify the wish.",
                [
                    "Wenn ich doch … !",
                    "Hätte ich nur … !",
                    "Ich wünschte, …",
                ],
                [
                    {
                        "de": "Wenn ich doch mehr Zeit zum Lernen hätte!",
                        "en": "If only I had more time to study!",
                        "fa": "کاش وقت بیشتری برای درس خواندن داشتم!",
                    },
                    {
                        "de": "Wäre ich nur schon im Examen fertig!",
                        "en": "If only I had already finished the exam!",
                        "fa": "کاش امتحان را تمام کرده بودم!",
                    },
                ],
                title_fa="وجه التزامی دوم: جملات آرزو",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "wegen",
                "wegen",
                "Sie wechselt die Uni ___ der besseren Betreuung.",
                "wegen",
                "g1",
                ["wegen", "obwohl", "trotzdem"],
            ),
            drill(
                "d2",
                "cloze",
                "nämlich",
                "nämlich",
                "Ich bleibe hier. Die Bibliothek ist ___ hervorragend.",
                "nämlich",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "obwohl",
                "obwohl",
                "___ er wenig Geld hat, studiert er in einer Großstadt.",
                "Obwohl",
                "g1",
                ["Obwohl", "Wegen", "Nämlich"],
            ),
            drill(
                "d4",
                "cloze",
                "Wunsch",
                "wish",
                "Wenn ich ___ ein Stipendium hätte! (Verstärkung)",
                "doch",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "zwar … aber",
                "zwar … aber",
                "Zwar | ist | das | Studium | anstrengend | , | aber | es | macht | Spaß | .",
                "Zwar ist das Studium anstrengend, aber es macht Spaß.",
                "g1",
            ),
            drill(
                "d6",
                "multiple-choice",
                "Wunschsatz",
                "wish clause",
                "___ ich nur früher angefangen!",
                "Hätte",
                "g2",
                ["Hätte", "Habe", "Hatte"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Er studiert Medizin ___ seines Interesses an Menschen.",
                "wegen",
                ["wegen", "obwohl", "trotzdem"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Ich brauche Ruhe. Morgen ist ___ die Prüfung.",
                "nämlich",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "___ das Wohnheim teuer ist, bleibe ich dort.",
                "Obwohl",
                ["Obwohl", "Wegen", "Zwar"],
                "g1",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Es regnet stark. ___ gehe ich zur Vorlesung.",
                "Trotzdem",
                grammar_id="g1",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Wenn ich ___ schon eingeschrieben wäre!",
                "doch",
                ["doch", "also", "nämlich"],
                "g2",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: ___ ich nur bessere Noten!",
                "Hätte",
                grammar_id="g2",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Zwar ist die Uni weit, ___ die Atmosphäre ist super.",
                "aber",
                ["aber", "obwohl", "wegen"],
                "g1",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: Ich wünschte, ich ___ mehr Geld. (haben → Konj. II)",
                "hätte",
                grammar_id="g2",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Wäre das Semester ___ schon vorbei!",
                "nur",
                ["nur", "also", "wegen"],
                "g2",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Sie bleibt ___ der hohen Kosten in der WG.",
                "trotz",
                ["trotz", "wegen", "nämlich"],
                "g1",
            ),
        ],
    },
    24: {
        "goals": [
            {
                "de": "Anhand von Informationstexten und Anzeigen herausfinden, was zu einer Person passt",
                "en": "Use info texts and ads to find what suits a person",
                "fa": "با متون و آگهی‌ها بفهمید چه چیزی به فرد می‌خورد",
            },
            {
                "de": "E-Mail mit Bitten um Informationen schreiben",
                "en": "Write an email requesting information",
                "fa": "نوشتن ایمیل برای درخواست اطلاعات",
            },
            {
                "de": "Bewerbungsmail verstehen und selbst schreiben",
                "en": "Understand and write an application email",
                "fa": "فهم و نوشتن ایمیل درخواست کار/داوطلبی",
            },
            {
                "de": "Notizen zu einer Präsentation über Freiwilligeneinsatz machen",
                "en": "Take notes on a presentation about volunteering",
                "fa": "یادداشت از ارائه درباره کار داوطلبانه",
            },
            {
                "de": "Von einem Freiwilligeneinsatz oder Arbeitserfahrungen schriftlich berichten",
                "en": "Write about volunteering or work experience",
                "fa": "گزارش کتبی از کار داوطلبانه یا تجربه کاری",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Finalsätze: damit / um … zu",
                "Purpose clauses: damit / um … zu",
                "Same subject → um … zu + Infinitiv: Ich spare, um zu reisen. Different subjects → damit + Nebensatz: Ich erkläre es langsam, damit du es verstehst. Also zum/zur + Nomen: zum Lernen.",
                [
                    "um … zu + Inf.",
                    "damit + Nebensatz",
                    "zum / zur + Nomen",
                ],
                [
                    {
                        "de": "Ich melde mich an, um auf dem Biohof zu arbeiten.",
                        "en": "I sign up in order to work on the organic farm.",
                        "fa": "ثبت‌نام می‌کنم تا در مزرعه ارگانیک کار کنم.",
                    },
                    {
                        "de": "Wir erklären alles, damit die Freiwilligen sich zurechtfinden.",
                        "en": "We explain everything so that the volunteers can find their way.",
                        "fa": "همه‌چیز را توضیح می‌دهیم تا داوطلبان راه بیفتند.",
                    },
                ],
                title_fa="جملات هدف: damit / um … zu",
            ),
            g(
                "g2",
                "wo(r)- / da(r)- Pronomen; Partizip Präsens als Adjektiv",
                "wo(r)- / da(r)- pronouns; present participle as adjective",
                "Questions: Worauf wartest du? Womit arbeitest du? Statements: Ich warte darauf. Ich arbeite damit. Partizip I as adjective: die arbeitenden Studenten, das fließende Wasser (often -d + ending).",
                [
                    "Worauf … ? / darauf",
                    "Womit … ? / damit",
                    "die lachenden Kinder",
                ],
                [
                    {
                        "de": "Worauf freust du dich? — Ich freue mich darauf, auf der Alp zu sein.",
                        "en": "What are you looking forward to? — I’m looking forward to being on the alp.",
                        "fa": "به چه چیزی خوشحال می‌شوی؟ — به بودن روی آلپ.",
                    },
                    {
                        "de": "Die blühenden Wiesen sind im Sommer wunderschön.",
                        "en": "The blooming meadows are beautiful in summer.",
                        "fa": "چمنزارهای گل‌دار در تابستان زیبا هستند.",
                    },
                ],
                title_fa="ضمایر wo(r)-/da(r)-؛ اسم فاعل به‌عنوان صفت",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "um … zu",
                "um … zu",
                "Sie lernt Deutsch, ___ später in der Schweiz zu arbeiten.",
                "um",
                "g1",
                ["um", "damit", "weil"],
            ),
            drill(
                "d2",
                "cloze",
                "damit",
                "damit",
                "Ich schreibe langsam, ___ du alles verstehst.",
                "damit",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "worauf",
                "worauf",
                "___ wartest du?",
                "Worauf",
                "g2",
                ["Worauf", "Darauf", "Wofür"],
            ),
            drill(
                "d4",
                "cloze",
                "darauf",
                "darauf",
                "Ich freue mich ___, Natur zu erleben.",
                "darauf",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "Finalsatz",
                "Purpose",
                "Er | spart | Geld | , | um | später | zu | reisen | .",
                "Er spart Geld, um später zu reisen.",
                "g1",
            ),
            drill(
                "d6",
                "multiple-choice",
                "Partizip I",
                "Pres. participle",
                "Die ___ Kühe stehen auf der Weide.",
                "grasenden",
                "g2",
                ["grasenden", "gegrasten", "grasen"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Ich fahre auf die Alp, ___ dort zu helfen.",
                "um",
                ["um", "damit", "weil"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Er spricht laut, ___ alle ihn hören.",
                "damit",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "___ interessierst du dich?",
                "Wofür",
                ["Wofür", "Dafür", "Womit"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Ich träume ___ , auf einem Biohof zu leben.",
                "davon",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Wir treffen uns zum ___ .",
                "Arbeiten",
                ["Arbeiten", "arbeiten zu", "Arbeitens"],
                "g1",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: ___ arbeitest du auf dem Hof? — Mit den Tieren.",
                "Womit",
                grammar_id="g2",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Die ___ Sonne wärmt uns.",
                "scheinende",
                ["scheinende", "geschienene", "scheinen"],
                "g2",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: Sie lernt viel, ___ die Prüfung zu bestehen.",
                "um",
                grammar_id="g1",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Ich denke oft ___ .",
                "daran",
                ["daran", "woran", "daran zu"],
                "g2",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Same subject → prefer:",
                "um … zu",
                ["um … zu", "damit", "weil"],
                "g1",
            ),
        ],
    },
    25: {
        "goals": [
            {
                "de": "Sich über Begrüßungsformen in unterschiedlichen Ländern austauschen",
                "en": "Exchange ideas about greeting customs in different countries",
                "fa": "گفتگو درباره آداب سلام در کشورهای مختلف",
            },
            {
                "de": "Anhand von Informationstexten Fragen zu Small Talk, Duzen/Siezen, Anrede und Schreibstil beantworten",
                "en": "Answer questions on small talk, du/Sie, address forms and writing style from info texts",
                "fa": "پاسخ به پرسش‌ها درباره اسمال‌تاک، تو/شما، خطاب و سبک نوشتار",
            },
            {
                "de": "Small Talk in deutschsprachigen Ländern mit der Heimat vergleichen und einen Beispieldialog schreiben",
                "en": "Compare small talk with your country and write a sample dialogue",
                "fa": "مقایسه اسمال‌تاک با کشور خود و نوشتن دیالوگ نمونه",
            },
            {
                "de": "Text über Fehler verstehen; sich über den Umgang mit Fehlern in der Fremdsprache austauschen",
                "en": "Understand a text about mistakes; discuss dealing with errors in a foreign language",
                "fa": "فهم متن درباره اشتباه؛ گفتگو درباره برخورد با خطا در زبان خارجی",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Reziproke Reflexivpronomen",
                "Reciprocal reflexive pronouns",
                "sich (einander) expresses mutual action: Sie grüßen sich. Wir verstehen uns gut. Optional einander for clarity: Sie helfen einander. Verb often reflexive: sich kennenlernen, sich streiten.",
                [
                    "Sie grüßen sich.",
                    "Wir verstehen uns.",
                    "Sie helfen einander.",
                ],
                [
                    {
                        "de": "In Deutschland siezen sich Kollegen oft lange.",
                        "en": "In Germany colleagues often use Sie with each other for a long time.",
                        "fa": "در آلمان همکاران اغلب مدت‌ها به هم «شما» می‌گویند.",
                    },
                    {
                        "de": "Die beiden Studenten helfen sich beim Lernen.",
                        "en": "The two students help each other with studying.",
                        "fa": "آن دو دانشجو هنگام درس به هم کمک می‌کنند.",
                    },
                ],
                title_fa="ضمایر بازتابی متقابل",
            ),
            g(
                "g2",
                "Konsekutive Sätze: also / sodass / so … dass",
                "Consecutive clauses: so / so that / so … that",
                "also / folglich connect result in a main clause. sodass / so dass introduce a result subordinate clause. so + Adj./Adv. … dass intensifies: Er war so nervös, dass er stockte.",
                [
                    "… , also …",
                    "… , sodass …",
                    "so … , dass …",
                ],
                [
                    {
                        "de": "Ich habe den Namen falsch geschrieben, also musste ich mich entschuldigen.",
                        "en": "I wrote the name wrong, so I had to apologize.",
                        "fa": "اسم را اشتباه نوشتم، بنابراین باید عذرخواهی می‌کردم.",
                    },
                    {
                        "de": "Er sprach so leise, dass niemand ihn verstand.",
                        "en": "He spoke so quietly that nobody understood him.",
                        "fa": "آن‌قدر آهسته حرف زد که کسی او را نفهمید.",
                    },
                ],
                title_fa="جملات نتیجه‌ای: also / sodass / so … dass",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "reziprok",
                "reciprocal",
                "Die Nachbarn grüßen ___ jeden Morgen.",
                "sich",
                "g1",
                ["sich", "ihn", "euch"],
            ),
            drill(
                "d2",
                "cloze",
                "uns",
                "uns",
                "Wir verstehen ___ sehr gut.",
                "uns",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "also",
                "so/therefore",
                "Du hast dich vertippt, ___ schreib die E-Mail noch einmal.",
                "also",
                "g2",
                ["also", "obwohl", "damit"],
            ),
            drill(
                "d4",
                "cloze",
                "sodass",
                "so that",
                "Sie übt jeden Tag, ___ sie weniger Fehler macht.",
                "sodass",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "so … dass",
                "so … that",
                "Er | war | so | aufgeregt | , | dass | er | stockte | .",
                "Er war so aufgeregt, dass er stockte.",
                "g2",
            ),
            drill(
                "d6",
                "multiple-choice",
                "einander",
                "each other",
                "Die Gäste stellen ___ vor.",
                "sich / einander",
                "g1",
                ["sich / einander", "ihn", "jemanden"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "In vielen Ländern umarmen ___ Freunde zur Begrüßung.",
                "sich",
                ["sich", "ihn", "man"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Kennt ihr ___ schon lange?",
                "euch",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Ich habe „Sie“ gesagt, ___ habe ich formal begrüßt.",
                "also",
                ["also", "obwohl", "damit"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Sie war ___ unsicher, ___ sie nichts sagte.",
                "so … dass",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Wir schreiben ___ regelmäßig E-Mails.",
                "uns",
                ["uns", "wir", "unser"],
                "g1",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Er hat viele Fehler gemacht, ___ muss er den Text korrigieren.",
                "also",
                grammar_id="g2",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Sie streiten ___, aber versöhnen ___ schnell.",
                "sich … sich",
                ["sich … sich", "ihn … ihn", "man … man"],
                "g1",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: Er spricht undeutlich, ___ man ihn schlecht versteht.",
                "sodass",
                grammar_id="g2",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Das Gespräch war ___ peinlich, ___ niemand weiterredete.",
                "so … dass",
                ["so … dass", "um … zu", "entweder … oder"],
                "g2",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Die Kollegen duzen ___ seit dem ersten Tag.",
                "sich",
                ["sich", "ihn", "euch"],
                "g1",
            ),
        ],
    },
    26: {
        "goals": [
            {
                "de": "E-Mail über die neue Umgebung verstehen",
                "en": "Understand an email about a new environment",
                "fa": "فهم ایمیل درباره محیط جدید",
            },
            {
                "de": "Arbeitsvertrag verstehen und ergänzen; über Arbeitsverträge in der Heimat sprechen",
                "en": "Understand and complete a work contract; talk about contracts at home",
                "fa": "فهم و تکمیل قرارداد کار؛ صحبت درباره قرارداد در کشور خود",
            },
            {
                "de": "Ausführlich über sich Auskunft geben (erster Arbeitstag)",
                "en": "Give detailed information about yourself (first day at work)",
                "fa": "ارائه اطلاعات مفصل درباره خود (روز اول کار)",
            },
            {
                "de": "Kleinanzeigen verstehen und selbst schreiben",
                "en": "Understand and write classified ads",
                "fa": "فهم و نوشتن آگهی‌های کوتاه",
            },
            {
                "de": "Zeitungsartikel über den Standort Dresden zusammenfassen; Text über Zukunftsträume schreiben",
                "en": "Summarize an article on Dresden as a business location; write about future dreams",
                "fa": "خلاصه مقاله درباره درسدن؛ نوشتن درباره رویاهای آینده",
            },
        ],
        "grammar": [
            g(
                "g1",
                "lassen + Verb",
                "lassen + verb",
                "(sich) lassen + Infinitiv: cause/allow something to be done — Ich lasse mein Auto reparieren. Reflexive: Das lässt sich ändern (can be changed). Perfekt: hat … lassen (double infinitive at end): Ich habe mir die Haare schneiden lassen.",
                [
                    "lassen + Inf.",
                    "sich lassen + Inf.",
                    "hat … Inf. lassen",
                ],
                [
                    {
                        "de": "Ich lasse mir den Vertrag erklären.",
                        "en": "I have the contract explained to me.",
                        "fa": "قرارداد را برایم توضیح می‌دهند (می‌گذارم توضیح دهند).",
                    },
                    {
                        "de": "Das Problem hat sich lösen lassen.",
                        "en": "The problem could be solved.",
                        "fa": "مشکل قابل حل بوده است.",
                    },
                ],
                title_fa="lassen + فعل",
            ),
            g(
                "g2",
                "Modalverben im Perfekt",
                "Modal verbs in the perfect",
                "With a second verb: double infinitive — hat … arbeiten müssen / können / wollen / sollen / dürfen / mögen. Without second verb: normal Partizip — hat gemusst. Word order: … hat nach Dresden fahren müssen.",
                [
                    "hat … Inf. müssen",
                    "hat … Inf. können",
                    "hat gemusst (ohne 2. Verb)",
                ],
                [
                    {
                        "de": "Am ersten Tag habe ich früh aufstehen müssen.",
                        "en": "On the first day I had to get up early.",
                        "fa": "روز اول مجبور بودم زود بیدار شوم.",
                    },
                    {
                        "de": "Sie hat die Stelle bekommen wollen.",
                        "en": "She wanted to get the job.",
                        "fa": "او می‌خواست آن شغل را بگیرد.",
                    },
                ],
                title_fa="افعال وجهی در Perfekt",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "lassen",
                "lassen",
                "Ich ___ mir die Schlüsselkopie machen.",
                "lasse",
                "g1",
                ["lasse", "lasse zu", "lasse mich"],
            ),
            drill(
                "d2",
                "cloze",
                "Perfekt lassen",
                "lassen perfect",
                "Ich habe die Wohnung renovieren ___.",
                "lassen",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "Modal Perfekt",
                "Modal perfect",
                "Er hat länger bleiben ___.",
                "müssen",
                "g2",
                ["müssen", "gemusst", "musste"],
            ),
            drill(
                "d4",
                "cloze",
                "können Perfekt",
                "können perfect",
                "Wir haben den Vertrag nicht ändern ___.",
                "können",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "Doppelinfinitiv",
                "Double infinitive",
                "Sie | hat | nach | Dresden | ziehen | wollen | .",
                "Sie hat nach Dresden ziehen wollen.",
                "g2",
            ),
            drill(
                "d6",
                "multiple-choice",
                "sich lassen",
                "sich lassen",
                "Der Fehler ___ sich leicht korrigieren.",
                "lässt",
                "g1",
                ["lässt", "lässt zu", "hat lassen"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Kannst du dir die Adresse ___ ?",
                "geben lassen",
                ["geben lassen", "lassen geben", "gegeben lassen"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Ich habe mein Büro streichen ___.",
                "lassen",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Am Montag habe ich Überstunden machen ___.",
                "müssen",
                ["müssen", "gemusst", "musste"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Sie hat nicht länger bleiben ___.",
                "dürfen",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Das lässt ___ nicht ändern.",
                "sich",
                ["sich", "ihn", "man"],
                "g1",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Er hat die Firma wechseln ___.",
                "wollen",
                grammar_id="g2",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Ohne zweites Verb: Ich habe das leider ___.",
                "gemusst",
                ["gemusst", "müssen", "musste"],
                "g2",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: Wir ___ uns beraten. (Präsens lassen)",
                "lassen",
                grammar_id="g1",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Ich habe mir einen Termin ___ .",
                "geben lassen",
                ["geben lassen", "gelassen geben", "geben gelassen"],
                "g1",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Sie hat früher kommen ___.",
                "sollen",
                ["sollen", "gesollt", "sollte"],
                "g2",
            ),
        ],
    },
    27: {
        "goals": [
            {
                "de": "Tour durch Berlin nachverfolgen",
                "en": "Follow a tour through Berlin",
                "fa": "دنبال کردن تور در برلین",
            },
            {
                "de": "Erraten, wann jemand was gemacht hat",
                "en": "Guess when someone did what",
                "fa": "حدس زدن که کسی چه زمانی چه کاری کرده",
            },
            {
                "de": "Text über die Geschichte Berlins erfassen; Geschichte der Heimatstadt vorstellen",
                "en": "Grasp a text on Berlin’s history; present your hometown’s history",
                "fa": "درک متن تاریخ برلین؛ معرفی تاریخ شهر خود",
            },
            {
                "de": "Sich über ein Thema anhand von Fotos austauschen",
                "en": "Discuss a topic using photos",
                "fa": "گفتگو درباره یک موضوع با کمک عکس‌ها",
            },
            {
                "de": "Erzählung verstehen; eigene Geschichte und Texte über Lieblingsorte verfassen",
                "en": "Understand a story; write your own story and texts about favorite places",
                "fa": "فهم داستان؛ نوشتن داستان خود و متن درباره مکان‌های محبوب",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Plusquamperfekt Aktiv und Passiv",
                "Past perfect active and passive",
                "Active: hatte/war + Partizip II — After something earlier in the past. Passive: war/waren + Partizip II + worden — Die Mauer war 1961 gebaut worden (context of later past narration).",
                [
                    "hatte … gemacht",
                    "war … geworden / gegangen",
                    "war … worden (Passiv)",
                ],
                [
                    {
                        "de": "Nachdem er angekommen war, besuchte er das Brandenburger Tor.",
                        "en": "After he had arrived, he visited the Brandenburg Gate.",
                        "fa": "بعد از آنکه رسیده بود، از دروازه براندنبورگ دیدن کرد.",
                    },
                    {
                        "de": "Die Mauer war schon gefallen, bevor ich Berlin sah.",
                        "en": "The Wall had already fallen before I saw Berlin.",
                        "fa": "دیوار قبلاً فروریخته بود، قبل از آنکه برلین را ببینم.",
                    },
                ],
                title_fa="ماضی بعید فعال و مجهول",
            ),
            g(
                "g2",
                "nachdem / bevor / während",
                "after / before / while",
                "nachdem + Plusquamperfekt (earlier action) → main clause Perfekt/Präteritum. bevor + Präsens/Präteritum for later action. während for simultaneous actions (Gleichzeitigkeit).",
                [
                    "Nachdem … Plq., …",
                    "Bevor … , …",
                    "Während … , …",
                ],
                [
                    {
                        "de": "Nachdem wir das Museum besichtigt hatten, gingen wir essen.",
                        "en": "After we had visited the museum, we went to eat.",
                        "fa": "بعد از آنکه موزه را دیده بودیم، رفتیم غذا بخوریم.",
                    },
                    {
                        "de": "Bevor die Führung begann, kauften wir Tickets.",
                        "en": "Before the tour began, we bought tickets.",
                        "fa": "قبل از شروع تور، بلیت خریدیم.",
                    },
                    {
                        "de": "Während er fotografierte, erzählte die Guide die Geschichte.",
                        "en": "While he was taking photos, the guide told the story.",
                        "fa": "در حالی که عکس می‌گرفت، راهنما تاریخ را تعریف می‌کرد.",
                    },
                ],
                title_fa="nachdem / bevor / während",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "Plusquamperfekt",
                "Past perfect",
                "Er ___ die Ausstellung schon gesehen, bevor wir kamen.",
                "hatte",
                "g1",
                ["hatte", "hat", "hatte gewesen"],
            ),
            drill(
                "d2",
                "cloze",
                "Passiv Plq.",
                "Passive plq.",
                "Das Denkmal ___ 1989 eingeweiht worden.",
                "war",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "nachdem",
                "after",
                "___ wir angekommen waren, begann die Tour.",
                "Nachdem",
                "g2",
                ["Nachdem", "Bevor", "Während"],
            ),
            drill(
                "d4",
                "cloze",
                "bevor",
                "before",
                "___ du gehst, schau noch die East Side Gallery an.",
                "Bevor",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "während",
                "while",
                "Während | sie | erzählte | , | machten | wir | Notizen | .",
                "Während sie erzählte, machten wir Notizen.",
                "g2",
            ),
            drill(
                "d6",
                "multiple-choice",
                "Plq. Verb",
                "Plq. verb",
                "Sie ___ schon nach Berlin gezogen, als ich sie traf.",
                "war",
                "g1",
                ["war", "ist", "wurde"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Nachdem er die Geschichte ___ , stellte er Fragen. (lesen)",
                "gelesen hatte",
                ["gelesen hatte", "gelesen hat", "lesen hatte"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Die Brücke ___ schon gebaut worden, bevor der Krieg endete.",
                "war",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "___ wir fotografierten, erklärte der Guide die Fassade.",
                "Während",
                ["Während", "Nachdem", "Bevor"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: ___ die Nacht kam, war die Stadt noch hell.",
                "Bevor",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Sie ___ den Roman schon gelesen, als der Film startete.",
                "hatte",
                ["hatte", "hat", "war"],
                "g1",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Nachdem wir gegessen ___ , gingen wir weiter.",
                "hatten",
                grammar_id="g2",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Das Museum ___ renoviert worden, bevor es wieder öffnete.",
                "war",
                ["war", "wurde", "ist"],
                "g1",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: ___ er erzählte, hörten alle zu.",
                "Während",
                grammar_id="g2",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Vorzeitigkeit → typischerweise:",
                "nachdem + Plusquamperfekt",
                [
                    "nachdem + Plusquamperfekt",
                    "bevor + Plusquamperfekt",
                    "während + Futur",
                ],
                "g2",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Er ___ bereits weggegangen, als wir ankamen.",
                "war",
                ["war", "ist", "hatte gewesen"],
                "g1",
            ),
        ],
    },
    28: {
        "goals": [
            {
                "de": "Sich über Auswanderungsgründe austauschen",
                "en": "Exchange reasons for emigrating",
                "fa": "گفتگو درباره دلایل مهاجرت",
            },
            {
                "de": "Über ein Balkendiagramm sprechen",
                "en": "Talk about a bar chart",
                "fa": "صحبت درباره نمودار میله‌ای",
            },
            {
                "de": "Beim Beratungsangebot Informationen einholen und die Antwort verstehen",
                "en": "Obtain information from an advice service and understand the reply",
                "fa": "گرفتن اطلاعات از مرکز مشاوره و فهم پاسخ",
            },
            {
                "de": "Reiseführertexte verstehen; Zukunftspläne und Träume vorstellen",
                "en": "Understand guidebook texts; present future plans and dreams",
                "fa": "فهم متون راهنما؛ معرفی برنامه‌ها و رویاهای آینده",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Futur I; brauchen … nur zu",
                "Future I; need only to",
                "Futur I: werden + Infinitiv for future or prediction: Ich werde auswandern. brauchen + nur/bloß + zu + Inf. = only need to: Du brauchst nur anzurufen.",
                [
                    "werde / wirst / wird + Inf.",
                    "brauchen nur zu + Inf.",
                ],
                [
                    {
                        "de": "Nächstes Jahr werde ich in Innsbruck leben.",
                        "en": "Next year I will live in Innsbruck.",
                        "fa": "سال آینده در اینسبروک زندگی خواهم کرد.",
                    },
                    {
                        "de": "Du brauchst nur das Formular auszufüllen.",
                        "en": "You only need to fill in the form.",
                        "fa": "فقط کافی است فرم را پر کنی.",
                    },
                ],
                title_fa="آینده ساده؛ brauchen … nur zu",
            ),
            g(
                "g2",
                "sowohl … als auch / weder … noch / nicht nur … sondern auch",
                "both … and / neither … nor / not only … but also",
                "Two-part connectors: sowohl A als auch B; weder A noch B; nicht nur A, sondern auch B. They link equal elements (nouns, verbs, clauses).",
                [
                    "sowohl … als auch",
                    "weder … noch",
                    "nicht nur … , sondern auch",
                ],
                [
                    {
                        "de": "Er spricht sowohl Deutsch als auch Englisch.",
                        "en": "He speaks both German and English.",
                        "fa": "او هم آلمانی و هم انگلیسی حرف می‌زند.",
                    },
                    {
                        "de": "Ich habe weder Angst noch Zweifel.",
                        "en": "I have neither fear nor doubt.",
                        "fa": "نه ترس دارم و نه تردید.",
                    },
                    {
                        "de": "Sie will nicht nur arbeiten, sondern auch studieren.",
                        "en": "She wants not only to work but also to study.",
                        "fa": "او نه فقط می‌خواهد کار کند، بلکه درس هم بخواند.",
                    },
                ],
                title_fa="هم…هم / نه…نه / نه فقط…بلکه",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "Futur",
                "Future",
                "Ich ___ bald umziehen.",
                "werde",
                "g1",
                ["werde", "würde", "bin"],
            ),
            drill(
                "d2",
                "cloze",
                "brauchen nur",
                "need only",
                "Du brauchst ___ das Formular auszufüllen.",
                "nur",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "sowohl",
                "both … and",
                "Sie kennt ___ Innsbruck ___ Wien.",
                "sowohl … als auch",
                "g2",
                ["sowohl … als auch", "weder … noch", "entweder … oder"],
            ),
            drill(
                "d4",
                "cloze",
                "weder … noch",
                "neither … nor",
                "Er hat ___ Job ___ Wohnung gefunden.",
                "weder … noch",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "nicht nur",
                "not only",
                "Sie | will | nicht | nur | arbeiten | , | sondern | auch | lernen | .",
                "Sie will nicht nur arbeiten, sondern auch lernen.",
                "g2",
            ),
            drill(
                "d6",
                "multiple-choice",
                "brauchen zu",
                "brauchen zu",
                "Ihr braucht nicht ___ zu kommen.",
                "früh",
                "g1",
                ["früh", "frühen", "früheren"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Wir ___ nächstes Jahr auswandern.",
                "werden",
                ["werden", "würden", "sind"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Du brauchst nur die Website ___ . (besuchen)",
                "zu besuchen",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Er spricht ___ Deutsch ___ Italienisch.",
                "sowohl … als auch",
                ["sowohl … als auch", "weder … noch", "je … desto"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Ich habe ___ Zeit ___ Geld.",
                "weder … noch",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Sie will ___ informieren, ___ entscheiden.",
                "nicht nur … sondern auch",
                [
                    "nicht nur … sondern auch",
                    "entweder … oder",
                    "um … zu",
                ],
                "g2",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Es ___ bestimmt besser werden. (Futur)",
                "wird",
                grammar_id="g1",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Man braucht ___ den Pass zu zeigen.",
                "nur",
                ["nur", "nicht", "schon"],
                "g1",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: ___ die Sprache ___ die Kultur interessieren ihn.",
                "Sowohl … als auch",
                grammar_id="g2",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Futur I besteht aus:",
                "werden + Infinitiv",
                ["werden + Infinitiv", "haben + Infinitiv", "sein + worden"],
                "g1",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "___ Regen ___ Schnee hält sie zurück.",
                "Weder … noch",
                ["Weder … noch", "Sowohl … als auch", "Je … desto"],
                "g2",
            ),
        ],
    },
    29: {
        "goals": [
            {
                "de": "Lexikon- und Fachartikel zum politischen System in Deutschland verstehen",
                "en": "Understand encyclopedia and specialist articles on Germany’s political system",
                "fa": "فهم مقالات دانشنامه‌ای درباره نظام سیاسی آلمان",
            },
            {
                "de": "Handout über das politische System im Heimatland erstellen und Referat halten",
                "en": "Create a handout on your country’s political system and give a talk",
                "fa": "تهیه جزوه درباره نظام سیاسی کشور خود و ارائه سخنرانی",
            },
            {
                "de": "Informationstexte zu Bundestagswahlen verstehen",
                "en": "Understand information texts on federal elections",
                "fa": "فهم متون اطلاعاتی درباره انتخابات بوندستاگ",
            },
            {
                "de": "Verstehen, warum jemand eine bestimmte Partei wählt; Wahlsystem der Heimat vorstellen",
                "en": "Understand why someone votes for a party; present your country’s voting system",
                "fa": "فهم دلیل رأی به یک حزب؛ معرفی نظام انتخاباتی کشور خود",
            },
        ],
        "grammar": [
            g(
                "g1",
                "je … desto / umso",
                "the … the (je … desto/umso)",
                "je + Komparativ … , desto/umso + Komparativ … : Je mehr man diskutiert, desto klarer wird die Meinung. Word order: verb at end of je-clause; verb second in desto-clause.",
                [
                    "Je … , desto …",
                    "Je … , umso …",
                ],
                [
                    {
                        "de": "Je mehr Informationen man hat, desto besser kann man wählen.",
                        "en": "The more information you have, the better you can vote.",
                        "fa": "هرچه اطلاعات بیشتر باشد، بهتر می‌توان رأی داد.",
                    },
                    {
                        "de": "Je jünger die Wähler sind, umso digitaler informieren sie sich.",
                        "en": "The younger the voters are, the more digitally they get informed.",
                        "fa": "هرچه رأی‌دهندگان جوان‌تر باشند، بیشتر دیجیتال اطلاع می‌گیرند.",
                    },
                ],
                title_fa="je … desto / umso",
            ),
            g(
                "g2",
                "Relativsätze mit was / wo(r)-; manch- / einig-",
                "Relative clauses with was / wo(r)-; manch- / einig-",
                "was refers to a whole clause, das, or indefinite neuter: alles, was … ; etwas, was … . wo(r)- + prep. for things: das Thema, worüber wir sprechen. manch- / einig- decline like ein/kein or adjectives: mancher Bürger, einige Parteien.",
                [
                    "alles, was …",
                    "das Thema, worüber …",
                    "manche / einige",
                ],
                [
                    {
                        "de": "Alles, was im Grundgesetz steht, ist wichtig.",
                        "en": "Everything that is in the Basic Law is important.",
                        "fa": "هرچه در قانون اساسی آمده مهم است.",
                    },
                    {
                        "de": "Das ist ein Thema, worüber manch einer heftig diskutiert.",
                        "en": "That is a topic about which some people argue heatedly.",
                        "fa": "این موضوعی است که بعضی‌ها درباره‌اش بحث داغ می‌کنند.",
                    },
                ],
                title_fa="جملات نسبی با was/wo(r)-؛ manch-/einig-",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "je … desto",
                "the … the",
                "Je genauer man liest, ___ klarer wird der Text.",
                "desto",
                "g1",
                ["desto", "als", "wie"],
            ),
            drill(
                "d2",
                "cloze",
                "umso",
                "umso",
                "Je länger die Debatte dauert, ___ spannender wird sie.",
                "umso",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "was",
                "was",
                "Alles, ___ du sagst, wird protokolliert.",
                "was",
                "g2",
                ["was", "das", "wo"],
            ),
            drill(
                "d4",
                "cloze",
                "worüber",
                "worüber",
                "Das ist ein Punkt, ___ wir abstimmen müssen.",
                "worüber",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "je desto",
                "je desto",
                "Je | mehr | Stimmen | eine | Partei | hat | , | desto | stärker | ist | sie | .",
                "Je mehr Stimmen eine Partei hat, desto stärker ist sie.",
                "g1",
            ),
            drill(
                "d6",
                "multiple-choice",
                "manche",
                "some",
                "___ Bürger gehen nicht zur Wahl.",
                "Manche",
                "g2",
                ["Manche", "Manches", "Manchen"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Je älter man wird, ___ interessanter wird Politik oft.",
                "desto",
                ["desto", "als", "je"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Je weniger man weiß, ___ unsicherer fühlt man sich.",
                "umso",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Etwas, ___ mich überrascht hat, war die Wahlbeteiligung.",
                "was",
                ["was", "das", "wo"],
                "g2",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Das Gesetz, ___ wir sprechen, ist neu.",
                "worüber",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "___ Parteien sind für Umweltschutz.",
                "Einige",
                ["Einige", "Einiges", "Einigen"],
                "g2",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Je klarer das Programm ist, ___ leichter fällt die Entscheidung.",
                "desto",
                grammar_id="g1",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Nichts, ___ er versprochen hat, wurde umgesetzt.",
                "was",
                ["was", "das", "welche"],
                "g2",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: ___ Wähler wechseln oft die Partei.",
                "Manche",
                grammar_id="g2",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Die Frage, ___ es geht, betrifft das Wahlsystem.",
                "worum",
                ["worum", "worüber", "was"],
                "g2",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Je intensiver man diskutiert, ___ besser versteht man die Positionen.",
                "desto",
                ["desto", "je", "als"],
                "g1",
            ),
        ],
    },
    30: {
        "goals": [
            {
                "de": "Sich austauschen, in welchen Ländern und Regionen Deutsch gesprochen wird",
                "en": "Discuss in which countries and regions German is spoken",
                "fa": "گفتگو درباره کشورهای و مناطقی که آلمانی در آن‌ها صحبت می‌شود",
            },
            {
                "de": "Anhand von Fachartikeln einen Vortrag über die deutsche Sprache halten",
                "en": "Give a talk on the German language based on specialist articles",
                "fa": "ارائه سخنرانی درباره زبان آلمانی بر اساس مقالات تخصصی",
            },
            {
                "de": "Artikel über Varietäten der deutschen Sprache verstehen; Varietäten (D, A, CH, Dialekte) unterscheiden",
                "en": "Understand articles on German varieties; distinguish D/A/CH and dialects",
                "fa": "فهم مقالات درباره گونه‌های آلمانی؛ تمایز آلمان/اتریش/سوئیس و گویش‌ها",
            },
            {
                "de": "Sich über Tipps beim Fremdsprachenlernen austauschen",
                "en": "Exchange tips for learning foreign languages",
                "fa": "گفتگو درباره نکات یادگیری زبان خارجی",
            },
            {
                "de": "Geschichte über Erfahrungen und Ziele beim Lernen verfassen; kleine Texte und Gedichte selbst schreiben",
                "en": "Write about learning experiences and goals; create short texts and poems",
                "fa": "نوشتن درباره تجربه‌ها و اهداف یادگیری؛ نوشتن متون و شعر کوتاه",
            },
        ],
        "grammar": [
            g(
                "g1",
                "Relativpronomen im Genitiv: dessen / deren",
                "Relative pronouns in the genitive: dessen / deren",
                "dessen (masc./neut. antecedent), deren (fem./plural). The relative possessive stands before the noun it owns: der Autor, dessen Buch … ; die Region, deren Dialekt … ; die Länder, deren Sprachen …",
                [
                    "der Mann, dessen …",
                    "die Frau, deren …",
                    "die Länder, deren …",
                ],
                [
                    {
                        "de": "Das ist der Dialekt, dessen Geschichte ich untersuche.",
                        "en": "That is the dialect whose history I am researching.",
                        "fa": "این گویشی است که تاریخش را بررسی می‌کنم.",
                    },
                    {
                        "de": "Österreich ist ein Land, dessen Varietäten ich kennenlernen möchte.",
                        "en": "Austria is a country whose varieties I would like to get to know.",
                        "fa": "اتریش کشوری است که گونه‌های زبانی‌اش را می‌خواهم بشناسم.",
                    },
                ],
                title_fa="ضمایر نسبی در حالت اضافی: dessen / deren",
            ),
            g(
                "g2",
                "Relativsätze mit Genitiv in Kontext",
                "Genitive relative clauses in context",
                "Combine genitive relatives with prepositions and longer NPs: die Stadt, in deren Zentrum … ; der Kurs, mit dessen Hilfe … . Agreement depends on the antecedent, not on the following noun’s gender alone for dessen/deren choice.",
                [
                    "in deren Zentrum …",
                    "mit dessen Hilfe …",
                    "von deren Bedeutung …",
                ],
                [
                    {
                        "de": "Das ist die Sprache, von deren Vielfalt wir sprechen.",
                        "en": "That is the language of whose diversity we are speaking.",
                        "fa": "این زبانی است که درباره تنوع آن حرف می‌زنیم.",
                    },
                    {
                        "de": "Die Schweiz ist ein Land, in dessen Regionen verschiedene Varietäten leben.",
                        "en": "Switzerland is a country in whose regions different varieties live.",
                        "fa": "سوئیس کشوری است که در مناطقش گونه‌های مختلف زنده‌اند.",
                    },
                ],
                title_fa="جملات نسبی با Genitiv در بافت",
            ),
        ],
        "drills": [
            drill(
                "d1",
                "multiple-choice",
                "dessen",
                "dessen",
                "Der Linguist, ___ Buch ich lese, kommt aus Wien.",
                "dessen",
                "g1",
                ["dessen", "deren", "dem"],
            ),
            drill(
                "d2",
                "cloze",
                "deren",
                "deren",
                "Die Varietät, ___ Regeln ich lerne, ist Schweizerdeutsch.",
                "deren",
                "g1",
            ),
            drill(
                "d3",
                "multiple-choice",
                "Plural",
                "plural",
                "Die Dialekte, ___ Unterschiede groß sind, faszinieren mich.",
                "deren",
                "g1",
                ["deren", "dessen", "denen"],
            ),
            drill(
                "d4",
                "cloze",
                "in deren",
                "in deren",
                "Die Stadt, in ___ Zentrum Deutsch gesprochen wird, liegt am Rhein.",
                "deren",
                "g2",
            ),
            drill(
                "d5",
                "reorder",
                "Relativ Gen.",
                "Rel. gen.",
                "Das | ist | der | Kurs | , | mit | dessen | Hilfe | ich | lerne | .",
                "Das ist der Kurs, mit dessen Hilfe ich lerne.",
                "g2",
            ),
            drill(
                "d6",
                "multiple-choice",
                "Neutrum",
                "neuter",
                "Das Land, ___ Sprache ich studiere, ist Deutschland.",
                "dessen",
                "g1",
                ["dessen", "deren", "das"],
            ),
        ],
        "quiz": [
            quiz(
                "q1",
                "grammar-mc",
                "Die Autorin, ___ Gedichte wir lesen, lebt in Berlin.",
                "deren",
                ["deren", "dessen", "der"],
                "g1",
            ),
            quiz(
                "q2",
                "cloze",
                "Complete: Der Dialekt, ___ Melodie mir gefällt, ist bayrisch.",
                "dessen",
                grammar_id="g1",
            ),
            quiz(
                "q3",
                "grammar-mc",
                "Die Länder, ___ Amtssprache Deutsch ist, liegen in Europa.",
                "deren",
                ["deren", "dessen", "denen"],
                "g1",
            ),
            quiz(
                "q4",
                "cloze",
                "Complete: Das Wörterbuch, mit ___ Hilfe ich übersetze, ist neu.",
                "dessen",
                grammar_id="g2",
            ),
            quiz(
                "q5",
                "grammar-mc",
                "Die Region, von ___ Kultur er erzählt, ist Tirol.",
                "deren",
                ["deren", "dessen", "der"],
                "g2",
            ),
            quiz(
                "q6",
                "cloze",
                "Complete: Das Gedicht, ___ Reime einfach sind, schreibe ich selbst.",
                "dessen",
                grammar_id="g1",
            ),
            quiz(
                "q7",
                "grammar-mc",
                "Maskulinum → Relativpronomen Genitiv:",
                "dessen",
                ["dessen", "deren", "dem"],
                "g1",
            ),
            quiz(
                "q8",
                "cloze",
                "Complete: Die Schule, in ___ Klassen man Dialekt hört, liegt in Bayern.",
                "deren",
                grammar_id="g2",
            ),
            quiz(
                "q9",
                "grammar-mc",
                "Femininum Singular → Genitiv-Relativ:",
                "deren",
                ["deren", "dessen", "die"],
                "g1",
            ),
            quiz(
                "q10",
                "grammar-mc",
                "Das ist ein Thema, von ___ Bedeutung wir überzeugt sind.",
                "dessen",
                ["dessen", "deren", "dem"],
                "g2",
            ),
        ],
    },
}


def validate_lesson_payload(n: int, payload: dict) -> None:
    assert len(payload["goals"]) >= 3
    assert len(payload["grammar"]) == 2
    assert len(payload["drills"]) == 6
    assert len(payload["quiz"]) == 10
    for d in payload["drills"]:
        assert d["type"] in {"multiple-choice", "cloze", "reorder"}
        assert d.get("grammarId") in {"g1", "g2"}
        if d["type"] == "multiple-choice":
            assert "options" in d and d["answer"] in d["options"]
    for q in payload["quiz"]:
        assert q["type"] in {"vocab-de-en", "vocab-en-de", "grammar-mc", "cloze"}
        if q["type"] == "grammar-mc":
            assert "options" in q and q["answer"] in q["options"]
            assert q.get("grammarId") in {"g1", "g2"}


def update_lesson(n: int) -> None:
    path = CONTENT / f"b1-l{n:02d}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    payload = deepcopy(LESSONS[n])
    validate_lesson_payload(n, payload)

    data["goals"] = payload["goals"]
    data["grammar"] = payload["grammar"]
    data["drills"] = payload["drills"]
    data["quiz"] = payload["quiz"]
    data["status"] = "complete"

    if not data.get("titleFa"):
        data["titleFa"] = TITLE_FA_FALLBACK[n]

    # Preserve id, level, number, titles, vocab, listening — rewrite in stable key order
    ordered = {
        "id": data["id"],
        "level": data["level"],
        "number": data["number"],
        "titleDe": data["titleDe"],
        "titleEn": data["titleEn"],
        "status": data["status"],
        "goals": data["goals"],
        "vocab": data.get("vocab", []),
        "grammar": data["grammar"],
        "drills": data["drills"],
        "quiz": data["quiz"],
    }
    if "listening" in data:
        ordered["listening"] = data["listening"]
    if data.get("titleFa"):
        ordered["titleFa"] = data["titleFa"]

    path.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"updated {path.name}: goals={len(ordered['goals'])} grammar={len(ordered['grammar'])} drills={len(ordered['drills'])} quiz={len(ordered['quiz'])} vocab={len(ordered['vocab'])}")


def update_index() -> None:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    target = {f"b1-l{n:02d}" for n in range(20, 31)}
    for lesson in index["lessons"]:
        if lesson["id"] in target:
            lesson["status"] = "complete"
    INDEX.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"updated index.json statuses for {sorted(target)}")


def main() -> None:
    for n in range(20, 31):
        update_lesson(n)
    update_index()


if __name__ == "__main__":
    main()
