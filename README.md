# CloudPlus Quiz Practice

Static quiz practice site generated from the PDF files in `Question/`.

## Files

- `index.html` - GitHub Pages entry point
- `app.js` / `styles.css` - static frontend
- `data/questions.json` - generated quiz database
- `assets/questions/` - cropped question images from the source PDFs
- `assets/answers/` - cropped official answer strips from the source PDFs
- `tools/build_quiz_data.py` - PDF extraction script

## Regenerate Data

Run from this folder:

```powershell
$py='C:\Users\prang\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py .\tools\build_quiz_data.py
```

The extractor reads `cloud_quiz01.pdf` through `cloud_quiz12.pdf` only and ignores `cloud_quiz_final.pdf`.
