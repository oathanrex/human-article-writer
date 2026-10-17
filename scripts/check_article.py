#!/usr/bin/env python3
"""
check_article.py - lint a markdown article against the human-article-writer rules.

Usage:
    python scripts/check_article.py draft.md [--target 900] [--tolerance 0.15]
                                    [--tool "ToolName"] [--max-tool 3] [--no-notes]
                                    [--lang en] [--strict] [--json]

Use "-" as the file to read from stdin.
Exit code:
    0 if clean (or only CHECK items when not in --strict mode)
    1 if any FIX item is found (or any CHECK item in --strict mode)
    2 if file not found or invalid args
FIX   = must change.  CHECK = look at it and decide.  INFO = context only.
"""
import argparse
from collections import Counter
import json as json_mod
import pathlib
import re
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
REFS_DIR = HERE.parent / "references"

SENT_SPLIT = re.compile(r"(?<=[.!?।])\s+(?=[A-Za-z0-9\u0900-\u097F\"'(\u00C0-\u017F])")
# Unicode-aware word pattern covering Latin (with accents/umlauts), Devanagari, etc.
WORD = re.compile(r"[\w]+(?:['’]\w+)?", re.UNICODE)

OPINION_PATTERNS = {
    "en": re.compile(
        r"\b(i think|i'd say|i would say|in my opinion|i feel|i kinda think|i kind of think|"
        r"honestly|i prefer|i lean|my guess|personally|i'd go with|i'd put|i'd post|i'd assume|"
        r"i wouldn't|i'd keep|i'd start|i'd treat|i'd probably)\b",
        re.I,
    ),
    "hi": re.compile(
        r"(mere hisaab se|mujhe lagta|mera maanna|sachchi baat|sach kahun to|sach kahun toh|"
        r"mere khayal se|main to kahun|main manta|meri rai|mujhe lagta hai|"
        r"मेरे हिसाब से|मुझे लगता|मेरा मानना|सच कहूँ तो|मेरी राय|"
        r"मैं तो कहूंगा|ईमानदारी से)",
        re.I,
    ),
    "es": re.compile(
        r"\b(en mi opinión|creo que|me parece que|sinceramente|la verdad es que|yo diría que|"
        r"personalmente|a mi parecer|desde mi punto de vista|prefiero)\b",
        re.I,
    ),
    "fr": re.compile(
        r"\b(à mon avis|je pense que|je trouve que|honnêtement|personnellement|d'après moi|"
        r"selon moi|j'ai l'impression que|pour ma part)\b",
        re.I,
    ),
    "de": re.compile(
        r"\b(meiner meinung nach|ich denke|ich finde|ehrlich gesagt|persönlich|"
        r"meines erachtens|ich würde sagen|aus meiner sicht)\b",
        re.I,
    ),
    "pt": re.compile(
        r"\b(na minha opinião|acho que|acredito que|sinceramente|a meu ver|"
        r"eu diria que|pessoalmente|no meu entender|prefiro)\b",
        re.I,
    ),
    "it": re.compile(
        r"\b(secondo me|a mio parere|credo che|penso che|onestamente|"
        r"a mio avviso|personalmente|direi che|per quanto mi riguarda)\b",
        re.I,
    ),
    "ja": re.compile(
        r"(私の意見では|個人的には|正直なところ|〜だと思います|〜だと考えます|"
        r"私の見解では|個人的な感想として|個人的には|と思う|と考えます)",
        re.I,
    ),
    "zh": re.compile(
        r"(在我看来|我个人认为|坦白说|老实说|我倾向于|依我看|我个人觉得|我认为|我觉得)",
        re.I,
    ),
    "ru": re.compile(
        r"\b(по моему мнению|на мой взгляд|я считаю|честно говоря|лично я|мне кажется|по-моему)\b",
        re.I,
    ),
    "ar": re.compile(
        r"(في رأيي|أعتقد أن|أرى أن|بصراحة|شخصيا|من وجهة نظري|أعتقد|أرى)",
        re.I,
    ),
    "nl": re.compile(
        r"\b(naar mijn mening|ik denk|ik vind|eerlijk gezegd|persoonlijk|ik zou zeggen|mijn inziens)\b",
        re.I,
    ),
    "ko": re.compile(
        r"(제 생각에는|개인적으로|솔직히|~라고 생각합니다|제 의견으로는|생각합니다|보입니다)",
        re.I,
    ),
    "tr": re.compile(
        r"\b(bana göre|bence|düşünüyorum|dürüst olmak gerekirse|kişisel olarak|sanırım)\b",
        re.I,
    ),
    "pl": re.compile(
        r"\b(moim zdaniem|uważam że|myślę że|szczerze mówiąc|osobiście|według mnie)\b",
        re.I,
    ),
    "id": re.compile(
        r"\b(menurut saya|saya rasa|sejujurnya|menurut hemat saya|secara pribadi|saya pikir|pendapat saya)\b",
        re.I,
    ),
    "vi": re.compile(
        r"(theo tôi|tôi nghĩ rằng|thành thật mà nói|cá nhân tôi|tôi cho rằng|theo quan điểm của tôi|tôi nghĩ)",
        re.I,
    ),
    "bn": re.compile(
        r"(আমার মতে|আমার মনে হয়|সত্যি বলতে|ব্যক্তিগতভাবে|আমি মনে করি|আমার বিবেচনায়)",
        re.I,
    ),
    "ur": re.compile(
        r"(میرے خیال میں|میری رائے میں|سچ کہوں تو|ذاتی طور پر|مجھے لگتا ہے|میرا خیال ہے)",
        re.I,
    ),
    "uk": re.compile(
        r"\b(на мою думку|на мій погляд|я вважаю|чесно кажучи|особисто я|мені здається)\b",
        re.I,
    ),
    "sv": re.compile(
        r"\b(enligt min mening|jag tycker|jag anser|ärligt talat|personligen|jag skulle säga)\b",
        re.I,
    ),
    "cs": re.compile(
        r"\b(podle mého názoru|myslím že|podle mě|upřímně řečeno|osobně|řekl bych)\b",
        re.I,
    ),
    "ro": re.compile(
        r"\b(în opinia mea|cred că|după părerea mea|sincer să fiu|personal|aș spune că)\b",
        re.I,
    ),
    "el": re.compile(
        r"(κατά τη γνώμη μου|πιστεύω ότι|ειλικρινά|προσωπικά|θεωρώ ότι|θα έλεγα ότι)",
        re.I,
    ),
    "hu": re.compile(
        r"\b(véleményem szerint|szerintem|őszintén szólva|személy szerint|úgy gondolom|azt mondanám)\b",
        re.I,
    ),
    "da": re.compile(
        r"\b(efter min mening|jeg synes|jeg mener|ærligt talt|personligt|jeg vil sige)\b",
        re.I,
    ),
    "fi": re.compile(
        r"\b(mielestäni|omasta mielestäni|rehellisesti sanottuna|henkilökohtaisesti|sanoisin että|luulen että)\b",
        re.I,
    ),
    "no": re.compile(
        r"\b(etter min mening|jeg synes|jeg mener|ærlig talt|personlig|jeg vil si)\b",
        re.I,
    ),
    "he": re.compile(
        r"(לדעתי|אני חושב|לפי דעתי|למען האמת|באופן אישי|הייתי אומר)",
        re.I,
    ),
    "th": re.compile(
        r"(ในความคิดของผม|ในมุมมองของฉัน|ส่วนตัวแล้ว|พูดตามตรง|ผมคิดว่า|ฉันคิดว่า)",
        re.I,
    ),
    "fa": re.compile(
        r"(به نظر من|من فکر می‌کنم|صادقانه بگویم|شخصاً|به عقیده من|من معتقدم)",
        re.I,
    ),
    "ms": re.compile(
        r"\b(pada pendapat saya|saya rasa|sejujurnya|secara peribadi|saya fikir|pandangan saya)\b",
        re.I,
    ),
    "tl": re.compile(
        r"\b(sa tingin ko|sa palagay ko|sa totoo lang|personal kong|para sa akin|masasabi ko)\b",
        re.I,
    ),
    "sw": re.compile(
        r"\b(kwa maoni yangu|nafikiri|kwa kweli|binafsi|nadhani|kwa mtazamo wangu)\b",
        re.I,
    ),
}

