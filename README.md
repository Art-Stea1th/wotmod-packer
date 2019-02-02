# *.wotmod Packer

This is a very simple utility that speeds up debugging mods.

- Write code
- Run the utility
- Start the game, after everything is rebuilt and deploy

just put this package next to the folder where your mod_{name}.py is located and run

All *.py modules and packages that are at this level and below will be compiled and packaged in:
- mod_{name}.wotmod\res\scripts\client\gui\mods, like the other, near mod files.

If GAME_PATH is set correctly, the mod will be immediately placed in the folder.
- \mods\x.x.x.x, where x.x.x.x is the current version of the game.

Otherwise, the variable BUILD_OUTPUT will be used.

If there is something incorrect in BUILD_OUTPUT, then the mod will be placed next to the working directory.
