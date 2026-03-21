# GraphIt

GraphIt is an interactive coordinate graphing activity for the Sugar desktop.

GraphIt shows a grid with X and Y axes. Click anywhere on the grid to plot points at integer coordinates, or type exact values using the coordinate entry boxes. Built-in challenges show a ghost shape to guide you — match all the target points to complete the task. A free draw mode lets you create any shape you imagine.

GraphIt is not part of the Sugar desktop, but can be added.

Please refer to;
- [How to Get Sugar](https://www.sugarlabs.org),
- [How to use Sugar](https://help.sugarlabs.org),
- [How to use GraphIt](#how-to-use).

## How to use

- Choose a shape category from the sidebar (Triangles, Quadrilaterals, Stars & Polygons, or Free Draw)
- Pick a challenge from the list — a ghost shape appears on the grid as your target
- Click the grid to plot a point, or type x and y values and press Plot
- Match all the ghost points to complete the challenge and earn a star
- Use Undo (↩) in the toolbar to remove the last point
- Use Clear to remove all points and start fresh
- Toggle Connect in the toolbar to draw lines between your points
- Press the ℹ button in the toolbar to reopen the how-to-play screen

## How to upgrade

On Sugar desktop systems;
- use My Settings, Software Update, or;
- use Browse to open [activities.sugarlabs.org](https://activities.sugarlabs.org), search for GraphIt, then download.

## How to develop

Setup a [development environment for Sugar desktop](https://github.com/sugarlabs/sugar/blob/master/docs/development-environment.md),
```bash
cd ~/Activities
git clone https://github.com/Bindkushal/Graph.activity.git Graph.activity
```

Log out and back in to Sugar — GraphIt will appear on the home screen.

Test in Terminal by typing;
```
sugar-activity3 activity.GraphIt
```

## Dependencies

GraphIt depends on Python, Sugar Toolkit for GTK+ 3, GTK+ 3, and PyCairo.

## Licence

GPLv3+. See [COPYING](COPYING).
