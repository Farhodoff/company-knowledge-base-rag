# 🏢 Kompaniya Bilimlar Bazasi RAG — Foydalanish Bo‘yicha To‘liq Qo‘llanma

Ushbu qo‘llanma **Company Knowledge Base RAG** tizimini o‘rnatish, sozlash, hujjatlar yuklash va kundalik faoliyatda (Terminal, Web interfeys, Slack/Discord botlar) samarali ishlatish bo‘yicha to‘liq yo‘riqnomadir.

---

## 📑 Mundarija
1. [Loyiha haqida](#1-loyiha-haqida)
2. [Tezkor O‘rnatish (macOS va Linux)](#2-tezkor-ornatish-macos-va-linux)
3. [API Kalitini Sozlash (`GOOGLE_API_KEY`)](#3-api-kalitini-sozlash)
4. [Kompaniya Hujjatlarini Boshqarish (PDF, MD, CSV)](#4-kompaniya-hujjatlarini-boshqarish)
5. [Global CLI Buyruqlari (`company-rag`)](#5-global-cli-buyruqlari)
6. [Web Cockpit Interfeysi (Streamlit)](#6-web-cockpit-interfeysi)
7. [Jamoaviy Integratsiyalar (Slack, Discord, Webhook API)](#7-jamoaviy-integratsiyalar)
8. [Muammolarni Hal Qilish (Troubleshooting & FAQ)](#8-muammolarni-hal-qilish)

---

## 1. Loyiha haqida
**Company Knowledge Base RAG** — kompaniyaning ichki hujjatlari (HR ta’til siyosati, dasturlash standartlari, xavfsizlik reglamentlari, onboarding qo‘llanmalari) asosida ishlovchi xususiy AI yordamchi.

- **0% Gallyutsinatsiya**: AI faqatgina siz yuklagan hujjatlar ichidan javob topadi. Agar javob mavjud bo‘lmasa, to‘qib chiqarmaydi.
- **Aniq Sahifali Havolalar**: Har bir javob tagida hujjat nomi va sahifasi (masalan, `sample_vacation_policy.md (Page 1)`) keltiriladi.
- **Lokal-birinchi Maxfiylik**: Barcha matnlar sizning kompyuteringizdagi **FAISS** vektor bazasida saqlanadi.

---

## 2. Tezkor O‘rnatish (macOS va Linux)

###  1-qatorli Avtomatik O‘rnatgich
Terminalingizni oching va quyidagi buyruqni ishga tushiring:

```bash
curl -fsSL https://raw.githubusercontent.com/Farhodoff/company-knowledge-base-rag/main/install.sh | bash
```

**O‘rnatgich nimalarni bajaradi:**
1. Loyihani `~/.company-rag` papkasiga klonlaydi;
2. Izolyatsiyalangan virtual muhit (`.venv`) yaratadi va kerakli paketlarni o‘rnatadi;
3. Tizim bo‘yicha global `company-rag` buyrug‘ini ro‘yxatdan o‘tkazadi;
4. macOS uchun **Spotlight** ilovasini yaratadi: `~/Applications/Company Knowledge Base.app`.

> **Eslatma:** O‘rnatgandan so‘ng terminalni qayta oching yoki `export PATH="$HOME/.local/bin:$PATH"` buyrug‘ini bajaring.

---

## 3. API Kalitini Sozlash

Tizim Google Gemini modeli va embedding vektorlaridan foydalanishi uchun **Google Gemini API kaliti** zarur. Kalitni [Google AI Studio](https://aistudio.google.com/apikey) orqali bepul olishingiz mumkin.

### Kalitni buyruq orqali kiritish:
```bash
company-rag config SIZNING_API_KALITINGIZ
```
yoki:
```bash
company-rag set-key SIZNING_API_KALITINGIZ
```

Bu buyruq kalitni avtomatik saqlaydi va bazadagi hujjatlarni avtomatik vektor indeksiga aylantiradi.

---

## 4. Kompaniya Hujjatlarini Boshqarish

Tizim quyidagi formatlarni qo‘llab-quvvatlaydi:
- **PDF**: Qo‘llanmalar, sertifikatlar, nizomlar (`.pdf`)
- **Markdown / Matn**: Texnik standartlar, README lar (`.md`, `.txt`)
- **Word**: Rasmiy ko‘rsatmalar (`.docx`)
- **Jadval ma’lumotlari**: Xodimlar ro‘yxati, telefon kitobchalari (`.csv`)

### Yangi hujjat qo‘shish:
```bash
# 1. Istalgan PDF yoki MD faylni bazaga qo'shish:
company-rag add ~/Downloads/kompaniya_tibbiy_sugurta.pdf

# 2. Hujjatlar papkasini Finder'da ochish:
company-rag docs
```

### Hujjatlarni qayta indekslash (Embedding):
Agar papkaga qo‘lda bir nechta fayl tashlagan bo‘lsangiz:
```bash
company-rag ingest
```

---

## 5. Global CLI Buyruqlari (`company-rag`)

Terminaldan turib brauzerni ochmasdan butun bilimlar bazasidan foydalanish mumkin:

| Buyruq | Tavsif |
|---|---|
| `company-rag ask "Savol"` | Terminalda to‘g‘ridan-to‘g‘ri savol berish |
| `company-rag ui` | Brauzerda Streamlit grafik interfeysini ochish |
| `company-rag add <fayl>` | Yangi PDF/MD faylni nusxalash va indekslash |
| `company-rag ingest` | Hujjatlar papkasini to‘liq qayta indekslash |
| `company-rag docs` | Hujjatlar papkasini macOS Finder'da ochish |
| `company-rag config [KEY]` | API kalitini saqlash yoki `.env` ni tahrirlash |
| `company-rag update` | GitHub’dan so‘nggi yangilanishlarni tortib olish |
| `company-rag slack` | Slack botni ishga tushirish (Socket Mode) |
| `company-rag discord` | Discord botni ishga tushirish |
| `company-rag api --port 8000` | Universal REST Webhook serverini ko‘tarish |

---

## 6. Web Cockpit Interfeysi (Streamlit)

### Ishga tushirish:
```bash
company-rag ui
```
yoki **Spotlight** (`Cmd + Space`) orqali **"Company Knowledge Base"** ilovasini bosing.

### Imkoniyatlari:
1. **🌐 Til tanlash**: 🇺🇿 O‘zbekcha va 🇬🇧 English o‘rtasida 1 bosishda almashish.
2. **Tayyor tezkor savollar**: Ta’til, Backend standartlari, Onboarding va Xavfsizlik bo‘yicha tezkor tugmalar.
3. **Fayl yuklash (Drag & Drop)**: Yangi PDF yoki MD fayllarni to‘g‘ridan-to‘g‘ri interfeys orqali yuklash.
4. **Vektor manbalari (Verified Sources)**: Har bir javob tagidagi havolani bosib, asl matn parchasini ko‘rish.
5. **Parametrlarni sozlash**: Qidiruv algoritmi (`similarity` yoki `mmr`), model tanlovi (`gemini-2.5-flash`), Top-K qismlar soni.

---

## 7. Jamoaviy Integratsiyalar

### 1. Slack Bot (Socket Mode)
Kompaniyangiz Slack kanalida `@KnowledgeBot` deb savol berganda javob beradi:
```bash
company-rag slack
```
*Tashqi ochiq port yoki webhook ochish shart emas — Slack WebSocket orqali korporativ xavfsizlik devori (firewall) ortida ishlaydi.*

### 2. Discord Bot
Dasturchilar Discord serverida `!ask <savol>` buyrug‘i orqali ishlaydi:
```bash
company-rag discord
```

### 3. Universal REST Webhook API
Kompaniya ichki portali, HR sayti yoki Zapier bilan bog‘lash:
```bash
company-rag api --port 8000
```
**So‘rov yuborish (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{"question": "Ta’tilga chiqish tartibi qanday?"}'
```

---

## 8. Muammolarni Hal Qilish (Troubleshooting & FAQ)

### ❓ `company-rag: command not found` xatosi chiqsa:
Terminalni qayta ishga tushiring yoki quyidagini kiriting:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### ❓ `404 NOT_FOUND` modeli xatosi chiqsa:
Agar avval eski `text-embedding-004` modeli qolib ketgan bo‘lsa, yangi standartga o‘tkazing:
```bash
company-rag config SIZNING_API_KEY
```
Standart model `models/gemini-embedding-001` va `gemini-2.5-flash` qilib sozlangan.

### ❓ Hujjatlar o‘zgartirilganda javoblar yangilanmasa:
Qayta indekslash buyrug‘ini bering:
```bash
company-rag ingest
```

---

**Muallif**: Farhod ([GitHub: @Farhodoff](https://github.com/Farhodoff))  
**Litsenziya**: MIT License