EXPERIENCE_PATTERNS = {
    "en": re.compile(
        r"\b(i (?:tried|tested|used|ran|compared|timed|checked|measured|switched)|"
        r"i've (?:tried|tested|used|compared|wasted|seen|noticed|found)|"
        r"last (?:week|month|year)|"
        r"in my (?:testing|test|experience)|when i (?:tried|tested|used|ran)|"
        r"my (?:colleague|friend|team|boss|client) (?:told|said|tried)|"
        r"i (?:noticed|found|discovered|realized|saw) that)\b",
        re.I,
    ),
    "hi": re.compile(
        r"(maine try kiya|maine test kiya|maine use kiya|maine dekha ki|maine notice kiya|"
        r"mere experience mein|pichle hafte|pichle mahine|jab maine|"
        r"मैंने ट्राई किया|मैंने टेस्ट किया|मैंने देखा कि|मेरे एक्सपीरियंस में|"
        r"पिछले हफ्ते|पिछले महीने|जब मैंने)",
        re.I,
    ),
    "es": re.compile(
        r"\b(he probado|probé|usé|utilicé|hice una prueba|en mis pruebas|en mi experiencia|"
        r"la semana pasada|el mes pasado|cuando probé|me di cuenta de que)\b",
        re.I,
    ),
    "fr": re.compile(
        r"\b(j'ai testé|j'ai essayé|j'ai utilisé|dans mes tests|dans mon expérience|"
        r"la semaine dernière|le mois dernier|en testant|j'ai remarqué que)\b",
        re.I,
    ),
    "de": re.compile(
        r"\b(ich habe getestet|ich habe ausprobiert|in meinen tests|in meiner erfahrung|"
        r"letzte woche|letzten monat|beim testen|ich habe bemerkt)\b",
        re.I,
    ),
    "pt": re.compile(
        r"\b(eu testei|testei|usei|utilizei|fiz um teste|nos meus testes|na minha experiência|"
        r"semana passada|mês passado|quando testei|notei que)\b",
        re.I,
    ),
    "it": re.compile(
        r"\b(ho testato|ho provato|ho usato|utilizzato|fatto un test|nei miei test|nella mia esperienza|"
        r"la scorsa settimana|il mese scorso|quando ho provato|ho notato che)\b",
        re.I,
    ),
    "ja": re.compile(
        r"(試してみました|テストしました|使ってみました|私のテストでは|先週|先月|実際に使ってみたところ)",
        re.I,
    ),
    "zh": re.compile(
        r"(我测试了|我尝试了|我使用了|在我的测试中|上周|上个月|当我测试时|我注意到)",
        re.I,
    ),
    "ru": re.compile(
        r"\b(я протестировал|я попробовал|я использовал|в моем опыте|на прошлой неделе|в прошлом месяце|я заметил что)\b",
        re.I,
    ),
    "ar": re.compile(
        r"(لقد جربت|اختبرت|استخدمت|في تجربتي|الأسبوع الماضي|الشهر الماضي|عندما جربت)",
        re.I,
    ),
    "nl": re.compile(
        r"\b(ik heb getest|ik heb geprobeerd|ik gebruikte|in mijn ervaring|vorige week|vorige maand|toen ik testte)\b",
        re.I,
    ),
    "ko": re.compile(
        r"(제가 테스트해봤을 때|직접 사용해보니|지난주에|지난달에|테스트 결과)",
        re.I,
    ),
    "tr": re.compile(
        r"\b(test ettim|denedim|kullandım|deneyimlerime göre|geçen hafta|geçen ay)\b",
        re.I,
    ),
    "pl": re.compile(
        r"\b(przetestowałem|wypróbowałem|użyłem|w moim doświadczeniu|w zeszłym tygodniu|w zeszłym miesiącu)\b",
        re.I,
    ),
    "id": re.compile(
        r"\b(saya telah mencoba|saya menguji|saya menggunakan|dalam pengujian saya|minggu lalu|bulan lalu|ketika saya mencoba)\b",
        re.I,
    ),
    "vi": re.compile(
        r"(tôi đã thử|tôi đã kiểm tra|tôi đã dùng|trong thử nghiệm của tôi|tuần trước|tháng trước|khi tôi thử)",
        re.I,
    ),
    "bn": re.compile(
        r"(আমি পরীক্ষা করেছি|আমি চেষ্টা করেছি|আমি ব্যবহার করেছি|আমার পরীক্ষায়|গত সপ্তাহে|গত মাসে|যখন আমি ব্যবহার করেছি)",
        re.I,
    ),
    "ur": re.compile(
        r"(میں نے آزمایا|میں نے ٹیسٹ کیا|میں نے استعمال کیا|میرے ٹیسٹ میں|پچھلے ہفتے|پچھلے مہینے|جب میں نے چلایا)",
        re.I,
    ),
    "uk": re.compile(
        r"\b(я протестував|я спробував|я використовував|у моїх тестах|минулого тижня|минулого місяця|коли я тестував)\b",
        re.I,
    ),
    "sv": re.compile(
        r"\b(jag testade|jag provade|jag använde|i mina tester|förra veckan|förra månaden|när jag testade)\b",
        re.I,
    ),
    "cs": re.compile(
        r"\b(testoval jsem|vyzkoušel jsem|použil jsem|v mých testech|minulý týden|minulý měsíc|když jsem testoval)\b",
        re.I,
    ),
    "ro": re.compile(
        r"\b(am testat|am încercat|am folosit|în testele mele|săptămâna trecută|luna trecută|când am testat)\b",
        re.I,
    ),
    "el": re.compile(
        r"(δοκίμασα|έλεγξα|χρησιμοποίησα|στις δοκιμές μου|την προηγούμενη εβδομάδα|τον προηγούμενο μήνα|όταν δοκίμασα)",
        re.I,
    ),
    "hu": re.compile(
        r"\b(teszteltem|kipróbáltam|használtam|a tesztjeim során|múlt héten|múlt hónapban|amikor kipróbáltam)\b",
        re.I,
    ),
    "da": re.compile(
        r"\b(jeg testede|jeg afprøvede|jeg brugte|i mine test|i sidste uge|i sidste måned|da jeg testede)\b",
        re.I,
    ),
    "fi": re.compile(
        r"\b(testasin|kokeilin|käytin|testeissäni|viime viikolla|viime kuussa|kun testasin)\b",
        re.I,
    ),
    "no": re.compile(
        r"\b(jeg testet|jeg prøvde|jeg brukte|i mine tester|forrige uke|forrige måned|da jeg testet)\b",
        re.I,
    ),
    "he": re.compile(
        r"(בדקתי|ניסיתי|השתמשתי|בבדיקות שלי|בשבוע שעבר|בחודש שעבר|כשבדקתי)",
        re.I,
    ),
    "th": re.compile(
        r"(ผมได้ทดสอบ|ฉันได้ลอง|ผมใช้|ในการทดสอบของผม|สัปดาห์ที่แล้ว|เดือนที่แล้ว|เมื่อผมได้ลอง)",
        re.I,
    ),
    "fa": re.compile(
        r"(من تست کردم|من امتحان کردم|من استفاده کردم|در آزمایش‌های من|هفته گذشته|ماه گذشته|وقتی امتحان کردم)",
        re.I,
    ),
    "ms": re.compile(
        r"\b(saya telah menguji|saya mencuba|saya menggunakan|dalam ujian saya|minggu lepas|bulan lepas|apabila saya cuba)\b",
        re.I,
    ),
    "tl": re.compile(
        r"\b(sinubukan ko|sinubok ko|ginamit ko|sa aking pagsubok|noong nakaraang linggo|noong nakaraang buwan|nang subukan ko)\b",
        re.I,
    ),
    "sw": re.compile(
        r"\b(nilijaribu|nilifanya majaribio|nilitumia|katika majaribio yangu|wiki iliyopita|mwezi uliopita|nilipojaribu)\b",
        re.I,
    ),
}

