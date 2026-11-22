# 300 Spartalıdan Biri Olsaydın? — Zaman Kırığı

"300 Spartalıdan biri olsaydın ne olurdu?" videosunun tamamı kodla üretilir:
karakterler, animasyonlar, savaş sahneleri, Türkçe seslendirme, müzik, ses efektleri
ve altyazılar. Hiçbir hazır görsel/ses dosyası kullanılmaz (sadece açık lisanslı fontlar
ve açık kaynak Türkçe TTS ses modeli).

## Çıktılar (`output/`)

| Dosya | Açıklama |
|---|---|
| `300_Spartalidan_Biri_Olsaydin_github.mp4` | 1920×1080, 30 fps, 8:51, altyazılar gömülü (80 MB, depoya sığacak şekilde sıkıştırılmış) |
| `300_Spartalidan_Biri_Olsaydin.mp4` | Aynı videonun yüksek kaliteli hali (178 MB, `build.py` ile üretilir; GitHub limiti nedeniyle depoda yok) |
| `300_Spartalidan_Biri_Olsaydin.srt` | Ayrı altyazı dosyası (YouTube'a ayrıca yüklenebilir) |
| `thumbnail.jpg` / `thumbnail.png` | 1280×720 kapak görseli |
| `Reels_300_Spartali.mp4` | Dikey Reels/Shorts/TikTok versiyonu: 1080×1920, 55,5 sn |
| `Reels_300_Spartali.srt` | Reels altyazı dosyası |

## Bölümler

1. Soğuk açılış — okların güneşi kapatması, Dienekes: "Gölgede savaşırız."
2. Doğum — yaşlıların bebeği incelemesi (Plutarkhos), Taygetos
3. Agoge — 7 yaşında eğitim, yalınayak koşu, tek pelerin, sazlardan yatak, yemek çalma
4. Spartalı hayatı — kışla, ortak sofra, kara çorba esprisi
5. Pers tehdidi — Kserkses, Çanakkale'deki gemi köprüsü, ordu büyüklüğü (Herodot vs. modern tahmin)
6. Seçilmiş 300 — Karneia bayramı, oğlu olanlar, "Ya kalkanınla dön ya da üstünde"
7. Termopil — müttefikler (~7000), harita, Fokis duvarı, casus, Demaratos, "Molon labe"
8. Savaş — Medler, falanks, Ölümsüzler, sahte geri çekilme, Kserkses'in tahtından fırlaması
9. İhanet — Efialtes, Anopaia patikası
10. Son sabah — müttefiklerin gönderilmesi, Thespiaililer, "Akşam yemeğini Hades'te yiyeceğiz"
11. Son savaş — Leonidas'ın düşüşü, bedeni için 4 saldırı, Kolonos tepesi, ok yağmuru
12. Ya hayatta kalsaydın? — Aristodemos "Titrek"
13. Sonrası — Atina, Salamis, Plataia, Simonides'in kitabesi
14. Kapanış — soru, abone ol, logo

Kaynaklar: Herodot, *Tarih* VII–IX; Plutarkhos, *Lykurgos* ve *Lakonya Özdeyişleri*; Athenaios IV.

## Nasıl üretilir

```bash
pip install -r requirements.txt          # pycairo, numpy, scipy, piper-tts
python3 build.py                         # ses modeli indirilir, her şey yeniden üretilir
python3 build.py --audio                 # sadece ses
python3 build.py --video                 # sadece görüntü (+ mevcut ses ile birleştirme)
python3 src/thumbnail.py                 # kapak görseli
python3 build_reels.py                   # dikey Reels versiyonu (max 60 sn)
python3 src/render.py --scene final      # bir sahnenin önizleme kareleri
```

Gerekenler: Python 3.10+, ffmpeg (libx264, rubberband), Cairo. Türkçe ses modeli
(`tr_TR-dfki-medium`, Piper) ilk çalıştırmada Hugging Face'ten indirilir. Fontlar `assets/fonts/`
içindedir (Cinzel, Baloo 2, Nunito — SIL Open Font License); sistemde kurulu olmalıdır
(`~/.local/share/fonts` + `fc-cache`).

## Lisans notu (önemli)

Seslendirmede kullanılan Piper modeli `tr_TR-dfki-medium`, **CC BY-NC-SA 4.0 (ticari olmayan)**
lisanslı DFKI veri setiyle eğitilmiştir. Kanal para kazanıyorsa (reklam geliri vb.) bu sesi
kullanmak lisansa aykırı olabilir. Çözüm: `src/tts.py` içindeki `synth_line` fonksiyonunu ticari
kullanıma izin veren bir TTS'e (ör. ücretli bir ElevenLabs planı) ya da kendi kaydınıza
bağlamak — zaman çizelgesi, altyazı, müzik ve animasyon yeni seslerin sürelerine otomatik uyar.
Fontlar SIL OFL lisanslıdır (`assets/fonts/OFL-*.txt`), müzik ve efektler bu kodla üretilmiştir.

## Yapı

```
build.py                 tüm üretim hattı
src/script.py            senaryo (metin, konuşmacılar, sahne işaretleri)
src/tts.py               Piper TTS + karakter sesleri (perde/formant/yankı)
src/timeline.py          ses sürelerinden zaman çizelgesi ve altyazılar
src/draw/                cairo çizim motoru: karakterler, arka planlar, efektler, yazılar
src/scenes/              sahne animasyonları (s_intro, s_sparta, s_persia, s_battle, s_end)
src/audio/               enstrüman sentezi, müzik, ses efektleri, miks ve mastering
src/render.py            kare üretimi (paralel) + ffmpeg
```

Sahnelerin süresi seslendirmeden hesaplandığı için senaryodaki bir cümleyi değiştirip
`python3 build.py` çalıştırmak yeterlidir; görüntü, müzik, efektler ve altyazı otomatik
olarak yeni zamanlamaya uyar.
