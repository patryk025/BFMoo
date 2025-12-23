[snake.b -- snake game
(c) 2025 Daniel B. Cristofani
http://brainfuck.org/

This program is licensed under a Creative Commons Attribution-ShareAlike 4.0
International License (http://creativecommons.org/licenses/by-sa/4.0/).

This snake game is based closely on an earlier one written by PortalRunner
(https://github.com/p2r3/bf16/blob/main/examples/snake.b), which runs on a
specific brainfuck interpreter (https://github.com/p2r3/bf16/tree/main) and was
the subject of a YouTube video (https://www.youtube.com/watch?v=Qn0yFkgNXqQ).
This program's behavior copies the behavior of the original program in most
ways (and needs that same interpreter), but this one is written from scratch.

Because the video memory is densely packed and doesn't have maneuvering room,
we keep a separate map of the board and use it to update the video memory; each
move, we wipe the whole video memory and then poke the updated values into it,
filling it from left to right so we don't have to mess with previously placed
values.

If concision were the top priority, we'd want to generate a color code and then
poke it into the video memory, so we'd scan back and forth into video memory 48
times to set a cell to 48. Since speed is a priority, we instead scan in and
out once per pixel, by giving each color its own little scanning routine, at
the cost of duplicating the left-scanning code four times. We use a case
statement to choose between them. (Even with this optimization, setting values
in the video memory is the dominant time cost of this program; but it's fast
enough to reliably stay within a quarter of the allowed time to avoid lag
(at least on my laptop).)

Then the biggest algorithmic question is how we maintain the tail and switch
the end of the tail back to empty space at the right time. What I've done for
this program is to keep a counter associated with each tail cell: the oldest
tail cell will have value 1, and the newest will have value score-1 (where
score is the snake's length).

When moving the snake, we first find the head, turn it to a tail cell and set
its tail counter to the current score, then find the new head location. If it
was empty space, we decrement all nonzero tail counters, and we set the oldest
one (with a value of 1) to empty space. That's easy. Conversely, if the new
head cell was an apple, we leave the tail alone, increment the score, and place
a new apple "randomly".

Each pixel, then, gets three array cells in the map: a code for what kind of
pixel it is, a tail counter, and an empty space for navigation and scratch
space, as usual. Codes, chosen for concision with the help of a small program,
are head=-1, tail=2, empty=3, apple=4, wall=1. Walls are not copied to video
memory; they are just there to produce a game over if the snake hits them.
The right wall of each row doubles as the left wall of the next. The map is
terminated by zeroes at the left and right.

Between video memory and the map we keep a few globals. The score, current
direction of movement, "random" value, and a potential sound to output, as
well as some working space. The exact arrangement is somewhat arbitrary and
could probably be improved.

Once we get the video memory updated, we output it 8 times and try to get input
eight times, then process snake movement and update the map. The speed is
copied from the original program, but the input and output are put into an
inner loop executed eight times rather than making the movement-processing part
of the main loop conditional.

General data layout is:
v v v ... (256) v 0 0 0 d s m r n x c n x c n x c n x c n x c n ...
where v is video memory, d is direction, s is score, m is sound code sometimes
and 0 other times, r is "random" value, x are pixel codes of cells, c are tail
counters, and n are navigation cells (usually 0).

This program firmly assumes that cells are bytes.]

-[-[>+<-]>]
move past video memory

>>>>+++[>++++++<-]>[>[>>>]+[<<<]++++[>++++<-]>[>>[>>>]+++[<<<]>-]>-]
set up 18 rows each of 1 wall and 16 empties

>[->>>-]+[>>>]+[-<<<-]+
turn top and bottom row into wall (clearing start corner wall)

<--[--[<<<+>>>-]<<<]<<----
place snake head (location copied from original game)

<--[-----[>>>+<<<-]>>>]<<<<<<<<+[<<<]<+[
place apple; score=1; while score:

  <<<<<[-]>-[[<]<[-]>+[>]<-]+>+>>>>+>>>[
  wipe video memory; build trail of 1s;
  increment m cell for scanning past; for each pixel:

    -[<+>>>+<<-]+<[
    copy x value; set 1 for output case statement; if not wall:

      ++[---[-[
      selector

        ->[<<<]<[<]>+++[>----<-]<]apple
        >[[<<<]<[<]>-]<]empty
        >[[<<<]<[<]>>+++<-]<]tail
        >[[<<<]<[<]>>+++++<-]head

      >+++++++[<<++++>>-]+[>]<[>>>]
      build value and return to map
      (notice these are coded as (n plus 7) times 4)

    ]+>>>[<<+>>-]>
    leave n trail and restore x value
    (we move left on x cells and right on n cells)

  ]<<<[<-<<]>>+>->--->++++++++[
  done updating v cells; clear n trail; restore m; reduce r
  (we reduce r by 3 because we're increasing it by 21 each
  movement as in the original program: we use this loop executed
  8 times to increase by 24 so we decrease by 3 outside the loop);
  set loop counter to 8

  (note that this means if you use a number other than 8 to tweak
  the speed you will need to change the "random" code to
  compensate or else accept whatever your change does to it)

    <+++<.[-]<<<+<,
    increase r; output video memory (and play and clear sound);
    set new direction tentatively to 1; get input

    (note that the timing is a little fragile because if you do
    two inputs per snake movement it will accept only the second
    this can turn a U turn into a (fatal) 180

    I think the original game had this flaw but it was less of
    an issue because that game didn't have walls)
    
    -[>--<-[<+>>+<--[<-->----[<+>[+]]]]]
    set parts of new direction based on input

    (direction is stored as an offset to the current head location;
    can be minus 17 or minus 1 or 0 or 1 or 17

    in building it we store the 17 part left of the input cell and
    the 1 part right of the input cell)
 
    <[>++++>+<<-]>[>++++<-]>[>[-]<[>+<-]]>>>>>-
    use the aforementioned cells to build new direction;
    if nonzero it replaces old direction in d

  ]<<<<[
  end of input/output loop

  if d is nonzero (we are moving) process movement

  (making this conditional was slightly easier than adding a case
  for "new head cell was already a head cell")

    >[<<+>>>+[->>>+]->+<[<<<]<-]
    copy s (score) to head and move s 2 steps left 

    >+[->>>+]+++[<++++++>-]++<[-[<<<+>>>-]<<<]>[<+<<]
    the head movement code is a little bit of a mess

    go to head; change it to a tail cell and move 18 steps left;
    build trail of 1s in n cells leading from there back to globals

    next when we lengthen this trail by (direction plus 17) (which
    is always nonnegative) the trail will then point to the new head
    location (it points to the zero to the right of its end)

    in my first draft I had a version that would count the distance
    from head left to the globals; put that value in a cell; add
    d onto it; then use it to move back to new head location

    the problem with that is that because of the walls the distance
    to the bottom couple rows of the screen does not fit in a byte
    and I think trying to measure distance in non wall spaces would
    be too much trouble

    hence this rather clunky solution
 
    <<[<<+>>>>+<<-]>++++[>++++<-]>+[>>[>>>]+[<<<]>-]>>[->>>]+>---[
    copy d; add 17 to it; lengthen trail; go to new head location;
    then start a case statement

      -[
      game over (default case) (not space nor apple)

        [>>>]-[>+<-----]>+.<
        go to right end of map to get clear of data; produce and output
        a note a perfect fourth below the apple tone

        (I chose this as a game over sound instead of the three
        notes from the original program)

        (it sounds a bit quieter than the apple sound somehow)

        (I've arranged the positioning so this will then exit or
        skip all remaining loops and terminate the program)

        (we do not update video memory so the head is shown
        next to whatever it hit at the end)

      ]<[
      apple case

        ->-[<<<]<<<+[
        set x to head; move back to globals; increment s (score);
        if s is still nonzero:

          +>>>>[<<+<<[+>]>>[-[<<->>-]>]>-]
          increment s once more (you'll soon see why) and reduce r
          ("random") modulo minus score (number of empty spaces left)

          I've chosen a mod algorithm that expects to work with divisor
          minus 1 since minus score is one less than accurate (score is
          one greater than accurate)

          (this of course introduces a bias toward the upper part of
          the screen; oh well)

          <<+[<<->>[>>>]+>---[+++>>+>---]+++[<<<]<-]+[->>>]<<+[<<<]<
          increment the modulus/remainder because this code finds the
          nth empty space (can't be the zeroth)

          this code incidentally restores score (it was split haphazardly
          between divisor and remainder as usual for divmod code)

          now s is set to s plus one minus (remainder plus one) = score

          the main thing this big loop does is to find the nth empty space:
          each time through it starts looking at the first cell after the
          last one it checked last time through; and then builds a trail
          of 1 cells in n cells from there to the next empty space

          after finishing that loop we follow (and wipe) the trail and
          place an apple in the last empty space we found

          I should note that this one wipes the "random" number from r
          after placing it (as the original game does) but also does not
          factor in the snake head's current location in choosing an apple
          position; it seems tolerably unpredictable but places in a square
          near the upper left a little too often; haven't got that fully
          figured out yet; the quality could be improved some by measuring
          which of the 8 iterations of the input/output loop input occurs
          in (and possibly by not wiping r each time); not messing with it
          more right now

        ]-[>+<+++++++++]<[>>++.[-]]
        next we set m to the "found apple" sound ready for next output

        if s is zero (because the snake fills the whole board) this will
        end up in a space two left of its normal location in m

        but in that case the second little loop will find a nonzero d
        and will increase the note by 2 to make a note a whole tone up
        from the apple sound (which I've chosen as a victory sound)
        and will output and clear it (again not updating video memory to
        show the state after the eating of the apple: too much hassle for
        my taste right now) and syncs the pointer so we terminate the
        program at the 0 s

      ]>
      end of apple case

    ]<[
      empty space case

      ->-[>>>]<<<[>[-[->]<+[<]<]<<<<]<<
      set x to head; go to end of map; scroll back to start of map
      decrementing all c cells and when we find the one where c was 1
      turning that x from snake (2) to empty (3)

      this code is somewhat cute; think through both cases

      (I originally had one scan for the 1 in a c cell and a second
      scan to decrement all c cells; that was pretty short but this
      is even better)      

    ]
  ]<[[[>>+<<-]<]>>]>>
  restore score and direction to their original places in s and d
  (if score is still nonzero)

]
end at s in cases other than "lose game"
(if game is won pointer is at s=0 (score of 256); if game is lost
pointer is at a zero far to the right)