SPECIFIC_NUM = re.compile(
    r"\b\d+(?:\.\d+)?\s?(?:kb|mb|gb|seconds?|secs?|minutes?|mins?|hours?|%|percent|times|pixels?|px|dpi)\b",
    re.I,
)
RISKY_CLAIM = re.compile(
    r"(?:100%|\b(?:guarantee[sd]?|never leaves? your device|files never leave|"
    r"no data is (?:stored|collected|uploaded|saved)|completely (?:safe|private|secure)|"
    r"totally (?:safe|private|secure)|zero risk|always works?|nothing is uploaded|"
    r"never uploaded|never stored)\b)",
    re.I,
)
UNCONTRACTED = re.compile(
    r"\b(do not|does not|did not|is not|are not|was not|were not|cannot|can not|will not|"
    r"would not|should not|could not|it is|that is|you are|they are|we are|i am|i have|"
    r"there is|here is)\b",
    re.I,
)
CONTRACTED = re.compile(r"\b\w+(?:n't|'re|'ve|'ll|'m)\b|\b(?:it's|that's|there's|here's|let's)\b", re.I)

NOT_X_BUT_Y = [
    re.compile(
        r"\b(?:isn't|aren't|wasn't|not)\s+(?:just\s+|only\s+|about\s+)?[^.!?;,]{1,40}[,;]\s*"
        r"(?:it's|it is|they're|that's|but)\b",
        re.I,
    ),
    re.compile(r"\bnot only\b.{0,60}\bbut also\b", re.I),
    re.compile(r"\bno solo\b.{0,60}\bsino (?:también\b|que\b)", re.I),
    re.compile(r"\bnon seulement\b.{0,60}\bmais (?:aussi\b|encore\b)", re.I),
    re.compile(r"\bnicht nur\b.{0,60}\bsondern auch\b", re.I),
    re.compile(r"\bnon solo\b.{0,60}\bma anche\b", re.I),
    re.compile(r"\bnão (?:só|apenas)\b.{0,60}\bmas também\b", re.I),
    re.compile(r"\bnie tylko\b.{0,60}\bale (?:także\b|również\b)", re.I),
    re.compile(r"\bniet alleen\b.{0,60}\bmaar ook\b", re.I),
]

