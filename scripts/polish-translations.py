#!/usr/bin/env python3
"""
Polish DE→EN and DE→FA glosses across lesson JSON.

- Clean Anki HTML junk in fa
- Apply curated EN/FA overrides (quality first)
- Add titleFa + goal fa for all lessons
- Add grammar titleFa / explanationFa for authored A1–A2 topics
- Fill remaining missing fa via GoogleTranslator (cached), then re-apply overrides
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

ROOT = Path("/Users/masoomehghoreishi/Documents/Deutch kurs/Daf Kompakt")
APP = ROOT / "daf-kompakt-app"
CONTENT = APP / "public" / "content" / "lektionen"
FA_CACHE = APP / "scripts" / ".fa-cache.json"
EN_CACHE = APP / "scripts" / ".en-cache.json"
PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")

# --- Lesson titles (DE already in files) ---
TITLE_FA = {
    "a1-l01": "من و دیگران",
    "a1-l02": "قرار ملاقات‌ها",
    "a1-l03": "شرکت خانواده",
    "a1-l04": "بازی و سرگرمی",
    "a1-l05": "بالاخره یک اتاق!",
    "a1-l06": "لباس شخصیت می‌سازد",
    "a1-l07": "خوش آمدید در سوئیس",
    "a1-l08": "مم، چه خوشمزه!",
    "a2-l09": "جشن‌ها را همان‌طور که می‌آیند برگزار کنیم",
    "a2-l10": "جابه‌جایی، اسباب‌کشی، نقل مکان",
    "a2-l11": "تازه در کلن",
    "a2-l12": "داستان‌های بانکی و بیشتر",
    "a2-l13": "سلامتی مثل نمک است",
    "a2-l14": "پاییز در مونیخ",
    "a2-l15": "سفری به وین",
    "a2-l16": "پانصد شغل! اما کدام؟",
    "a2-l17": "کارآموزی: تجربه، یادگیری، لذت",
    "a2-l18": "از آلپ تا دریا",
    "b1-l19": "کارآموز در لیختن‌اشتاین",
    "b1-l20": "تصادف رانندگی در مرکز شهر",
    "b1-l21": "خلاق در هامبورگ",
    "b1-l22": "برو پست!",
    "b1-l23": "تحصیل در آلمان",
    "b1-l24": "کار با طبیعت",
    "b1-l25": "هنر (نکردن) اشتباه",
    "b1-l26": "به سمت درسدن!",
    "b1-l27": "داستان‌ها و چهره‌های برلین",
    "b1-l28": "از اینجا به آنجا — از آنجا به اینجا",
    "b1-l29": "به سیاست علاقه دارید؟",
    "b1-l30": "شخصیت اصلی: آلمانی",
}

# Goal FA keyed by exact German goal string
GOAL_FA: dict[str, str] = {
    "Sich begrüßen (formell und informell)": "سلام کردن (رسمی و غیررسمی)",
    "Sich und andere vorstellen": "معرفی خود و دیگران",
    "Zahlen von 1 bis 1 Milliarde verstehen und sprechen": "فهمیدن و گفتن اعداد از ۱ تا ۱ میلیارد",
    "Telefonnummern verstehen und sprechen": "فهمیدن و گفتن شماره تلفن",
    "Namen buchstabieren und notieren": "هجی کردن و نوشتن نام‌ها",
    "Personalbogen ausfüllen": "پر کردن فرم مشخصات فردی",
    "Sagen, woher man kommt (Adresse, Land, Kontinent)": "گفتن اهل کجا هستید (آدرس، کشور، قاره)",
    "Uhrzeiten verstehen und sagen (formell/informell)": "فهمیدن و گفتن ساعت (رسمی/غیررسمی)",
    "Tageszeiten verstehen und sagen": "فهمیدن و نام بردن اوقات روز",
    "Über Termine sprechen": "صحبت درباره قرارها و نوبت‌ها",
    "Kulturangebote verstehen": "فهمیدن اطلاعات برنامه‌های فرهنگی",
    "Verabredungen verstehen": "فهمیدن قرار ملاقات‌ها",
    "Monate, Datum, Jahreszeiten und Jahreszahlen nennen": "نام بردن ماه‌ها، تاریخ، فصل‌ها و سال‌ها",
    "Eine Urlaubsmail verstehen und schreiben": "فهمیدن و نوشتن ایمیل تعطیلات",
    "Aufgaben im Haushalt verstehen": "فهمیدن کارهای خانه",
    "Sich austauschen, was man kann, muss und möchte": "صحبت درباره اینکه چه می‌توانید، باید و می‌خواهید انجام دهید",
    "Lebensmittel, Mengen und Verpackungen verstehen": "فهمیدن مواد غذایی، مقدارها و بسته‌بندی‌ها",
    "Preise verstehen und sagen": "فهمیدن و گفتن قیمت‌ها",
    "Einkaufszettel schreiben": "نوشتن لیست خرید",
    "Über die Familie und Berufe sprechen": "صحبت درباره خانواده و شغل‌ها",
    "Freizeitanzeigen verstehen": "فهمیدن آگهی‌های اوقات فراغت",
    "Über Freizeit, Hobbys und Sportarten sprechen": "صحبت درباره اوقات فراغت، سرگرمی‌ها و ورزش‌ها",
    "Anzeigen für Freizeitpartner schreiben bzw. darauf antworten": "نوشتن یا پاسخ به آگهی برای شریک اوقات فراغت",
    "Vorlieben und Abneigungen ausdrücken": "بیان علاقه‌ها و بیزاری‌ها",
    "Über das Befinden sprechen": "صحبت درباره حال و احوال",
    "Flyer über Sportangebote verstehen": "فهمیدن بروشور پیشنهادهای ورزشی",
    "Informationen über ein Zimmer/eine Wohnung verstehen und weitergeben": "فهمیدن و انتقال اطلاعات درباره اتاق/آپارتمان",
    "Über sein Wochenende sprechen": "صحبت درباره آخر هفته خود",
    "Möbelanzeigen verstehen": "فهمیدن آگهی‌های مبلمان",
    "Telefonisch einen Möbelkauf verabreden": "تلفنی قرار خرید مبلمان گذاشتن",
    "Sein Zimmer beschreiben": "توصیف اتاق خود",
    "Webseiten zum Thema Waschsalon verstehen": "فهمیدن وب‌سایت‌های مربوط به خشکشویی/لباسشویی",
    "Schriftliche Anleitungen verstehen und formulieren": "فهمیدن و نوشتن دستورالعمل‌های کتبی",
    "Vorschläge verstehen und machen": "فهمیدن و پیشنهاد دادن",
    "Kleidungsstücke und Farben benennen": "نام بردن لباس‌ها و رنگ‌ها",
    "Anweisungen höflich nachfragen und notieren": "مودبانه درباره دستورالعمل‌ها پرسیدن و یادداشت کردن",
    "Informationen über Sehenswürdigkeiten verstehen": "فهمیدن اطلاعات جاذبه‌های گردشگری",
    "Wegbeschreibungen verstehen und machen": "فهمیدن و دادن نشانی راه",
    "Anweisungen am Fahrkartenautomaten verstehen": "فهمیدن دستورالعمل دستگاه بلیت",
    "E-Mail über Erlebnisse schreiben/antworten": "نوشتن یا پاسخ به ایمیل درباره تجربه‌ها",
    "Über kulturelle Besonderheiten bei Einladungen sprechen": "صحبت درباره تفاوت‌های فرهنگی در دعوت‌ها",
    "Über Vorlieben beim Essen und Trinken sprechen": "صحبت درباره سلیقه در غذا و نوشیدنی",
    "Gespräch im Restaurant spielen": "نقش‌بازی مکالمه در رستوران",
    "Speisekarte verstehen": "فهمیدن منو",
    "Vorschläge machen und zustimmen oder ablehnen": "پیشنهاد دادن و موافقت یا رد کردن",
    "Tischreservierung telefonisch verstehen": "فهمیدن رزرو میز تلفنی",
    "Andere um etwas bitten und auf Bitten reagieren": "از دیگران چیزی خواستن و به درخواست‌ها پاسخ دادن",
    "Eine Weihnachtseinladung verstehen": "فهمیدن دعوت‌نامه کریسمس",
    "Einladung, Zusage und Absage schreiben": "نوشتن دعوت، پذیرش و رد",
    "Vermuten, welches Geschenk zu wem passt": "حدس زدن کدام هدیه به چه کسی می‌آید",
    "Sich über Geschenkideen austauschen": "رد و بدل کردن ایده هدیه",
    "Artikel und Statements über Feste und Bräuche verstehen": "فهمیدن متن‌ها و گفته‌ها درباره جشن‌ها و آداب",
    "Über Feste in der Heimat sprechen und schreiben": "صحبت و نوشتن درباره جشن‌های وطن",
    "Gespräch über Wohnlage verstehen": "فهمیدن صحبت درباره موقعیت محله",
    "Wohnungsanzeigen verstehen und über Lage sprechen": "فهمیدن آگهی آپارتمان و صحبت درباره موقعیت",
    "Telefongespräch Mieter–Vermieter spielen": "نقش‌بازی تماس مستأجر–صاحب‌خانه",
    "Mietvertrag ausfüllen und Wohnung beschreiben": "پر کردن قرارداد اجاره و توصیف آپارتمان",
    "Über Studium im Ausland und Wohnungssuche sprechen": "صحبت درباره تحصیل در خارج و جستجوی مسکن",
    "E-Mail über die erste Zeit in Köln verstehen": "فهمیدن ایمیل درباره روزهای اول در کلن",
    "WG-Regeln verstehen und Nachrichten schreiben": "فهمیدن قوانین خانه مشترک و نوشتن پیام",
    "Über Fremdheitserfahrungen sprechen": "صحبت درباره حس غریب بودن",
    "Gespräch am Bankschalter verstehen und nachspielen": "فهمیدن و نقش‌بازی گفتگو در باجه بانک",
    "Anweisungen am Online-Terminal verstehen": "فهمیدن دستورالعمل پایانه آنلاین",
    "Vorfall beschreiben; Fundbüro-Gespräch führen": "توصیف یک رویداد؛ مکالمه در دفتر اشیای گم‌شده",
    "Märchen verstehen und nacherzählen": "فهمیدن و بازگویی یک قصه",
    "Beschwerden verstehen und passenden Arzt finden": "فهمیدن علائم و یافتن پزشک مناسب",
    "Gespräch mit Arzthelferin und Arzt nachspielen": "نقش‌بازی با منشی و پزشک",
    "Körperteile und Beipackzettel verstehen": "نام اعضای بدن؛ فهمیدن بروشور دارو",
    "Museum/Heimat vorstellen": "معرفی موزه / چیزی از وطن",
    "Wetterkarte und Wetterbericht verstehen": "فهمیدن نقشه و گزارش هوا",
    "Über Kleidung sprechen und Kaufhaus-Durchsagen verstehen": "صحبت درباره لباس؛ فهمیدن اعلان‌های فروشگاه",
    "Texte über Oktoberfest verstehen und Volksfest berichten": "فهمیدن متن‌های اوکتوبرفست؛ گزارش جشن محلی",
    "Über Übernachtung und Couchsurfing Meinung äußern": "اظهار نظر درباره اقامت و کوچ‌سرفینگ",
    "Wegbeschreibung nach Wien verstehen und nachspielen": "فهمیدن و نقش‌بازی مسیر به وین",
    "Notizen zu einer Führung machen; Minireiseführer erstellen": "یادداشت از یک تور؛ ساخت راهنمای کوچک سفر",
    "Vorschläge zur Berufswahl verstehen und geben": "فهمیدن و دادن پیشنهاد درباره انتخاب شغل",
    "Über Eignung sprechen; Brief nach Berufsberatung schreiben": "صحبت درباره تناسب؛ نوشتن نامه پس از مشاوره شغلی",
    "Präsentation über den Weg zum Traumberuf halten": "ارائه مسیر رسیدن به شغل رؤیایی",
    "Bewerbungsbrief und Lebenslauf verstehen und schreiben": "فهمیدن و نوشتن نامه درخواست کار و رزومه",
    "Vorstellungsgespräch nachspielen": "نقش‌بازی مصاحبه شغلی",
    "Über Abteilungen und Aufgaben Meinungen äußern": "اظهار نظر درباره بخش‌ها و وظایف",
    "E-Mail über den 1. Tag im Praktikum schreiben": "نوشتن ایمیل درباره روز اول کارآموزی",
    "Urlaubsangebote und Unterkünfte vergleichen": "مقایسه پیشنهادهای تعطیلات و محل اقامت",
    "Vorlieben äußern; um Infos bei einem Gasthof bitten": "بیان سلیقه؛ درخواست اطلاعات از مسافرخانه",
    "Von Urlaubserlebnissen berichten": "گزارش تجربه‌های تعطیلات",
    "Vorschläge und Ratschläge verstehen und äußern": "فهمیدن و بیان پیشنهاد و توصیه",
    "Notizen zu Texten über Liechtenstein machen": "یادداشت از متن‌های مربوط به لیختن‌اشتاین",
    "Gespräch im Reisebüro führen; Reise bestätigen": "مکالمه در آژانس مسافرتی؛ تأیید سفر",
    "Reklamation bei Reisegepäck formulieren": "تنظیم شکایت درباره بار سفر",
    "Wichtigen Wortschatz der Lektion sammeln und üben": "جمع‌آوری و تمرین واژگان مهم درس",
    "Grammatikthemen der Lektion im Überblick wiederholen": "مرور اجمالی موضوعات گرامری درس",
    "Sprachhandlungen in einfachen Übungen anwenden": "به‌کار بردن کنش‌های زبانی در تمرین‌های ساده",
}

# Stub goal template FA (title interpolated)
STUB_GOAL_FA = {
    "learn": "اهداف یادگیری «{title}» را در کتاب دوره بخوانید و بفهمید",
}

# Curated FA + EN overrides (lemma lower key)
FA_OVERRIDE: dict[str, str] = {
    "adresse": "آدرس",
    "alphabet": "الفبا",
    "antwort": "پاسخ",
    "artikel": "حرف تعریف؛ مقاله",
    "aufgabe": "تمرین؛ تکلیف",
    "bleistift": "مداد",
    "blick": "نگاه؛ چشم‌انداز",
    "buchstabe": "حرف الفبا",
    "cd": "سی‌دی",
    "computer": "رایانه؛ کامپیوتر",
    "dialog": "گفتگو",
    "dvd": "دی‌وی‌دی",
    "e-mail-adresse": "آدرس ایمیل",
    "essen": "غذا؛ خوردن",
    "familienname": "نام خانوادگی",
    "fernseher": "تلویزیون",
    "flug": "پرواز",
    "formular": "فرم",
    "frau": "خانم؛ زن",
    "gespräch": "گفتگو",
    "grammatik": "دستور زبان",
    "kurs": "دوره؛ کلاس",
    "kursbuch": "کتاب دوره",
    "nomen": "اسم",
    "ergänzen": "تکمیل کردن",
    "hören": "شنیدن",
    "redemittel": "عبارات آماده گفتار",
    "tabelle": "جدول",
    "partner": "شریک؛ همکار",
    "zeit": "زمان؛ وقت",
    "ganz": "کاملاً؛ تمام",
    "immer": "همیشه",
    "text": "متن",
    "foto": "عکس",
    "person": "شخص",
    "morgen": "صبح؛ فردا",
    "neu": "جدید",
    "rechts": "راست",
    "haus": "خانه",
    "information": "اطلاعات",
    "sagen": "گفتن",
    "endung": "پایان (دستوری)",
    "gruppe": "گروه",
    "stadt": "شهر",
    "woche": "هفته",
    "verb": "فعل",
    "sport": "ورزش",
    "ei": "تخم‌مرغ",
    "satz": "جمله",
    "treffen": "ملاقات؛ قرار",
    "kino": "سینما",
    "wochenende": "آخر هفته",
    "problem": "مشکل",
    "ende": "پایان",
    "leute": "مردم",
    "cafe": "کافه",
    "café": "کافه",
    "name": "نام",
    "team": "تیم",
    "restaurant": "رستوران",
    "hotel": "هتل",
    "million": "میلیون",
    "position": "موقعیت؛ پست",
    "design": "طراحی",
    "gmbh": "شرکت با مسئولیت محدود (آلمانی)",
    "zusammen": "با هم",
    "gemütlich": "دنج؛ راحت",
    "brutto": "ناخالص",
    "praktisch": "کاربردی؛ عملی",
    "glück": "شانس؛ خوشبختی",
    "praxis": "عمل؛ مطب؛ تجربه کاری",
    "einräumen": "چیدن داخل؛ جا دادن",
    "besprechung": "جلسه؛ مذاکره",
    "chefin": "رئیس (زن)",
    "bitte": "خواهش؛ لطفاً",
    "arbeit": "کار",
    "art": "نوع؛ جور",
    "begrüßung": "سلام و احوال‌پرسی",
    "beruf": "شغل؛ حرفه",
    "bürokratie": "بوروکراسی؛ کاغذبازی",
    "anderen": "دیگران",
    "großeinkauf": "خرید عمده؛ خرید بزرگ",
    "band": "گروه موسیقی؛ نوار",
    "chanson": "ترانه‌ی فرانسوی",
    "grüßen": "سلام کردن",
    "kommen": "آمدن",
    "heißen": "نامیده شدن",
    "wohnen": "زندگی کردن؛ سکونت داشتن",
    "sprechen": "صحبت کردن",
    "schreiben": "نوشتن",
    "lesen": "خواندن",
    "machen": "انجام دادن؛ ساختن",
    "gehen": "رفتن",
    "fahren": "رانندگی کردن؛ رفتن (با وسیله)",
    "kaufen": "خریدن",
    "verkaufen": "فروختن",
    "trinken": "نوشیدن",
    "schlafen": "خوابیدن",
    "arbeiten": "کار کردن",
    "lernen": "یاد گرفتن",
    "studieren": "تحصیل کردن",
    "suchen": "جستجو کردن",
    "finden": "پیدا کردن",
    "helfen": "کمک کردن",
    "fragen": "پرسیدن",
    "antworten": "پاسخ دادن",
    "öffnen": "باز کردن",
    "schließen": "بستن",
    "beginnen": "شروع کردن",
    "enden": "پایان یافتن",
    "telefon": "تلفن",
    "handy": "موبایل",
    "nummer": "شماره",
    "land": "کشور؛ سرزمین",
    "stadtteil": "محله",
    "straße": "خیابان",
    "zimmer": "اتاق",
    "wohnung": "آپارتمان",
    "möbel": "مبلمان",
    "tisch": "میز",
    "stuhl": "صندلی",
    "bett": "تخت",
    "schrank": "کمد",
    "tür": "در",
    "fenster": "پنجره",
    "küche": "آشپزخانه",
    "bad": "حمام",
    "badezimmer": "حمام",
    "geld": "پول",
    "preis": "قیمت",
    "euro": "یورو",
    "cent": "سنت",
    "farbe": "رنگ",
    "kleidung": "لباس",
    "hemd": "پیراهن",
    "hose": "شلوار",
    "jacke": "کت",
    "schuhe": "کفش",
    "freund": "دوست (مرد)",
    "freundin": "دوست (زن)",
    "familie": "خانواده",
    "mutter": "مادر",
    "vater": "پدر",
    "kind": "کودک",
    "sohn": "پسر",
    "tochter": "دختر",
    "bruder": "برادر",
    "schwester": "خواهر",
    "mann": "مرد؛ شوهر",
    "herr": "آقا",
    "heute": "امروز",
    "gestern": "دیروز",
    "uhr": "ساعت",
    "minute": "دقیقه",
    "stunde": "ساعت (مدت)",
    "tag": "روز",
    "monat": "ماه",
    "jahr": "سال",
    "frühling": "بهار",
    "sommer": "تابستان",
    "herbst": "پاییز",
    "winter": "زمستان",
    "wetter": "هوا",
    "regen": "باران",
    "sonne": "خورشید",
    "schnee": "برف",
    "arzt": "پزشک",
    "ärztin": "پزشک (زن)",
    "krankenhaus": "بیمارستان",
    "apotheke": "داروخانه",
    "schmerz": "درد",
    "krankheit": "بیماری",
    "gesundheit": "سلامتی",
    "reise": "سفر",
    "urlaub": "مرخصی؛ تعطیلات",
    "flugzeug": "هواپیما",
    "zug": "قطار",
    "bus": "اتوبوس",
    "bahnhof": "ایستگاه قطار",
    "flughafen": "فرودگاه",
    "ticket": "بلیت",
    "fahrkarte": "بلیت",
    "karte": "نقشه؛ کارت؛ منو",
    "bank": "بانک؛ نیمکت",
    "konto": "حساب بانکی",
    "passwort": "رمز عبور",
    "schlüssel": "کلید",
    "türschlüssel": "کلید در",
    "allergie": "آلرژی؛ حساسیت",
    "diät": "رژیم غذایی",
    "fall": "مورد؛ پرونده",
    "fieber": "تب",
    "husten": "سرفه",
    "leben": "زندگی؛ زنده بودن",
    "temperatur": "دما؛ تب",
    "oben": "بالا",
    "unten": "پایین",
    "auto": "ماشین",
    "betrieb": "کارخانه؛ محل کار",
    "cousine": "دخترعمه/خاله",
    "dame": "خانم",
    "eis": "بستنی؛ یخ",
    "erbse": "نخود فرنگی",
    "erinnerung": "خاطره؛ یادآوری",
    "etikett": "برچسب",
    "fan": "هوادار",
    "geschmack": "طعم؛ سلیقه",
    "handschuhe": "دستکش",
    "hostel": "هاستل",
    "kontakt": "تماس؛ ارتباط",
    "kuchen": "کیک",
    "mannschaft": "تیم",
    "milch": "شیر",
    "nudel": "رشته؛ پاستا",
    "oktoberfest": "جشن اکتبر (مونیخ)",
    "packung": "بسته",
    "patient": "بیمار",
    "pfeffer": "فلفل",
    "bürgermeister": "شهردار",
    "bürgermeisterin": "شهردار (زن)",
    "dirndl": "لباس سنتی زنانه بایرنی",
    "lederhose": "شلوار چرمی سنتی",
    "bierfass": "بشکه آبجو",
    "brathendl": "مرغ بریان (بایرنی)",
    "kassenbon": "رسید صندوق",
    "kleidergröße": "سایز لباس",
    "daunenmantel": "پالتو پر",
    "herrenabteilung": "بخش آقایان",
    "haushaltsware": "لوازم خانگی",
    "gastwirt": "صاحب رستوران/مسافرخانه",
    "analytik": "آنالیتیک؛ تحلیل",
    "bescheid sagen": "خبر دادن؛ اطلاع دادن",
    "betrag wählen": "انتخاب مبلغ",
    "geld entnehmen": "برداشت پول",
    "karte einführen": "وارد کردن کارت",
    "karte entnehmen": "برداشتن کارت",
    "pin eingeben": "وارد کردن رمز (PIN)",
    "angehen": "شروع شدن؛ مربوط بودن",
    "benutzen": "استفاده کردن",
    "entdecken": "کشف کردن",
    "fehlen": "کم بودن؛ غایب بودن",
    "formulieren": "فرمول‌بندی کردن؛ بیان کردن",
    "mitbringen": "همراه آوردن",
    "sammeln": "جمع کردن",
    "stellen": "گذاشتن (ایستاده)",
    "tauschen": "عوض کردن",
    "vergleichen": "مقایسه کردن",
    "verstehen": "فهمیدن",
    "verwenden": "به کار بردن",
    "wandern": "پیاده‌روی در طبیعت",
    "übernachten": "شب ماندن",
    "ablehnen": "رد کردن",
    "brechen": "شکستن",
    "profi": "حرفه‌ای",
    "putzfrau": "نظافتچی (زن)",
    "reis": "برنج",
    "rekord": "رکورد",
    "salat": "سالاد",
    "soldat": "سرباز",
    "soldatin": "سرباز (زن)",
    "sparkonto": "حساب پس‌انداز",
    "spielzeug": "اسباب‌بازی",
    "supermarkt": "سوپرمارکت",
    "tagesgeld": "سود روزانه؛ پول روزانه",
    "terminal": "پایانه",
    "treffpunkt": "محل قرار",
    "vorfall": "رویداد؛ حادثه",
    "wg": "خانه مشترک (WG)",
    "wirt": "میزبان؛ صاحب مسافرخانه",
    "wolke": "ابر",
    "zahlung": "پرداخت",
    "zucker": "شکر",
    "zweck": "هدف؛ مقصود",
    "abgeben": "تحویل دادن",
    "anklicken": "کلیک کردن",
    "behalten": "نگه داشتن",
    "betrügen": "فریب دادن",
    "bis": "تا",
    "brennen": "سوختن؛ آتش گرفتن",
    "cool": "باحال؛ عالی",
    "darum": "به همین دلیل",
    "des": "از (حالت اضافی)",
    "deswegen": "به همین خاطر",
    "un-": "پیشوند منفی‌ساز (un-)",
    "dieser": "این",
    "einsammeln": "جمع کردن",
    "eintreffen": "رسیدن",
    "einzahlen": "واریز کردن",
    "geblümt": "گل‌دار",
    "gestreift": "راه‌راه",
    "herankommen": "نزدیک شدن",
    "indirekte frage": "سؤال غیرمستقیم",
    "nacherzählen": "بازگویی کردن",
    "nicht zu": "نه خیلی؛ نه آن‌قدر",
    "passieren": "اتفاق افتادن",
    "pflanzen": "کاشتن؛ گیاه",
    "rauchen": "سیگار کشیدن",
    "raus": "بیرون",
    "salzig": "شور",
    "unfreundlich": "غیرمودب؛ سرد",
    "viele": "خیلی‌ها؛ بسیاری",
    "weh tun": "درد کردن",
    "welcher": "کدام",
    "wenige": "تعداد کمی",
    "zerbrochen": "شکسته",
    "zu": "به؛ خیلی",
    "ärmel": "آستین",
    "übernachtung": "اقامت شبانه",
    "überweisung": "حواله؛ انتقال بانکی",
    "überweisen": "حواله کردن",
}

EN_OVERRIDE: dict[str, str] = {
    "cd": "CD",
    "dvd": "DVD",
    "gmbh": "Ltd (GmbH)",
    "fernseher": "TV / television",
    "großeinkauf": "big shopping trip / bulk shopping",
    "dialog": "dialogue",
    "alphabet": "alphabet",
    "computer": "computer",
    "design": "design",
    "name": "name",
    "partner": "partner",
    "person": "person",
    "position": "position / job title",
    "restaurant": "restaurant",
    "team": "team",
    "text": "text",
    "verb": "verb",
    "band": "band",
    "cafe": "café",
    "café": "café",
    "hotel": "hotel",
    "chanson": "chanson (French song)",
    "million": "million",
    "essen": "food; to eat",
    "morgen": "morning; tomorrow",
    "bitte": "please; request",
    "art": "kind / type",
    "arbeit": "work / job",
    "besprechung": "meeting",
    "chefin": "boss (female)",
    "blick": "look; view",
    "gespräch": "conversation",
    "redemittel": "useful phrases",
    "kursbuch": "course book",
    "nomen": "noun",
    "endung": "ending (grammar)",
    "ergänzen": "to complete / fill in",
}


GRAMMAR_FA = {
    # titleDe -> (titleFa, explanationFa)
    "Regelmäßige Verben und „sein“ im Präsens": (
        "فعل‌های باقاعده و «sein» در زمان حال",
        "در زمان حال آلمانی (Präsens) بیشتر فعل‌ها یک ریشه دارند و پایانه‌های -e، -st، -t، -en، -t، -en می‌گیرند. فعل sein بی‌قاعده است: ich bin، du bist، er/sie/es ist، wir sind، ihr seid، sie/Sie sind.",
    ),
    "Personalpronomen und Wortstellung (Aussage, W-Frage, Ja/Nein-Frage)": (
        "ضمایر شخصی و ترتیب کلمات",
        "ضمایر فاعلی: ich، du، er/sie/es، wir، ihr، sie/Sie. در جمله خبری فعل در جایگاه دوم است. سؤال با کلمه پرسشی (W-Frage) با آن کلمه شروع می‌شود؛ سؤال بله/خیر با فعل شروع می‌شود.",
    ),
    "Verneinung: „nicht“ und „kein-“": (
        "نفی با nicht و kein-",
        "قبل از اسم بدون حرف تعریف معین از kein- استفاده کنید (kein Termin، keine Zeit). برای نفی فعل، صفت، قید یا بخش‌های دیگر جمله از nicht استفاده کنید.",
    ),
    "Bestimmter und unbestimmter Artikel (Nom./Akk.)": (
        "حرف تعریف معین و نامعین (فاعلی/مفعولی)",
        "فاعلی: der/die/das و ein/eine/ein. در مفعولی فقط مذکر عوض می‌شود: den / einen. مؤنث و خنثی die/eine و das/ein می‌مانند.",
    ),
    "Modalverben: können, müssen, möcht-": (
        "افعال وجهی: können، müssen، möchten",
        "فعل وجهی صرف می‌شود و فعل اصلی به صورت مصدر در پایان می‌ماند: Ich kann kochen. Ich muss einkaufen. Ich möchte bleiben.",
    ),
    "Possessivartikel im Nominativ; W-Fragen mit Wie viel/Wie viele": (
        "صفات ملکی؛ چقدر / چند تا",
        "mein/dein/sein/ihr/unser… با اسم تطبیق می‌کنند: mein Bruder، meine Schwester. Wie viel؟ برای غیرقابل‌شمارش؛ Wie viele؟ برای قابل‌شمارش.",
    ),
    "Modalverben dürfen, wollen, mögen; Verben mit Vokalwechsel": (
        "افعال وجهی dürfen/wollen/mögen؛ فعل‌های با تغییر واکه",
        "dürfen = اجازه داشتن؛ wollen = خواستن؛ mögen = دوست داشتن. برخی فعل‌ها در du/er واکه عوض می‌کنند: ich lese، du liest؛ ich fahre، du fährst.",
    ),
    "haben/sein im Präteritum; Konnektoren denn, oder, aber": (
        "haben/sein در گذشته ساده؛ حروف ربط denn/oder/aber",
        "ich war، du warst؛ ich hatte، du hattest. denn/oder/aber جمله‌های اصلی را وصل می‌کنند و فعل در هر بند در جایگاه ۲ می‌ماند.",
    ),
    "Trennbare Verben im Präsens und Perfekt": (
        "فعل‌های جداشدنی در حال و کامل",
        "در حال، پیشوند به پایان می‌رود: Ich räume das Zimmer auf. در کامل: Ich habe das Zimmer aufgeräumt.",
    ),
    "Regelmäßige Verben im Perfekt": (
        "فعل‌های باقاعده در زمان کامل (Perfekt)",
        "بیشتر فعل‌ها با haben + ge-…-t می‌آیند: ich habe gesucht. حرکت/تغییر وضعیت اغلب با sein: ich bin eingezogen.",
    ),
    "Imperativ (Sie / du / ihr) und Vorschläge": (
        "امر و پیشنهادها",
        "رسمی: Nehmen Sie …! غیررسمی du: Nimm …! جمع ihr: Nehmt …! پیشنهاد: Sollen/Wollen wir …؟",
    ),
    "Unregelmäßige und gemischte Verben im Perfekt; untrennbare Vorsilben": (
        "فعل‌های بی‌قاعده و ترکیبی در کامل؛ پیشوندهای جدا‌نشدنی",
        "بی‌قاعده: gefunden، genommen. ترکیبی: gebracht، gedacht. پیشوندهای be-/ge-/er-/ver-/zer- بدون ge- اضافی: besucht، verkauft.",
    ),
    "Ortsangaben mit Akkusativ und Dativ": (
        "عبارات مکانی با مفعولی و مفعول‌الیهی",
        "حروف اضافه دوسویه (in، an، auf…): مکان (کجا؟) → داتیو؛ جهت (به کجا؟) → آکوزاتیو.",
    ),
    "Indefinitpronomen etwas/nichts/alle/man; Präsens für Zukunft": (
        "ضمایر نامعین؛ حال برای آینده",
        "man sagt… = می‌گویند. etwas/nichts. با قید زمان، حال می‌تواند آینده باشد: Morgen fahren wir nach Bern.",
    ),
    "Adjektive im Nominativ und Akkusativ nach unbestimmtem Artikel": (
        "صفت‌ها پس از ein/eine در فاعلی و مفعولی",
        "پس از ein/eine/kein و صفات ملکی، صفت پایانه‌های ویژه می‌گیرد: ein leckerer Salat، einen leckeren Salat.",
    ),
    "Zusammengesetzte Nomen; Nomen aus Infinitiv/Adjektiv": (
        "اسم‌های مرکب؛ اسم از مصدر/صفت",
        "جنسیت اسم مرکب از جزء آخر می‌آید: der Obstsalat. مصدر می‌تواند اسم خنثی شود: das Essen.",
    ),
}


def load_cache(path: Path) -> dict[str, str]:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_cache(path: Path, cache: dict[str, str]) -> None:
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n")


def lemma_key(de: str) -> str:
    s = de.strip()
    s = re.sub(r"^(der|die|das)\s+", "", s, flags=re.I)
    s = re.sub(r"\s*\(.*?\)\s*", " ", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def clean_fa(fa: str) -> str:
    fa = re.sub(r"<br\s*/?>", " ", fa, flags=re.I)
    fa = re.sub(r"<[^>]+>", " ", fa)
    fa = (
        fa.replace("&nbsp;", " ")
        .replace("&nbsp", " ")
        .replace("&lt;", "")
        .replace("&lt", "")
        .replace("&gt;", "")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
    )
    # Drop German conjugation / example tails that pollute Anki backs
    fa = re.sub(
        r"\b(er|sie|es|ich|du|wir|ihr)\s+[a-zäöüß]+(?:\s+[a-zäöüß\-]+)*",
        " ",
        fa,
        flags=re.I,
    )
    fa = re.sub(
        r"\b(?:hat|ist|hatte|war)\s+[a-zäöüß]+",
        " ",
        fa,
        flags=re.I,
    )
    fa = re.sub(r"\b(?:das|der|die|eine?|einen?)\b", " ", fa, flags=re.I)
    fa = re.sub(r"#\s*[a-zäöüß]+", " ", fa, flags=re.I)
    fa = re.sub(r"\+[A-Z]\b", " ", fa)
    fa = re.sub(r"\bausräumen\b", "", fa, flags=re.I)
    # Keep Persian-containing segments; drop pure Latin leftovers
    parts = re.split(r"[,;/|،]+", fa)
    kept = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if PERSIAN_RE.search(p):
            # remove leftover latin words inside
            p2 = re.sub(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß\-]{2,}", " ", p)
            p2 = re.sub(r"\s+", " ", p2).strip(" -")
            if PERSIAN_RE.search(p2):
                kept.append(p2)
    fa = "، ".join(kept) if kept else fa
    fa = re.sub(r"\s+", " ", fa).strip(" ,;/-،")
    return fa


def fix_en(en: str, de: str) -> str:
    key = lemma_key(de)
    if key in EN_OVERRIDE:
        return EN_OVERRIDE[key]
    # Fix weird casing like cD, dVD, gmbH
    if en and de and en.lower() == de.lower() and de[:1].isupper():
        # keep common cognates capitalized nicely
        if de.isupper() and len(de) <= 4:
            return de
        if de.lower() in {"cd", "dvd", "tv", "pc", "wg"}:
            return de.upper() if de.lower() != "wg" else "WG"
    if re.fullmatch(r"[a-z].*", en or "") and de[:1].isupper() and " " not in en:
        # "computer" from "Computer" is fine; "cD" is not
        if any(c.isupper() for c in en[1:]):
            return de if len(de) <= 5 else en.capitalize()
    return en


def translate_fa_batch(words: list[str], cache: dict[str, str]) -> dict[str, str]:
    from deep_translator import GoogleTranslator

    t = GoogleTranslator(source="de", target="fa")
    missing = [w for w in words if lemma_key(w) not in cache and lemma_key(w) not in FA_OVERRIDE]
    print(f"Translating {len(missing)} DE→FA glosses…", flush=True)
    batch_size = 20
    for i in range(0, len(missing), batch_size):
        batch = missing[i : i + batch_size]
        try:
            outs = t.translate_batch(batch)
            for w, fa in zip(batch, outs):
                if isinstance(fa, str) and PERSIAN_RE.search(fa):
                    cache[lemma_key(w)] = clean_fa(fa)
                else:
                    cache[lemma_key(w)] = ""
        except Exception as e:
            print(f"  batch fail {i}: {e}", flush=True)
            for w in batch:
                try:
                    fa = t.translate(w)
                    cache[lemma_key(w)] = clean_fa(fa) if fa else ""
                    time.sleep(0.1)
                except Exception as e2:
                    print("  fail", w, e2, flush=True)
                    cache[lemma_key(w)] = ""
                    time.sleep(0.8)
        save_cache(FA_CACHE, cache)
        print(f"  {min(i + batch_size, len(missing))}/{len(missing)}", flush=True)
        time.sleep(0.35)
    return cache


def stub_goal_fa(de: str, title_de: str, title_fa: str) -> str | None:
    m = re.match(r'Lernziele zu „(.+?)“ im Kursbuch nachlesen und verstehen', de)
    if m:
        return STUB_GOAL_FA["learn"].format(title=title_fa or title_de)
    return GOAL_FA.get(de)


def polish_lesson(path: Path, fa_cache: dict[str, str]) -> tuple[int, int]:
    data = json.loads(path.read_text())
    lid = data["id"]
    changed_vocab = 0

    title_fa = TITLE_FA.get(lid)
    if title_fa and data.get("titleFa") != title_fa:
        data["titleFa"] = title_fa

    # goals
    for g in data.get("goals") or []:
        fa = GOAL_FA.get(g["de"]) or stub_goal_fa(
            g["de"], data.get("titleDe", ""), data.get("titleFa", "")
        )
        if fa and g.get("fa") != fa:
            g["fa"] = fa

    # grammar
    for topic in data.get("grammar") or []:
        pair = GRAMMAR_FA.get(topic.get("titleDe", ""))
        if pair:
            tfa, efa = pair
            if topic.get("titleFa") != tfa:
                topic["titleFa"] = tfa
            if topic.get("explanationFa") != efa:
                topic["explanationFa"] = efa
        for ex in topic.get("examples") or []:
            # leave example fa to cache/override via de of example? skip for now
            pass

    # vocab
    for v in data.get("vocab") or []:
        de = v.get("de") or ""
        key = lemma_key(de)
        old_en, old_fa = v.get("en"), v.get("fa")

        new_en = fix_en(old_en or "", de)
        if key in EN_OVERRIDE:
            new_en = EN_OVERRIDE[key]
        if new_en and new_en != old_en:
            v["en"] = new_en
            changed_vocab += 1

        new_fa = None
        if key in FA_OVERRIDE:
            new_fa = FA_OVERRIDE[key]
        elif old_fa:
            cleaned = clean_fa(old_fa)
            # if cleanup removed all persian, drop
            new_fa = cleaned if PERSIAN_RE.search(cleaned) else None
        if not new_fa:
            cached = fa_cache.get(key)
            if cached and PERSIAN_RE.search(cached):
                new_fa = clean_fa(cached)

        if new_fa and v.get("fa") != new_fa:
            v["fa"] = new_fa
            changed_vocab += 1
        elif not new_fa and old_fa and clean_fa(old_fa) != old_fa:
            cleaned = clean_fa(old_fa)
            if PERSIAN_RE.search(cleaned):
                v["fa"] = cleaned
                changed_vocab += 1
            else:
                v.pop("fa", None)
                changed_vocab += 1

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return 1, changed_vocab


def main() -> None:
    fa_cache = load_cache(FA_CACHE)
    # seed overrides into cache
    for k, v in FA_OVERRIDE.items():
        fa_cache[k] = v

    missing_words: list[str] = []
    for path in sorted(CONTENT.glob("*.json")):
        data = json.loads(path.read_text())
        for v in data.get("vocab") or []:
            key = lemma_key(v.get("de") or "")
            fa = v.get("fa")
            if key in FA_OVERRIDE:
                continue
            if fa and PERSIAN_RE.search(clean_fa(fa)):
                continue
            if key and key not in fa_cache:
                missing_words.append(v["de"])

    # unique preserve order
    seen = set()
    uniq = []
    for w in missing_words:
        k = lemma_key(w)
        if k not in seen:
            seen.add(k)
            uniq.append(w)

    if uniq:
        translate_fa_batch(uniq, fa_cache)
        save_cache(FA_CACHE, fa_cache)

    lessons = vocab_changes = 0
    for path in sorted(CONTENT.glob("*.json")):
        l, c = polish_lesson(path, fa_cache)
        lessons += l
        vocab_changes += c
        print(f"  polished {path.name}")

    # coverage report
    total = with_fa = 0
    for path in CONTENT.glob("*.json"):
        data = json.loads(path.read_text())
        for v in data.get("vocab") or []:
            total += 1
            if v.get("fa") and PERSIAN_RE.search(v["fa"]):
                with_fa += 1
        goals = data.get("goals") or []
        g_fa = sum(1 for g in goals if g.get("fa"))
        print(f"  {data['id']}: goals fa {g_fa}/{len(goals)}")

    print(
        f"Done. Lessons {lessons}, vocab field updates ~{vocab_changes}, "
        f"FA coverage {with_fa}/{total} ({100 * with_fa / max(total, 1):.0f}%)"
    )


if __name__ == "__main__":
    main()
