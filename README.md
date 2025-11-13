# WHO Translator (Windows 11 Style)

A modern, portable Windows desktop translation tool built with **Python + CustomTkinter**, featuring a clean Windows 11 Fluent-style UI.

This app uses **Google Cloud Translate API** (free 500,000 characters/month) and provides fast translation for:

- English  
- Thai  
- WHO Languages (Arabic, Chinese, French, Russian, Spanish)  
- Extra Languages (Japanese, Korean, German)

---

## 🚀 Features

### 🖥 Windows 11 Fluent Style UI
- Modern CustomTkinter interface
- Clean layout with black accent buttons
- Always-on character counter

### 🌐 Free Google Cloud Translate
- 500,000 characters/month
- No language detection (lower cost)
- WHO languages + extra languages
- Source/target grouping with non-selectable separators

### 🧠 Smart UI Behavior
- Language grouping:
  ```
  English
  Thai
  --- WHO Languages ---
  Arabic, Chinese, French, Russian, Spanish
  --- Extra Languages ---
  Japanese, Korean, German
  ```
- Separator lines cannot be selected

### 🔤 Text Input & Output
- Paste, Clear, Copy, Export (.txt)
- Auto character counting
- Warning for long text (≥ 5000 chars)
- Swap languages instantly

### 📊 Usage Tracking
- Counts characters translated each month
- Resets automatically every new month
- Shows remaining quota

### 🕒 Persistent History
- Automatically saved to `history.json`
- Organized by date
- Keeps most recent 500 entries

### 💼 Fully Portable
Everything is stored next to the `.exe`:
```
translator.exe
config.json
history.json
usage.json
```

---

## 📁 Project Structure

```
who-translator/
│
├── src/
│   ├── translator.py
│   ├── config.example.json
│   └── README.md
│
├── screenshots/
│   ├── main_ui.png
│   └── history.png
│
├── .gitignore
├── LICENSE
├── requirements.txt
```

---

## 🛠 Installation (Source)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up config  
Copy `config.example.json` → rename to `config.json`

```json
{
  "google_api_key": "YOUR_API_KEY",
  "monthly_limit": 500000
}
```

### 3. Run the app
```bash
python translator.py
```

---

## 🪟 Building Portable EXE

Run inside `/src`:

```bash
pyinstaller --onefile --noconsole translator.py
```

Output EXE will be in:

```
dist/translator.exe
```

Copy this next to your `config.json`.

---

## 🖼 Screenshots

```
Add your screenshots inside /screenshots and reference them here:
![Main UI](screenshots/main_ui.png)
![History](screenshots/history.png)
```

---

## 🌐 Supported Languages

### Main  
- English (en)  
- Thai (th)  

### WHO Languages  
- Arabic (ar)  
- Chinese (zh)  
- French (fr)  
- Russian (ru)  
- Spanish (es)  

### Extra  
- Japanese (ja)  
- Korean (ko)  
- German (de)

---

## 🛡 License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## ✨ Author  
**Prajuab Tunyu**

