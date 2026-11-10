# Spooky House Rescue

Bernie the dog ran into the silly spooky house on the hill. Kellan and Diana explore eight rooms, find things, and use them in the right places to bring him home: a key under the flowerpot, a cookie for Boo the ghost, cheese for the cellar mouse, a teddy for Fuzzy the monster under the bed. It is an original explore-and-solve adventure in the spirit of the old PC haunted-house adventures, with tapping instead of typing and nothing that can hurt you.

**Learning questions.** Eight times in each game a house friend asks a question before helping. Pick a level on the title screen:

- **Little (ages 4 to 6):** counting, colors, letters, shapes. Sparkles show what to tap next and things from the bag are used for you.
- **Kid (ages 7 to 12):** math, spelling, science. You pick what to use from your bag.
- **Grown-up:** harder trivia.

A wrong answer just means try again. Questions and room messages are read aloud (Voice button). The Hint button says what to do next. Progress saves by itself.

Single-file HTML5 game: open `index.html`. Tap or click to walk and use things; arrow keys also walk. Installs on Android from Chrome (Install app) and then works with no internet.

**Sound.** Beepy retro music and sound effects in the style of 1990 PC games, all original and made in the browser (no sound files): a title tune, sneaky music inside the house, creepy cellar music, a tiptoe tune upstairs and a happy tune when Bernie is found, plus door creaks, footsteps, ghost woos, an owl, a squeaky mouse, a purring cat and Bernie's bark. The Sound button turns it all off.

## Tests
`python3 tests/run.py` plays the whole game at all three levels, does 180 random-tap runs to check the game can never get stuck, tries real taps, and checks saving. Add a Chrome path and a folder to also save screenshots: `python3 tests/run.py "" shots`.

When you change a file, bump `CACHE` in `sw.js` so phones pick up the new version.
