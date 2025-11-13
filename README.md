# OJAD Pitch‑Accent Graph Downloader  

A Python script that reads Japanese sentences from a CSV file, sends each sentence to the **OJAD phrasing service** (the online “Japanese‑Open‑Dictionary of Accents & Dialects”), captures the generated pitch‑accent graph as a PNG image, and saves the image with a user‑defined filename. 

0019-JB.png

🔗 **OJAD phrasing service:** https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing   (official site for Japanese pitch‑accent analysis).

## ✨ Features
- **Fully configurable**: CSV path, output folder, head‑less mode, crop margins, and the column numbers for filename & text are all set at the top of the script.  
- **Single WebDriver instance** – fast processing of many rows.  
- **No personal data is sent** beyond the text you provide; the script only contacts OJAD.  

## 📦 Installation  

```bash
# Clone the repo
git clone https://github.com/your‑username/ojad-pitch-graph-downloader.git
cd ojad-pitch-graph-downloader

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

`requirements.txt` contains:
```
geckodriver-autoinstaller
selenium
beautifulsoup4
pillow
```

## 🛠️ Configuration  

Open `download_pitch_graphs.py` and edit the **settings block** at the top:

```python
CSV_PATH          = 'AnkiExport.csv"   # path to your CSV
OUTPUT_DIR        = "pitch_graph"          # where PNGs will be saved
HEADLESS          = True                   # set False to see the browser
CROP_TOP_PIXELS   = 60                     # pixels trimmed from the top
CROP_BOTTOM_PIXELS= 15                     # pixels trimmed from the bottom

# CSV column numbers (0‑based)
FILENAME_COL      = 0   # column that holds the output filename (e.g. Anki UUID)
TEXT_COL          = 1   # column that holds the Japanese phrase
```

*Columns are **0‑based**:* the first column is `0`, the second is `1`, etc.  
Adjust `FILENAME_COL` and `TEXT_COL` to match the layout of your CSV file.

## ▶️ Running the script  

```bash
python download_pitch_graphs.py
```

The script will:

1. Open the CSV.  
2. For each row, send the Japanese text to OJAD.  
3. Capture the generated pitch‑accent graph, crop it, and save it as  
   `OUTPUT_DIR/<filename>.png`.  

## 📂 Output  

All PNG files are placed in the folder defined by `OUTPUT_DIR`.  
If a file with the same name already exists, the script skips regeneration.

## 🐞 Troubleshooting  

- **`NoSuchElementError`** – OJAD may show a loading overlay. The script now waits for it to disappear; if the problem persists, try running with `HEADLESS = False` to watch the page.  
- **Blank images** – increase `CROP_TOP_PIXELS`/`CROP_BOTTOM_PIXELS` or add a short `sleep` after the CSS injection.  
- **Unicode errors** – ensure your CSV is saved as UTF‑8 (or UTF‑8‑BOM).  

## 📜 License  

This project is released under the MIT License – feel free to fork, modify, and use it in your own tools.

---  

**Enjoy generating pitch‑accent graphs!**





---
## How can I add these to Anki?

### 1. Add a column that contains an HTML `<img>` tag  

1. Open the CSV you already use for the downloader (e.g. `AnkiExport.csv`) in a spreadsheet program (Excel, LibreOffice Calc, Google Sheets) or a text editor.  
2. Insert a **new column** that will hold the filename for the pitch graph (the column you set as `FILENAME_COL`). Important: the order of the CSV columns must match the order of the fields in the Anki note type (or you must map each column to the correct field in the dialog). 
3. In the first data row of that new column enter the formula that builds the tag.  
   *If you are using a spreadsheet:*  

   - **Excel / LibreOffice** (assuming the filename column is **A** and the new column is **B**):  

     ```excel
     = "<img src=""" & A2 & ".png"">"
     ```

   - **Google Sheets** (same layout):  

     ```gs
     = "<img src=""" & A2 & ".png"">"
     ```

   Drag the fill‑handle down so the formula is applied to every row.  

4. If you edit the file directly in a text editor, you can generate the column with a quick script (Python example):

   ```python
   import csv

   in_path  = "AnkiExport.csv"
   out_path = "AnkiExport_with_img.csv"

   with open(in_path, newline="", encoding="utf-8") as src, \
        open(out_path, "w", newline="", encoding="utf-8") as dst:
       r = csv.reader(src)
       w = csv.writer(dst)

       for row in r:
           # assume filename is column 0
           filename = row[0]
           img_tag = f'<img src="{filename}.png">'
           # insert the tag after the filename column
           row.insert(1, img_tag)   # now column 1 holds the <img> tag
           w.writerow(row)
   ```

5. Save the file as **UTF‑8** (most spreadsheet programs will do this automatically when you export as CSV).

### 2. Create a new field in the Anki note type  

1. Open Anki → **Browse**.  
2. Select the note type used by the deck you are about to import (e.g. “Basic” or a custom type).  
3. Click **Fields…** → **Add**.  
4. Name the field something like `PitchGraph`. Change the field order to match the order of the columns in your `.csv`. 
5. Click **OK** to close the dialog.  

### 3. Import the modified CSV into Anki  

1. In Anki’s main window choose **File → Import**.  
2. Select the CSV you created in step 1 (`AnkiExport_with_img.csv`).  
3. In the import dialog:  

   - **Type:** choose the note type you edited in step 2.  
   - **Fields mapping:** ensure  each CSV column maps to the corresponding Anki field.  
     - The column that now contains the `<img …>` tag should be mapped to the `PitchGraph` field you just added.  
   - Make sure **Allow HTML in fields** is **checked** (otherwise Anki will escape the `<img>` tag).  
   - Set the appropriate **Deck** destination.  

4. Click **Import**. Anki will create a card for each row; the `PitchGraph` field will contain the raw HTML tag.

### 4. Move the PNG files to Anki’s media folder  

Anki looks for media files (images, audio, etc.) in the **collection.media** directory of the profile you are using.

1. Locate the folder:  

   - On Windows: `C:\Users\<YourUser>\AppData\Roaming\Anki2\<ProfileName>\collection.media`  
   - On macOS: `~/Library/Application Support/Anki2/<ProfileName>/collection.media`  
   - On Linux: `~/.local/share/Anki2/<ProfileName>/collection.media`  

   You can also open it from Anki → **Tools → Open Collection Folder**, then open the `collection.media` sub‑folder.

2. Copy (or move) **all PNG files** that were generated by the downloader (`pitch_graph/*.png`) into that folder.  

   ```bash
   # Example on macOS / Linux
   cp -r pitch_graph/*.png "/path/to/Anki2/Default/collection.media/"
   ```

3. Restart Anki (or press **Ctrl + R** on a card) so the media index is refreshed.  

Now each card’s `PitchGraph` field will render the image:

```
<img src="filename.png">
```

Because the image file lives in `collection.media`, Anki resolves the relative path automatically and displays the pitch‑accent graph on the card.