# Multilingual list of three with language-aware conjunction
THREE_LIST = re.compile(
    r"\b([\w]{3,15}), ([\w]{3,15}),? (?:and|y|et|und|e|aur|और|i|en|ve|dan|và|og|ja|och|és|și|kai|or|na) ([\w]{3,15})\b",
    re.I | re.UNICODE,
)

CONCLUSION_HEADING = re.compile(
    r"^(conclusion|final thoughts?|wrapping up|summary|bottom line|to sum up|in short|takeaways?|"
    r"final recommendation|faq|faqs|frequently asked|"
    r"conclusi[oó]n|conclusiones|en resumen|resumen|preguntas frecuentes|"
    r"fazit|zusammenfassung|h[aä]ufige fragen|"
    r"synth[eè]se|questions fr[eé]quentes|"
    r"conclusione|in sintesi|domande frequenti|"
    r"conclusão|em resumo|perguntas frequentes|"
    r"conclusie|samenvatting|veelgestelde vragen|"
    r"wnioski|podsumowanie|najczęściej zadawane pytania|"
    r"sonuç|özet|sıkça sorulan sorular|"
    r"заключение|выводы|итоги|резюме|"
    r"خاتمة|استنتاج|ملخص|الأسئلة الشائعة|"
    r"結論|まとめ|総括|要約|よくある質問|"
    r"结论|总结|结语|常见问题|"
    r"결론|요약|맺음말|자주 묻는 질문|"
    r"निष्कर्ष|सारांश|अंतिम विचार|"
    r"kesimpulan|ringkasan|pertanyaan yang sering diajukan|"
    r"kết luận|tóm lại|câu hỏi thường gặp|"
    r"উপসংহার|সারসংক্ষেপ|সাধারণ জিজ্ঞাসা|"
    r"خلاصہ|نتیجہ|عام سوالات|"
    r"висновок|підсумок|поширені запитання|"
    r"sammanfattning|slutsats|vanliga frågor|"
    r"závěr|shrnutí|často kladené otázky|"
    r"concluzie|rezumat|întrebări frecvente|"
    r"συμπέρασμα|σύνοψη|συχνές ερωτήσεις|"
    r"következtetés|összegzés|gyakran ismételt kérdések|"
    r"konklusion|opsummering|ofte stillede spørgsmål|"
    r"tiivistelmä|yhteenveto|usein kysytyt kysymykset|"
    r"konklusjon|sammendrag|ofte stilte spørsmål|"
    r"סיכום|מסקנה|שאלות נפוצות|"
    r"บทสรุป|สรุป|คำถามที่พบบ่อย|"
    r"نتیجه‌گیری|جمع‌بندی|پرسش‌های متداول|"
    r"buod|mga madalas itanong|"
    r"hitimisho|muhtasari|maswali ya mara kwa mara)\b",
    re.I,
)
PASSIVE_VOICE = re.compile(
    r"\b(?:is|are|was|were|been|being|be)\s+(?:\w+ly\s+)?(?:\w+ed|written|shown|seen|done|made|given|taken|known)\b",
    re.I,
)
TRANSITION_ANNOUNCE = re.compile(
    r"\b(?:let's talk about|let's move on|now let's|moving on to|"
    r"here's what you need|in this section|as mentioned|"
    r"let us now|let's now|let's explore|let's look at|"
    r"let's discuss|without further ado|having said that|"
    r"hablemos de|en esta secci[oó]n|ahora veamos|"
    r"parlons de|dans cette section|"
    r"sprechen wir [uü]ber|in diesem abschnitt|"
    r"parliamo di|in questa sezione|"
    r"vamos falar sobre|nesta seção|"
    r"laten we het hebben over|in deze sectie|"
    r"porozmawiajmy o|w tej sekcji|"
    r"davajte pogovorim|v etom razdele|"
    r"şimdi bahsedelim|bu bölümde|"
    r"について話しましょう|このセクションでは|"
    r"让我们来谈谈|在这一部分|"
    r"이제 이야기해 봅시다|이 섹션에서는|"
    r"دعونا نتحدث عن|في هذا القسم|"
    r"mari kita bahas|dalam bagian ini|"
    r"hãy cùng nói về|trong phần này|"
    r"চলুন আলোচনা করি|এই বিভাগে|"
    r"آئیے بات کرتے ہیں|اس حصے میں|"
    r"поговорімо про|у цьому розділі|"
    r"låt oss prata om|i det här avsnittet|"
    r"pojďme se bavit o|v této části|"
    r"să vorbim despre|în această secțiune|"
    r"ας μιλήσουμε για|σε αυτή την ενότητα|"
    r"beszéljünk a|ebben a részben|"
    r"lad os tale om|i dette afsnit|"
    r"puhutaanpa|tässä osiossa|"
    r"la oss snakke om|i denne delen|"
    r"בואו נדבר על|בסעיף זה|"
    r"เรามาพูดถึง|ในส่วนนี้|"
    r"بیایید درباره|در این بخش|"
    r"pag-usapan natin|sa bahaging ito|"
    r"tuzungumzie kuhusu|katika sehemu hii|"
    r"ab baat karte hain|is section mein)\b",
    re.I,
)

