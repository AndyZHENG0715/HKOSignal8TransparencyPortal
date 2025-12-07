## Chart Prototype

Presentation-ready charts live at `prototypes/charts.html`. They rely on the pre-generated JSON files under `/data`.

### Preview locally

From the project root:

```bash
# Option 1: Node
npx serve

# Option 2: Python
python -m http.server
```

Then open `http://localhost:3000/prototypes/charts.html` (or the port printed by your static server). The page fetches `data/index.json` plus per-event JSONs to render:

1. Tier compliance pie (Tier 1+2 vs Tier 3).
2. Early warning lead/lag horizontal bars.
3. Casualty and property scatter plots vs early-warning minutes.
4. A selectable per-event timeline that plots the number of reference stations ≥63 km/h with the T8 threshold.

Because it uses vanilla JS + Chart.js via CDN, no additional build step is required.
