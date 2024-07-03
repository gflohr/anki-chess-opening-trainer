# Anki Opening Trainer

This is the source code repository for the
[Anki](https://apps.ankiweb.net/)-add-on
"[Chess Opening Trainer](https://ankiweb.net/shared/info/705507113)". Anki is
a popular, open-source flashcard application.  The add-on takes a collection of
chess games and creates flashcards from it, helping you in building up an
opening repertoire.

## How It Works

You should have two decks, one deck for playing the opening with the white
pieces, one for playing with black.  I have a structure like the following

* Chess
* Chess::Opening
* Chess::Opening::White
* Chess::Opening::Black

If you select `Chess::Opening` for studying, you will study playing with white
and black in parallel.

You import one or more collections of games in Portable Game Notation (PGN)
format, and specify whether it is contains an opening repertoire for white
or for black.  If you specify white, all black moves are considered a
question, and all white replies found in the collection are considered correct
answers.

That differs from traditional opening libraries where the moves for both
black and white are considered playable moves.  But when you study an opening,
you should also remember how to reply to non-optimal moves of your opponent.
Therefore, it makes sense that you also include bad moves or blunders for
the other side.

It is also important that you reserve one Anki deck exclusively for one
collection of games.  When you import that collection again, the deck is
synchronized with the games in that collection.  Modified lines are updated,
and flashcards (called "notes" in Anki) that are no longer contained in the
collection are deleted.

## Usage

When you open Anki, you will find a new menu entry `Tools` ->
`Chess Opening Trainer`.  It shows a dialog box with four inputs:

* a list of PGN files containing the collection
* the deck where to import the collection
* the side that you are training for (black or white)
* the note type

The Anki "note type" is the layout of the flashcard.  This add-on requires
a note type with just two fields (front and back side) and no additional
elements.  This note type is one of the default types of Anki, usually called
"Basic".

But first you need at least one game collection, either for black or white.
Read on!

## Creating a Game Collection

Experienced chess players will usually have their own tool for creating PGN
files.  One easy option is to create a "study" on the online chess platform
lichess.org.  Select the "Learn" menu item, and then "Studies".  Go to
"My studies", click the Plus (+) button in the upper right corner and name
the collection something like "Opening Repertoire White".  Leave the board
orientation to white (switch to black if you want to learn from black's
perspective).

Next, you have to give the name of the first chapter.  Choose "A41 Old
Indian Defence".  You should now see a chess board that allows you to enter
moves.

It makes sense to first enter the main line, for example **1. d4 d6 2. c4 d6
3. Nc3 e5 4. d5**.  Say, you want to prepare for other replies of black to **3. Nc3.**
Select that move in the move window, and then enter another move **3. ... Nf6**.
That will create a variation.  A good continuation for white whould be 
**4. Nf3**.  Enter that move.

Black can also blunder here.  Select **3. Nc3** again and enter **3. ... Be6**.  This is
a blunder but you have to remember how to exploit it.  The correct answer is
**4. d5** because it attacks both the knight on c6 and the bishop on e6.

Later in Anki the move sequence **1. d4 d6 2. c4 d6 3. Nc3 Be6** will become a
question.  You will see the sequence of moves and a board representation of
this position.  The response will say **4. d5** and you will also see the position
*after* that move.

In chess literature, moves are often annotated with interpunction.  In lichess
you will find a little toolbar under the board.  Click on `!?` and then select
`??` for blunder.  You can now see that the bishop move changes to **3 ... Be6??**
in the move window.

You may also want to explain what is going on.  In the toolbar under the board
click on the speech bubble and enter a text like "Attacks both the knight on c6
and the bishop on e6".  The comment will appear in the move window, and later
in Anki will also be visible in the response to the exercise.

It is also possible to visualise the attack.  Right-click the pawn on d5 and
drag the mouse pointer to the bishop while holding down the ctrl key.  A red
arrow will appear.  Repeat this with the knight on c6.  If you want to show
that the pawn cannot be captured by the bishop, right-click on the knight on
c3.  It will be marked with a green circle.  Right-click and drag the mouse
pointer from c3 to d5, and a green arrow will appear showing that the knight
defends the pawn.  All these graphics will also be visible in Anki later.

You can explore all possibilities at https://lichess.org/study/ZRtfG7rP/gT2yFeb2

You can add more chapters to your study but in the end you have to get it into
Anki.  In the toolbar under the board, click on the "share" symbol.  Select
"study pgn" and you will find a file "lichess_study_*****.pgn" in your
download directory.

## Import into Anki

Open Anki, click `Tools -> Chess Opening Trainer`. Click the "Select files" button,
and navigate to the file(s) containing your games.  You can also select multiple
files at once.

Choose a deck of your choice, leave the colour as white, and make sure that
the note type is "Basic".  You should now have a deck with cards from every
position with white to move.  If you later edit the study, you can import
an updated version again, that gets merged into the existing deck.  Your
progress will be preserved to the extent possible.

*Important!* The PGN file must be in UTF-8 encoding!

You can import more files but you should always be sure whether the
currently selected deck is holding games from white's or black's
perspective.

## Copyright

This is free software.  Copyright © 2023, Guido Flohr <guido.flohr@cantanea.com>,
all rights reserved.