# Targeted clickbait patterns (avoids false-positive on legitimate tech terms like "secret management")
CLICKBAIT_HEADING = re.compile(
    r"\b(?:shocking|amazing|incredible|unbelievable|mind-?blowing|"
    r"you won't believe|nobody tells you|no one tells you|"
    r"everything you need to know|the truth about|what they don't want you to know|"
    r"the real reason why|one weird trick|game-?changer hack|"
    r"the secret (?:to|of|behind)|secret trick|secrets? revealed)\b",
    re.I,
)

# Wikipedia Signs of AI writing patterns
ONE_LINE_CLOSERS = re.compile(
    r"\b(?:let that sink in|read that again|that(?:'s| is) the real win|"
    r"that distinction matters|the old rules were gone|the takeaway is clear)\b",
    re.I,
)
ING_RIDERS = re.compile(
    r",\s+(?:ensuring|highlighting|showcasing|reflecting|underscoring|emphasizing|fostering|enabling)\b",
    re.I,
)
VAGUE_CONNECTION = re.compile(
    r"\b(?:serves as (?:a|an)|acts as (?:a|an)|stands as (?:a|an)|stands as a testament to|"
    r"plays a pivotal role in|plays a crucial role in)\b",
    re.I,
)
ARGUING_NO_ONE = re.compile(
    r"\b(?:i'm not saying|don't get me wrong|this isn't to say|this is not to say|"
    r"one might be tempted to|a tempting approach would be)\b",
    re.I,
)
META_DOC_TALK = re.compile(
    r"\b(?:in this (?:article|guide|post|tutorial),? (?:we will|we'll|we explore|we discuss)|"
    r"this (?:article|guide|post) (?:will explore|covers|aims to))\b",
    re.I,
)

# Verbose multi-word filler patterns (say in one word what AI wraps in six)
VERBOSE_FILLERS = re.compile(
    r"\b(?:due to the fact that|in the event that|has the ability to|"
    r"has the capacity to|for the purpose of|with regard to|with respect to|"
    r"in light of the fact that|prior to the event|subsequent to the event)\b",
    re.I,
)

# StoryScope discourse-level structural patterns
STATED_LESSON = re.compile(
    r"\b(?:the (?:lesson|takeaway|moral) (?:here )?is|what this means for you|"
    r"if you take (?:only )?one thing|moral of the story|and that'?s (?:the point|the whole point)|"
    r"the bottom line is)\b",
    re.I,
)
TIDY_CLOSER = re.compile(
    r"\b(?:at the end of the day|in the end,? we see|looking back on this|"
    r"the future looks bright|brings us full circle)\b",
    re.I,
)
VAGUE_ALLUSION = re.compile(
    r"\b(?:experts?|researchers?|scientists|professionals)\s+(?:say|agree|believe|argue|warn|suggest)\b|"
    r"\b(?:studies|research)\s+(?:show|shows|suggests?|indicates?|have shown)\b",
    re.I,
)
EMBODIED_EMOTION = re.compile(
    r"\b(?:breath (?:caught|hitched|stalled)|caught (?:my|his|her|their) breath|"
    r"blood ran cold|swallowed hard|knot in (?:my|his|her|their) stomach)\b",
    re.I,
)


def norm(s):
    return s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')


def get_available_languages():
    """Discover available language codes from banned-phrases-*.txt in references."""
    langs = {"en"}
    if REFS_DIR.exists():
        for f in REFS_DIR.glob("banned-phrases-*.txt"):
            code = f.stem.replace("banned-phrases-", "").lower()
            if code:
                langs.add(code)
    return sorted(langs)


def load_phrases(lang="en"):
    """Load banned phrases for the specified language."""
    phrase_file = REFS_DIR / "banned-phrases.txt"
    if lang != "en":
        lang_file = REFS_DIR / f"banned-phrases-{lang}.txt"
        if lang_file.exists():
            phrase_file = lang_file

    hard, soft, cur = [], [], None
    if phrase_file.exists():
        for raw in phrase_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            low = line.lower()
            if low == "[hard]":
                cur = hard
            elif low == "[soft]":
                cur = soft
            elif cur is not None:
                cur.append(norm(low))

    return hard, soft


def phrase_regex(p):
    esc = re.escape(p)
    # single words also match endings (navigate -> navigating); phrases match exactly
    if " " not in p and "-" not in p:
        return re.compile(r"\b" + esc + r"\w*", re.I)
    return re.compile(r"\b" + esc + r"\b", re.I)


def sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    return [s for s in SENT_SPLIT.split(text) if s]


def words(text):
    return WORD.findall(text)


