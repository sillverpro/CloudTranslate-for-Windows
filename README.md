# CloudTranslate for Windows

A modern, portable Windows desktop translation tool built with **Python + CustomTkinter**, featuring a clean Windows 11 Fluent-style UI.

This app uses **Google Cloud Translate API** (free 500,000 characters/month) and provides fast translation for:

- English  
- Thai  
- WHO Languages (Arabic, Chinese, French, Russian, Spanish)  
- Extra Languages (Japanese, Korean, German)

---

## 🚀 Quick Start

You can use this project in **two ways**:

1. **Download the ready-made EXE (recommended for normal users)**  
2. **Run from Python source (for developers / customisation)**  

---

## 2.1 Use the EXE: *CloudTranslate for Windows.exe*

This is the easiest way – no Python needed.

1. **Download the EXE**
   - Go to the **Releases** page of this repo.
   - Download ` Source code (zip)` (or similar name).
   - Unzip/Extract zip file on your PC

2. **Create `config.json`**
   - In the same folder as the EXE, create a file called `config.json`.
   - Use this structure (you can also copy from `config.example.json` in the repo):

   ```json
   {
     "google_api_key": "YOUR_GOOGLE_API_KEY",
     "monthly_limit": 500000
   }
   ```

   - Replace `YOUR_GOOGLE_API_KEY` with your real Google Cloud Translate API key.

3. **Run the app**
   - Double-click **CloudTranslate for Windows.exe**.
   - If `config.json` is missing or invalid, the app will show an error.

4. **Where data is stored**
   - `usage.json` – keeps monthly character usage  
   - `history.json` – stores translation history  
   These files are auto-created in the same folder as the EXE.

---

## 2.2 Run from Python source (customisable)

Use this method if you:

- want to change the app name  
- want to add/remove languages  
- want to tweak UI behavior

### 1. Clone / download the repository

```bash
git clone https://github.com/YOUR_USERNAME/CloudTranslate-for-Windows.git
cd CloudTranslate-for-Windows
```

(Or download as ZIP and extract.)

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `config.json` next to `translator.py`

From the project folder, copy the example:

```bash
copy config.example.json config.json   # on Windows
```

Then edit `config.json`:

```json
{
  "google_api_key": "YOUR_GOOGLE_API_KEY",
  "monthly_limit": 500000
}
```

### 4. Run the app

```bash
python translator.py
```

### 5. Customising the app (languages, name, etc.)

Open `translator.py`:

- **Window title**

  Find:

  ```python
  self.title("CloudTranslate for Windows")
  ```

  Change to:

  ```python
  self.title("YOUR_APP_NAME")
  ```

- **Languages list**

  Modify:

  ```python
  LANG_CODES = {
      "en": "English",
      "th": "Thai",
      "ar": "Arabic",
      "zh": "Chinese",
      "fr": "French",
      "ru": "Russian",
      "es": "Spanish",
      "ja": "Japanese",
      "ko": "Korean",
      "de": "German",
  }
  ```

And the grouping function:

```python
def build_lang_display_list():
    display = []
    display.append(format_lang("en"))
    display.append(format_lang("th"))
    display.append("--- WHO Languages ---")
    for c in ["ar", "zh", "fr", "ru", "es"]:
        display.append(format_lang(c))
    display.append("--- Extra Languages ---")
    for c in ["ja", "ko", "de"]:
        display.append(format_lang(c))
    return display
```

---

## 📊 Features

- Windows 11 Fluent UI  
- Google Translate API  
- EN/TH + WHO + JP/KR/DE  
- Language grouping with non-selectable separators  
- Paste, Clear, Copy, Export (.txt)  
- Auto character count  
- Big-text warnings  
- Character usage tracking  
- Monthly auto-reset  
- Persistent translation history  
- Fully portable  

---

## 🧩 Requirements

```
customtkinter
requests
```

---

## 🪟 Build EXE

```bash
pyinstaller --onefile --noconsole translator.py
```

EXE will appear in:

```
dist/translator.exe
```

---

## 🛡 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## ✨ Author

**Prajuab Tunyu**
