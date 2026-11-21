# -*- coding: utf-8 -*-
"""Screenplay: "300 Spartalıdan Biri Olsaydın Ne Olurdu?"

Each scene is a list of beats. A Line is spoken by a character (TTS), a Pause is
silent screen time (used for action / battle moments). Scene timing is derived
from the real length of the synthesized voice lines, so picture, voice, music
and subtitles always stay in sync.

`text` is what appears in the subtitles, `say` (optional) is what the TTS reads
(numbers written out as words etc.).

Historical sources behind the lines: Herodotus, Histories VII (scout & hair
combing 7.208-209, four days of waiting 7.210, Medes & Immortals 7.210-211,
feigned retreat 7.211, Xerxes leaping from his throne 7.212, Ephialtes
7.213-218, last day 7.219-225, Dienekes 7.226, Aristodemos 7.229-231 / 9.71);
Plutarch, Lycurgus 16-17 (infant inspection, agoge, reeds of the Eurotas,
stealing food) and Sayings of the Spartans / Spartan Women ("Molon labe",
"with your shield or on it"); Athenaeus IV (the black broth joke).
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Line:
    spk: str
    text: str
    say: Optional[str] = None
    gap: float = 0.35          # silence after the line
    tag: Optional[str] = None


@dataclass
class Pause:
    dur: float
    tag: Optional[str] = None


@dataclass
class Scene:
    id: str
    music: str
    beats: list
    chapter: Optional[str] = None   # chapter card shown at scene start
    lead: float = 0.5               # silence before first beat
    tail: float = 0.5               # silence after last beat


# Speaker -> display name for name tags / subtitles colour
SPEAKERS = {
    "N":   ("Anlatıcı", None),
    "LEO": ("Kral Leonidas", "#ffd166"),
    "XER": ("Kral Kserkses", "#d9a8ff"),
    "DIE": ("Dienekes", "#ffb38a"),
    "SOL": ("Asker", "#bfe3ff"),
    "ELD": ("Yaşlı", "#e8e0c8"),
    "TRN": ("Eğitmen", "#ffb38a"),
    "GST": ("Misafir", "#c8f7a8"),
    "MOM": ("Annen", "#ffc2d6"),
    "SCT": ("Pers Casusu", "#ffe08a"),
    "DEM": ("Demaratos", "#bfe3ff"),
    "HER": ("Pers Habercisi", "#ffe08a"),
    "EPH": ("Efialtes", "#c8f7a8"),
    "GRK": ("Gözcü", "#bfe3ff"),
    "SPA": ("Spartalı", "#ffb38a"),
    "SEN": ("Sen", "#ff8a8a"),
}

SCENES = [
    # ------------------------------------------------------------------ COLD OPEN
    Scene("cold_open", "tension", [
        Pause(2.2, tag="fadein"),
        Line("N", "M.Ö. 480. Termopil Geçidi.",
             say="Milattan önce dört yüz seksen. Termopil geçidi.", gap=0.6),
        Line("N", "Gökyüzü bir anda karardı.", gap=0.3, tag="dark"),
        Line("N", "Bu bir bulut değildi. Bu, binlerce Pers okuydu.", gap=0.2, tag="arrows"),
        Line("SOL", "Okları güneşi kapatacak kadar çok!", gap=0.25, tag="sol"),
        Line("DIE", "Daha iyi. Gölgede savaşırız.", gap=0.3, tag="die"),
        Pause(3.0, tag="impact"),
    ], lead=0.0, tail=0.3),

    Scene("title", "title", [
        Pause(1.2, tag="logo"),
        Line("N", "Peki sen o üç yüz kişiden biri olsaydın?",
             say="Peki, sen o üç yüz kişiden biri olsaydın?", gap=0.3),
        Line("N", "Doğduğun günden o geçitteki son sabaha kadar, hayatın nasıl olurdu?",
             gap=0.3),
        Line("N", "Hadi, zamanı kıralım.", gap=0.6, tag="break"),
        Pause(1.2),
    ], lead=0.2, tail=0.2),

    # ------------------------------------------------------------------ BIRTH
    Scene("birth", "sparta", [
        Line("N", "Sparta'da doğdun. Ama gözlerini açtığın an, ilk sınavın başladı bile."),
        Line("N", "Plutarkhos'a göre baban seni yaşlıların önüne götürdü. "
                  "Yaşlılar seni evirip çevirip inceledi.", tag="inspect"),
        Line("ELD", "Sağlıklı, güçlü bir çocuk. Yaşayacak!", gap=0.5, tag="verdict"),
        Line("N", "Zayıf ya da hastalıklı görünseydin, Taygetos Dağı'nın eteklerindeki "
                  "bir uçuruma bırakılabilirdin.", tag="cliff"),
        Line("N", "Gerçi bazı modern araştırmacılar, bu anlatının abartılı olabileceğini söylüyor.",
             gap=0.6),
    ], chapter="I. DOĞUM"),

    # ------------------------------------------------------------------ AGOGE
    Scene("agoge", "training", [
        Line("N", "Yedi yaşına geldiğinde seni annenin kucağından aldılar. "
                  "Artık devletin askeriydin.", tag="taken"),
        Line("N", "Bu sert eğitimin adı agoge'ydi.", say="Bu sert eğitimin adı, agoge idi.",
             gap=0.5),
        Line("N", "Saçların kazındı. Ayakkabı yasaktı. "
                  "Taşların üstünde yalınayak koşarak sertleşecektin.", tag="run"),
        Line("N", "Yaz kış, yılda sadece tek bir pelerin.", gap=0.4),
        Line("N", "Yatağını, Eurotas Nehri'nin kıyısındaki sazlardan, "
                  "bıçak kullanmadan kendi ellerinle koparıp yapardın.", tag="reeds"),
        Line("N", "Yemek bilerek az verilirdi. Çünkü senden yiyeceğini çalmayı öğrenmen beklenirdi.",
             tag="steal"),
        Line("TRN", "Çalmak suç değil. Yakalanmak suç!", gap=0.4, tag="caught"),
        Line("N", "Yakalanırsan, hırsızlık yaptığın için değil, "
                  "beceriksiz olduğun için dayak yerdin.", gap=0.6),
    ], chapter="II. AGOGE"),

    # ------------------------------------------------------------------ ADULT LIFE
    Scene("mess", "comic", [
        Line("N", "Yirmi yaşında artık tam bir askerdin. Evlensen bile, otuz yaşına kadar "
                  "geceleri kışlada arkadaşlarınla kalırdın."),
        Line("N", "Her akşam ortak sofrada yerdin. Menüde meşhur kara çorba vardı: "
                  "domuz eti, kan, sirke ve tuz.", tag="soup"),
        Line("N", "Sofraya konuk olan bir yabancı, çorbadan bir kaşık aldı ve...", gap=0.2,
             tag="taste"),
        Pause(0.9, tag="gag"),
        Line("GST", "Iyy! Spartalıların ölümden neden korkmadığını şimdi anladım!",
             say="Iyyy! Spartalıların ölümden neden korkmadığını, şimdi anladım!", gap=0.6,
             tag="joke"),
        Line("N", "Bütün hayatın, tek bir şey için hazırlanıyordu: savaş.", gap=0.6, tag="war"),
    ], chapter="III. SPARTALI HAYATI"),

    # ------------------------------------------------------------------ PERSIAN THREAT
    Scene("persia", "persian", [
        Line("N", "M.Ö. 480 yılında, dünyanın en büyük imparatorluğunun hükümdarı, "
                  "Pers Kralı Kserkses, Yunanistan'ı ele geçirmek için yola çıktı.",
             say="Milattan önce dört yüz seksen yılında, dünyanın en büyük imparatorluğunun "
                 "hükümdarı, Pers Kralı Kserkses, Yunanistan'ı ele geçirmek için yola çıktı.",
             tag="king"),
        Line("XER", "Babamın yarım bıraktığı işi ben bitireceğim. Bütün Yunanistan diz çökecek!",
             gap=0.5, tag="xer"),
        Line("N", "Ordusu, Çanakkale Boğazı'nı gemilerden yapılmış köprülerle geçti.",
             tag="bridge"),
        Line("N", "Tarihçi Herodot, bu ordunun milyonlarca kişi olduğunu yazar. "
                  "Modern tarihçiler ise yüz bin ile üç yüz bin arası bir sayı tahmin ediyor.",
             tag="count"),
        Line("N", "Yine de bu, Yunanların o güne kadar gördüğü en büyük orduydu.", gap=0.6),
    ], chapter="IV. PERS TEHDİDİ"),

    # ------------------------------------------------------------------ THE 300
    Scene("chosen", "solemn", [
        Line("N", "Ama Sparta'da kutsal Karneia bayramı vardı. "
                  "Bayram bitmeden ordunun tamamı savaşa çıkamazdı."),
        Line("N", "Bu yüzden Kral Leonidas, yanına sadece üç yüz seçkin asker aldı.",
             tag="leo"),
        Line("N", "Hepsinin geride bırakacağı birer oğlu vardı. Soyları sürsün diye.",
             tag="sons"),
        Line("N", "Ve sen de onlardan birisin.", gap=0.5, tag="you"),
        Line("LEO", "Hazır olun. Kuzeye yürüyoruz!", gap=0.6, tag="ready"),
        Line("N", "Yola çıkmadan önce annen kalkanını eline verdi ve "
                  "Spartalı kadınların o meşhur sözünü söyledi.", tag="mom"),
        Line("MOM", "Ya kalkanınla dön, ya da kalkanının üstünde.", gap=0.9, tag="shield"),
    ], chapter="V. SEÇİLMİŞ 300"),

    # ------------------------------------------------------------------ MARCH & PASS
    Scene("march", "march", [
        Line("N", "Yolda başka Yunan şehirlerinden askerler de size katıldı."),
        Line("N", "Yani aslında orada sadece üç yüz kişi yoktunuz. "
                  "Toplamda yaklaşık yedi bin Yunan askeri vardı.", tag="7000"),
    ], chapter="VI. TERMOPİL"),

    Scene("pass", "march", [
        Line("N", "Hedef, Termopil Geçidi'ydi. Bir yanda sarp dağlar, öbür yanda deniz.",
             tag="geo"),
        Line("N", "En dar yerinde, ancak tek bir arabanın geçebileceği kadar dar bir yol.",
             tag="narrow"),
        Line("N", "Burada sayının önemi yoktu. Dar geçitte, Persler kalabalıklarını kullanamazdı.",
             tag="numbers"),
        Line("N", "Eski bir taş duvarı onardınız ve beklemeye başladınız.", gap=0.6, tag="wall"),
    ]),

    # ------------------------------------------------------------------ WAITING
    Scene("scout", "persian", [
        Line("N", "Kserkses, geçide bir casus gönderdi. Casus, gördüklerine inanamadı."),
        Line("SCT", "Kralım! Spartalılar spor yapıyor... ve saçlarını tarıyorlar!",
             gap=0.3, tag="scout"),
        Line("XER", "Ha ha ha! Bunlar savaşa mı gelmiş, düğüne mi?",
             say="Ha ha ha! Bunlar savaşa mı gelmiş, düğüne mi?", gap=0.4, tag="laugh"),
        Line("N", "Ama yanındaki sürgün Spartalı kral Demaratos onu uyardı.", tag="dem"),
        Line("DEM", "Kralım, Spartalılar canlarını ortaya koymadan önce saçlarını tarar. "
                    "Bu adamlar sonuna kadar savaşacak.", gap=0.6, tag="warn"),
    ]),

    Scene("molon", "tension", [
        Line("N", "Kserkses dört gün bekledi. Sonra silahlarınızı teslim etmenizi istedi."),
        Line("HER", "Büyük Kral Kserkses emrediyor: Silahlarınızı bırakın!", gap=0.5,
             tag="herald"),
        Pause(0.6),
        Line("LEO", "Gel de al!", gap=0.7, tag="molon"),
        Line("N", "Antik Yunanca söylenişiyle: Molon labe.",
             say="Antik Yunanca söylenişiyle, Molon labe.", gap=0.8),
    ]),

    # ------------------------------------------------------------------ DAY ONE
    Scene("day1", "battle", [
        Line("N", "Beşinci gün savaş başladı. İlk dalgada Med askerleri üzerinize yürüdü.",
             tag="charge"),
        Pause(2.6, tag="clash"),
        Line("N", "Kalkanları birbirine kenetlediniz. Bu düzenin adı falankstı.",
             tag="phalanx"),
        Line("N", "Senin kalkanın, solundaki arkadaşını korurdu.", tag="left"),
        Line("N", "Mızrağın onlarınkinden uzun, zırhın daha ağırdı. "
                  "Persler hasır kalkanlarla dalga dalga geldi, ama o duvarı aşamadı.",
             tag="waves"),
        Pause(2.0, tag="fight2"),
    ], chapter="VII. SAVAŞ BAŞLIYOR"),

    Scene("immortals", "battle", [
        Line("N", "Sonra Kserkses en seçkin birliğini gönderdi.", tag="send"),
        Line("XER", "Ölümsüzler! Şu inatçıları ezin!", gap=0.4, tag="order"),
        Line("N", "On bin kişilik Ölümsüzler! Ama onlar da geçidi aşamadı.", tag="clash"),
        Line("N", "Spartalılar bir hile yaptı. Kaçıyormuş gibi geri çekildiler.",
             tag="feign"),
        Line("N", "Persler düzenlerini bozup peşlerinden koşunca...", gap=0.1, tag="chase"),
        Line("LEO", "Şimdi! Dönün!", gap=0.3, tag="turn"),
        Pause(2.4, tag="counter"),
        Line("N", "Herodot'a göre Kserkses, ordusunun bu hâlini görünce "
                  "korkuyla üç kez tahtından fırladı.", tag="throne"),
        Line("XER", "Bu nasıl olur?!", gap=0.6, tag="xer"),
        Line("N", "İkinci gün de aynısı oldu. Geçit tutuldu. "
                  "Yorgundun, yaralıydın, ama hayattaydın.", gap=0.7, tag="day2"),
    ]),

    # ------------------------------------------------------------------ BETRAYAL
    Scene("betrayal", "night", [
        Line("N", "Ama sonra, her şeyi değiştiren bir hain çıktı. "
                  "Malisli bir yerli olan Efialtes.", tag="eph"),
        Line("EPH", "Kralım... Dağlardan geçen gizli bir patika biliyorum. "
                    "Ödülümü verirseniz, sizi Spartalıların arkasına çıkarırım.",
             gap=0.4, tag="offer"),
        Line("XER", "Altınlar senin. Ölümsüzler, yola çıkın!", gap=0.5, tag="gold"),
        Line("N", "Ölümsüzler gece boyunca, meşalelerle dağ yolunu tırmandı.", tag="climb"),
        Line("N", "Patikayı koruyan Fokisli askerler tepeye çekildi. Yol açık kaldı.",
             gap=0.7, tag="open"),
    ], chapter="VIII. İHANET"),

    # ------------------------------------------------------------------ LAST MORNING
    Scene("morning", "solemn", [
        Line("N", "Şafak sökerken gözcüler koşarak geldi.", tag="run"),
        Line("GRK", "Kralım! Persler dağı aştı! Arkamızdan geliyorlar!", gap=0.4, tag="news"),
        Line("N", "Kuşatılmıştınız. Leonidas müttefik askerlerin çoğunu geri gönderdi.",
             tag="leave"),
        Line("N", "Ama Spartalılar çekilmeyecekti. Yedi yüz Thespiaili de "
                  "kendi isteğiyle sizinle kaldı.", tag="stay"),
        Line("N", "Sen de kaçabilirdin. Ama bir Spartalı için savaştan kaçmak, "
                  "ölmekten daha büyük bir utançtı.", tag="you"),
        Line("SEN", "Ben kalıyorum.", gap=0.6, tag="stay2"),
        Line("LEO", "Kahvaltınızı iyi yapın beyler. Akşam yemeğini Hades'te yiyeceğiz!",
             gap=1.0, tag="breakfast"),
    ], chapter="IX. SON SABAH"),

    # ------------------------------------------------------------------ FINAL BATTLE
    Scene("final", "final", [
        Line("N", "Bu kez duvarın arkasında beklemediniz. "
                  "Geçidin geniş kısmına çıkıp, Perslerin üstüne yürüdünüz.", tag="advance"),
        Pause(2.4, tag="clash"),
        Line("N", "Mızraklar kırıldı. Kılıçlara sarıldınız.", tag="swords"),
        Line("N", "Savaşın ortasında, Kral Leonidas düştü.", gap=0.3, tag="leofall"),
        Line("SPA", "Kral düştü! Kralı koruyun!", gap=0.3, tag="protect"),
        Line("N", "Onun bedenini geri almak için dört kez saldırdınız ve sonunda "
                  "Persleri geri püskürttünüz.", tag="body"),
        Line("N", "Ama sonra Ölümsüzler arkanızdan çıktı. "
                  "Hayatta kalanlar küçük bir tepeye çekildi.", tag="hill"),
        Line("N", "Herodot'a göre, silahı kalmayanlar elleriyle ve dişleriyle savaştı.",
             tag="teeth"),
        Line("N", "Persler artık yaklaşmaya bile cesaret edemedi. "
                  "Uzaktan, ok yağmuruyla bitirdiler.", gap=0.3, tag="rain"),
        Pause(3.6, tag="fall"),
        Line("N", "Ve böylece, üç yüz Spartalının hikâyesi orada sona erdi.", gap=1.2,
             tag="end"),
    ], chapter="X. SON SAVAŞ"),

    # ------------------------------------------------------------------ SURVIVOR
    Scene("survivor", "lament", [
        Line("N", "Peki ya hayatta kalsaydın?"),
        Line("N", "Aristodemos adlı bir Spartalı, göz hastalığı yüzünden "
                  "savaştan önce geri gönderilmişti.", tag="aris"),
        Line("N", "Sparta'ya döndüğünde kimse onunla konuşmadı. "
                  "Ona, korkak anlamında Titrek dediler.", tag="shame"),
        Line("N", "Bir yıl sonra Plataia Savaşı'nda, ölümüne savaşarak düştü.", tag="plataea"),
        Line("N", "Yani Sparta'da hayatta kalmak bile, bazen ölümden ağırdı.", gap=0.7),
    ], chapter="XI. YA HAYATTA KALSAYDIN?"),

    # ------------------------------------------------------------------ AFTERMATH
    Scene("aftermath", "epic_end", [
        Line("N", "Termopil'den sonra Persler Atina'yı yaktı. "
                  "Ama sizin direnişiniz, Yunanlara zaman kazandırmıştı.", tag="athens"),
        Line("N", "Aynı yıl, Salamis'te Yunan donanması Pers filosunu yendi.", tag="salamis"),
        Line("N", "Ertesi yıl Plataia'da Pers ordusu ağır bir yenilgi aldı "
                  "ve Yunanistan'dan çekildi.", tag="plataea"),
        Line("N", "Sizin düştüğünüz yere, şair Simonides'in şu sözleri kazındı.",
             gap=0.8, tag="stone"),
        Line("LEO", "Ey yolcu, git Spartalılara söyle: "
                    "Onların yasalarına bağlı kalarak, burada yatıyoruz.",
             gap=1.5, tag="epitaph"),
    ]),

    # ------------------------------------------------------------------ OUTRO
    Scene("outro", "outro", [
        Line("N", "Sen olsaydın ne yapardın? Kalır mıydın, yoksa geri mi dönerdin?",
             tag="q"),
        Line("N", "Cevabını yorumlara yaz. Zaman Kırığı'na abone olmayı unutma.",
             tag="sub"),
        Line("N", "Bir sonraki zaman kırığında görüşmek üzere.", gap=1.0, tag="bye"),
        Pause(2.5, tag="logo"),
    ], tail=0.0),
]