def parse(lines):
    """Return list of sections: dict(heading, start_line, body_lines[(no, text)]).

    Handles code blocks properly by not classifying code lines as prose.
    """
    sections = [{"heading": None, "line": 1, "body": []}]  # index 0 = intro
    h1_count = 0
    deep = []
    in_code_block = False

    for i, raw in enumerate(lines, 1):
        s = raw.rstrip()

        if s.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        if re.match(r"^#\s+", s):
            h1_count += 1
            continue
        if re.match(r"^##\s+", s):
            clean_head = re.sub(r"^##\s+", "", s).strip()
            sections.append({"heading": clean_head, "line": i, "body": []})
            continue
        if re.match(r"^#{3,}\s+", s):
            deep.append(i)
            continue
        if s.strip() and not re.match(r"^\s*-{3,}\s*$", s):
            sections[-1]["body"].append((i, s))

    return sections, h1_count, deep


def check_section_variance(body_sections):
    """Check if all sections are suspiciously similar in length (mechanical feel)."""
    issues = []
    if len(body_sections) < 3:
        return issues

    section_word_counts = []
    for sec in body_sections:
        sec_text = " ".join(t for _, t in sec["body"])
        wc = len(words(sec_text))
        section_word_counts.append(wc)

    if not section_word_counts or max(section_word_counts) == 0:
        return issues

    avg = statistics.mean(section_word_counts)
    if avg == 0:
        return issues

    # Coefficient of variation: stdev / mean
    if len(section_word_counts) >= 2:
        stdev = statistics.stdev(section_word_counts)
        cv = stdev / avg if avg > 0 else 0
        if cv < 0.15:
            counts_str = ", ".join(str(c) for c in section_word_counts)
            issues.append(
                f"sections are very similar in length ({counts_str} words), "
                f"vary them to avoid mechanical feel"
            )

    return issues


def check_opinion_variety(body_sections, opinion_re):
    """Check if the same opinion phrase is used repeatedly."""
    issues = []
    opinion_phrases = []
    for sec in body_sections:
        sec_text = " ".join(t for _, t in sec["body"])
        found = opinion_re.findall(sec_text)
        opinion_phrases.extend(f.lower() if isinstance(f, str) else f[0].lower() for f in found)

    if len(opinion_phrases) >= 3:
        counts = Counter(opinion_phrases)
        for phrase, count in counts.most_common(3):
            if count >= 3:
                issues.append(
                    f'opinion phrase "{phrase}" used {count} times, vary the wording'
                )

    return issues


