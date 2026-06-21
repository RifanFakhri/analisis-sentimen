Execution diagram (Mermaid) for the sentiment analysis system.

Files:
- `execution_diagram.mmd` : Mermaid source for the full system execution diagram.

How to render locally:

1) VS Code (recommended)
   - Install the "Markdown Preview Mermaid Support" or "Mermaid Preview" extension.
   - Open `execution_diagram.mmd` and use the extension to preview and export to PNG/SVG.

2) mermaid-cli (Node.js)
   - Install Node.js and run:

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagrams/execution_diagram.mmd -o diagrams/execution_diagram.svg
```

3) Online editors
   - Paste the Mermaid source into https://mermaid.live to preview and export.

If you want, saya bisa mencoba merender file SVG di lingkungan ini (jika Node/npm tersedia)."