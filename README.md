# GraphIt — Learn Coordinates Activity

A Sugar learning activity that teaches children X/Y coordinate graphing
in a fun, interactive way.

![GraphIt Screenshot](screenshots/01.png)

## What is GraphIt?

GraphIt lets kids:
- **Click** on a grid to plot points at integer coordinates
- **Type** exact `(x, y)` values using the coordinate entry boxes
- **Connect dots** with lines to draw shapes
- **Follow challenges** — match the ghost shape by plotting the right points
- **Free draw** — make any shape they imagine

The grid runs from **-10 to +10** on both axes. Every plotted point shows
its `(x, y)` label on the graph and is listed in order on the sidebar.

## Built-in Challenges

| Challenge | Points | Difficulty |
|-----------|--------|------------|
| ⭐ Star    | 11     | Medium     |
| 🏠 House   | 12     | Easy       |
| 🚀 Rocket  | 14     | Hard       |
| 🎨 Free Draw | — | Your choice |

## How to Play

1. Click anywhere on the grid → snaps to the nearest coordinate
2. Or type `x` and `y` in the boxes and press **Plot**
3. Toggle **Connect dots** in the toolbar to draw lines between points
4. Try to match the ghost shape shown on screen
5. Get ⭐ when you match all the target points!

## Controls

| Button | Action |
|--------|--------|
| Click grid | Plot a point |
| ↩ Undo | Remove last point |
| 🗑 Clear | Remove all points |
| 🔗 Connect | Toggle line drawing |
| ▶ Next | Next challenge |
| ? Help | Show instructions |

## Installation

### From Sugar (recommended)
Download the `.xo` bundle and open it in Sugar — it installs automatically.

### From source
```bash
git clone https://github.com/sugarlabs/graph-activity
cd graph-activity
python setup.py install
```

### Run without Sugar (for development)
```bash
sugar-activity3 activity.GraphIt
```

## Development

```
graph-activity/
├── activity.py               # Main GTK3 Sugar activity
├── activity/
│   ├── activity.info         # Activity metadata
│   └── activity-graphit.svg  # Activity icon
├── po/
│   └── GraphIt.pot           # Translation template
├── setup.py
├── README.md
└── NEWS
```

## Contributing

Contributions welcome! Ideas for future improvements:

- [ ] More challenge shapes (triangle, diamond, smiley face, letters)
- [ ] Quiz mode — show shape, hide coordinates, kids must figure them out
- [ ] Score system based on accuracy and speed
- [ ] Export drawing as image
- [ ] Collaborative multiplayer via Sugar's CollabWrapper
- [ ] Fractional coordinates (0.5 steps)

Please open an issue or pull request on GitHub.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Copyright (C) 2025 Kushal Kant Bind# Graph-activity
This activity taches students how to dram simple graph 