def main():
    avail_langs = get_available_languages()
    epilog_text = (
        f"Built-in language packs: {', '.join(avail_langs)}. "
        f"You can also pass any other language code; custom files are loaded from references/banned-phrases-<lang>.txt."
    )

    ap = argparse.ArgumentParser(
        description="Lint a markdown article against the human-article-writer rules.",
        epilog=epilog_text,
    )
    ap.add_argument("file", help='Path to markdown file, or "-" for stdin')
    ap.add_argument("--target", type=int, default=900, help="Target word count (default: 900)")
    ap.add_argument("--tolerance", type=float, default=0.15, help="Word count tolerance as fraction (default: 0.15)")
    ap.add_argument("--tool", default="", help="Tool name to check mention frequency")
    ap.add_argument("--max-tool", type=int, default=3, help="Max tool mentions allowed (default: 3)")
    ap.add_argument("--no-notes", action="store_true", help="Treat claimed-experience phrases as hard failures")
    ap.add_argument("--lang", default="en", help=f"Article language code (e.g. {', '.join(avail_langs)}, default: en)")
    ap.add_argument("--strict", action="store_true", help="Exit code 1 on any CHECK warning as well as FIX errors")
    ap.add_argument("--json", action="store_true", help="Output results as JSON")
    a = ap.parse_args()

    lang = a.lang.lower()

    try:
        text = sys.stdin.read() if a.file == "-" else pathlib.Path(a.file).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: File not found: {a.file}", file=sys.stderr)
        sys.exit(2)
    except PermissionError:
        print(f"Error: Permission denied: {a.file}", file=sys.stderr)
        sys.exit(2)

    ntext = norm(text)
    lines = ntext.splitlines()
    sections, h1_count, deep = parse(lines)

    fixes, checks, infos = [], [], []

    # ---- phrases, dashes, formatting (prose lines only, skip code blocks) ----
    hard, soft = load_phrases(lang)
    hard_re = [(p, phrase_regex(p)) for p in hard]
    soft_re = [(p, phrase_regex(p)) for p in soft]

    in_code_block = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip formatting checks inside code blocks
        if in_code_block:
            continue

        for p, rx in hard_re:
            if rx.search(line):
                fixes.append(f'line {i}: banned phrase "{p}"')
        for p, rx in soft_re:
            if rx.search(line):
                checks.append(f'line {i}: filler/corporate word "{p}" (rewrite unless it is really the right word)')
        if "\u2014" in line or re.search(r"\s\u2013\s", line) or re.search(r"\s--\s", line):
            fixes.append(f"line {i}: em dash or spaced dash, use a comma or full stop")
        if re.match(r"^\s*[-*+\u2022]\s+\S", line):
            fixes.append(f"line {i}: bullet point, use plain paragraphs")
        if re.match(r"^\s*\d+[.)]\s+\S", line):
            fixes.append(f"line {i}: numbered list, write steps as prose")
        if re.search(r"\*\*[^*]+\*\*|__[^_]+__", line):
            fixes.append(f"line {i}: bold text, remove emphasis")
        if re.match(r"^\s*\|", line):
            fixes.append(f"line {i}: table row, produce tables separately")
        for m in RISKY_CLAIM.finditer(line):
            checks.append(f'line {i}: absolute claim "{m.group(0)}", only keep it if the user verified it')
        # Transition/announcing phrases
        for m in TRANSITION_ANNOUNCE.finditer(line):
            checks.append(f'line {i}: transition/announcing phrase "{m.group(0)}", just start the topic directly')

    for i in deep:
        checks.append(f"line {i}: H3 or deeper heading, use H2 only")
    if h1_count > 1:
        checks.append(f"{h1_count} H1 headings found, expected 1 title")

    # ---- heading quality ----
    body_sections = sections[1:]
    for sec in body_sections:
        head = sec["heading"]
        if head:
            # Strip leading numbers, bullets, emoji before checking conclusion patterns
            clean_head = re.sub(r"^[\d\.\-\s\u2000-\u3300]+", "", head).strip()
            if CONCLUSION_HEADING.match(clean_head.lower()):
                fixes.append(f'line {sec["line"]}: heading "{head}" reads like a conclusion/FAQ, make it a normal topic section')
            if CLICKBAIT_HEADING.search(head):
                checks.append(
                    f'line {sec["line"]}: heading "{head}" sounds clickbaity, keep headings plain and descriptive'
                )

    # ---- structure ----
    if not body_sections:
        fixes.append("no H2 sections found")
    intro_text = " ".join(t for _, t in sections[0]["body"])
    intro_sents = sentences(intro_text)
    if not intro_sents:
        fixes.append("no opening review before the first H2")
    elif len(intro_sents) > 3:
        checks.append(f"opening review has {len(intro_sents)} sentences, aim for 1 to 2")

    for sec in body_sections:
        head = sec["heading"]
        sec_text = " ".join(t for _, t in sec["body"])
        sents = sentences(sec_text)
        if not sents:
            checks.append(f'line {sec["line"]}: section "{head}" is empty')
            continue
        if sents[0].rstrip().endswith("?"):
            fixes.append(f'line {sec["line"]}: section "{head}" opens with a question')
        if len(words(sents[-1])) <= 5 and len(sents) > 2:
            checks.append(f'line {sec["body"][-1][0]}: section "{head}" ends on a very short line ("{sents[-1][:40]}"), check it is not a punchy wrap-up')

    # ---- section length variance ----
    variance_issues = check_section_variance(body_sections)
    checks.extend(variance_issues)

    # ---- length ----
    body_text = " ".join(t for s in sections for _, t in s["body"])
    wc = len(words(body_text))
    lo, hi = int(a.target * (1 - a.tolerance)), int(a.target * (1 + a.tolerance))
    if wc < lo:
        checks.append(f"length: {wc} words, below {lo} (target {a.target}), expand with practical detail")
    elif wc > hi:
        checks.append(f"length: {wc} words, above {hi} (target {a.target}), trim repetition")

    # ---- rhythm and voice ----
    all_sents = sentences(body_text)
    avg = 0.0
    short_ratio = 0.0
    if all_sents:
        lens = [len(words(s)) for s in all_sents]
        avg = sum(lens) / len(lens)
        short_ratio = sum(1 for n in lens if n <= 8) / len(lens)
        spread = max(lens) - min(lens) if lens else 0
        mid_band_ratio = sum(1 for n in lens if 10 <= n <= 20) / len(lens)
        if avg > 17:
            checks.append(f"average sentence length is {avg:.1f} words, aim for under 17 with a mix of short ones")
        if short_ratio < 0.25:
            checks.append(f"only {short_ratio:.0%} of sentences are 8 words or fewer, add more short ones")
        if len(lens) >= 10 and spread < 14:
            checks.append(f"low sentence length spread ({spread} words delta between longest and shortest), alternate punchy and unfolded sentences")
        if len(lens) >= 12 and mid_band_ratio > 0.70:
            checks.append(f"{mid_band_ratio:.0%} of sentences are clustered in the 10-20 word mid-band, break rhythm with shorter and longer counterweights")
        run, prev = 1, None
        for s in all_sents:
            first = (words(s) or [""])[0].lower()
            if first and first == prev:
                run += 1
                if run == 3:
                    checks.append(f'three sentences in a row start with "{first}"')
            else:
                run = 1
            prev = first

    # ---- passive voice (English only) ----
    if lang == "en":
        passive_matches = PASSIVE_VOICE.findall(body_text)
        passive_count = len(passive_matches)
        total_sents = len(all_sents) if all_sents else 1
        passive_ratio = passive_count / total_sents
        if passive_ratio > 0.3:
            checks.append(
                f"high passive voice ratio ({passive_count} passive constructions in {total_sents} sentences), "
                f"use more active voice for a natural feel"
            )

    # ---- contractions (English only) ----
    if lang == "en":
        unc = UNCONTRACTED.findall(body_text)
        con = CONTRACTED.findall(body_text)
        if len(unc) >= 4 and len(unc) > 0.5 * max(len(con), 1):
            ex = ", ".join(sorted({u.lower() for u in unc})[:5])
            checks.append(f"{len(unc)} uncontracted phrases vs {len(con)} contractions (e.g. {ex}), use more contractions")

    kinda = len(re.findall(r"\b(gonna|kinda)\b", body_text, re.I))
    if kinda > 2:
        checks.append(f'"gonna/kinda" used {kinda} times, keep it to once or twice')

    # ---- opinions ----
    opinion_re = OPINION_PATTERNS.get(lang)
    if opinion_re:
        no_opinion = [s["heading"] for s in body_sections if not opinion_re.search(" ".join(t for _, t in s["body"]))]
        if body_sections and len(no_opinion) > len(body_sections) / 2:
            checks.append(f"{len(no_opinion)} of {len(body_sections)} sections have no personal comment, add small opinions to most sections")
        opinion_variety_issues = check_opinion_variety(body_sections, opinion_re)
        checks.extend(opinion_variety_issues)

    if lang == "en":
        n_think = len(re.findall(r"\bi think\b", body_text, re.I))
        if n_think > 3:
            checks.append(f'"I think" appears {n_think} times, vary the wording')

    # ---- patterns ----
    for rx in NOT_X_BUT_Y:
        for m in rx.finditer(body_text):
            checks.append(f'possible "not X but Y" pattern: "{m.group(0)[:70]}"')
    threes = THREE_LIST.findall(body_text)
    for t in threes[:8]:
        checks.append(f'possible list of three: "{t[0]}, {t[1]} and {t[2]}" (ignore if they are nouns or steps)')

    # ---- Wikipedia Signs of AI writing patterns ----
    for m in ONE_LINE_CLOSERS.finditer(body_text):
        fixes.append(f'AI one-line closer: "{m.group(0)}" (remove or integrate into previous sentence)')
    for m in ING_RIDERS.finditer(body_text):
        checks.append(f'shallow -ing participle rider: "{m.group(0)}" (state consequence directly)')
    for m in VAGUE_CONNECTION.finditer(body_text):
        checks.append(f'vague connection phrase: "{m.group(0)}" (use direct verbs like is, has, helps)')
    for m in ARGUING_NO_ONE.finditer(body_text):
        checks.append(f'arguing with phantom objection: "{m.group(0)}" (state the point directly)')
    for m in META_DOC_TALK.finditer(body_text):
        checks.append(f'document meta-talk: "{m.group(0)}" (focus on the subject, not the document)')
    for m in VERBOSE_FILLERS.finditer(body_text):
        checks.append(f'verbose multi-word filler: "{m.group(0)}" (use single direct word: because, if, can, etc.)')

    # ---- StoryScope discourse and structural patterns ----
    for m in STATED_LESSON.finditer(body_text):
        checks.append(f'stated lesson/moralizing: "{m.group(0)}" (let the technical details make the point)')
    for m in TIDY_CLOSER.finditer(body_text):
        checks.append(f'tidy wrap-up cliché: "{m.group(0)}" (end on a concrete technical fact, not a philosophical bow)')
    for m in VAGUE_ALLUSION.finditer(body_text):
        checks.append(f'unnamed authority claim: "{m.group(0)}" (name the specific tool or author, or state as direct fact)')
    for m in EMBODIED_EMOTION.finditer(body_text):
        checks.append(f'embodied emotion cliché: "{m.group(0)}" (state the technical situation plainly)')

    # ---- heading echo in opening sentence ----
    for s in body_sections:
        h = s["heading"].lower().strip()
        body_sents = sentences(" ".join(t for _, t in s["body"]))
        if body_sents:
            first_s = body_sents[0].lower()
            h_words = [w for w in words(h) if len(w) > 3]
            if len(h_words) >= 3 and all(w in first_s for w in h_words):
                checks.append(f'heading echoed in opening sentence of section "{s["heading"]}" (dive straight into detail)')

    # ---- experience / numbers ----
    exp_re = EXPERIENCE_PATTERNS.get(lang, EXPERIENCE_PATTERNS["en"] if lang == "en" else None)
    if exp_re:
        exp = exp_re.findall(body_text)
        if exp:
            flat_exp = []
            for e in exp:
                flat_exp.append(e.lower() if isinstance(e, str) else e[0].lower())
            msg = "claimed first-hand experience: " + "; ".join(sorted(set(flat_exp))[:6])
            if a.no_notes:
                fixes.append(msg + " (no real notes were given, rewrite as a general opinion)")
            else:
                infos.append(msg + " (confirm each matches the user's notes)")
    nums = SPECIFIC_NUM.findall(body_text)
    if nums:
        msg = "specific numbers: " + ", ".join(sorted({n.lower() for n in nums})[:10])
        if a.no_notes:
            checks.append(msg + " (each must come from the outline or be labelled a starting point)")
        else:
            infos.append(msg + " (confirm they match the user's notes or outline)")

    # ---- tool mentions ----
    if a.tool:
        tc = len(re.findall(re.escape(a.tool), body_text, re.I))
        if tc > a.max_tool:
            checks.append(f'"{a.tool}" mentioned {tc} times, keep it to once or twice where it fits')
        elif tc == 0:
            infos.append(f'"{a.tool}" is not mentioned')

    # ---- exit code determination ----
    has_failed = bool(fixes) or (a.strict and bool(checks))

    # ---- JSON output ----
    if a.json:
        result = {
            "file": a.file,
            "stats": {
                "words": wc,
                "target": a.target,
                "sections": len(body_sections),
                "avg_sentence_length": round(avg, 1) if all_sents else None,
                "short_sentence_ratio": round(short_ratio, 2) if all_sents else None,
                "gonna_kinda": kinda,
                "language": lang,
            },
            "fix": fixes,
            "check": checks,
            "info": infos,
            "passed": not has_failed,
        }
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1 if has_failed else 0)

    # ---- report ----
    print(f"=== Article check: {a.file} ===")
    print(f"Words: {wc} (target {a.target}) | H2 sections: {len(body_sections)} | gonna/kinda: {kinda} | lang: {lang}")
    if all_sents:
        print(f"Avg sentence: {avg:.1f} words | short sentences: {short_ratio:.0%}")
    print()

    def dump(title, items, cap=25):
        if not items:
            return
        print(f"{title} ({len(items)})")
        for it in items[:cap]:
            print(f"  - {it}")
        if len(items) > cap:
            print(f"  ... and {len(items) - cap} more")
        print()

    dump("FIX (must change)", fixes)
    dump("CHECK (look and decide)", checks)
    dump("INFO", infos)
    if not fixes and not checks:
        print("Clean. Do the self-review pass in references/voice-guide.md, then deliver.")
    sys.exit(1 if has_failed else 0)


if __name__ == "__main__":
    main()
