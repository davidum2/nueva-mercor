# Compaction rubric

## Criterion 1

````text
ID: criteria_0
Category: Goal fidelity
Weight: major
Description:
States the goal of replacing the single bounding box invalidation model of `bInvalidateEn` and `rInvalidateRect` with a bounded multi-region dirty-rectangle manager wired through the partial-redraw path.
````

## Criterion 2

````text
ID: criteria_1
Category: Goal fidelity
Weight: major
Description:
Lists `gslc_InvalidateRgnCount`, `gslc_InvalidateRgnGet`, and `gslc_InvalidateRgnIsDirty` as the three net-new public query functions.
````

## Criterion 3

````text
ID: criteria_2
Category: Goal fidelity
Weight: major
Description:
States that `GSLC_INVALIDATE_RGN_MAX` defaults to 8 and may be set to any value from 1 to 32 by a user config header or a compiler define.
````

## Criterion 4

````text
ID: criteria_3
Category: Goal fidelity
Weight: major
Description:
States that the region set is managed with no dynamic allocation anywhere in the core library's or the SDL driver's own code.
````

## Criterion 5

````text
ID: criteria_4
Category: Goal fidelity
Weight: major
Description:
States that any added rect with positive-area overlap transitively coalesces with the existing active regions into their bounding-box union until every region is pairwise disjoint.
````

## Criterion 6

````text
ID: criteria_5
Category: Goal fidelity
Weight: major
Description:
States that the add function clamps each input rect to the display bounds and drops empty or fully offscreen rects.
````

## Criterion 7

````text
ID: criteria_6
Category: Goal fidelity
Weight: major
Description:
States that screen invalidation yields exactly one full-display region.
````

## Criterion 8

````text
ID: criteria_7
Category: Goal fidelity
Weight: major
Description:
States that when the region count exceeds `GSLC_INVALIDATE_RGN_MAX`, the pair minimizing wasted area is repeatedly merged.
````

## Criterion 9

````text
ID: criteria_8
Category: Goal fidelity
Weight: major
Description:
States that when invalidation is active, each active region is drawn independently with the clipping rectangle set to that region before its background and element rendering.
````

## Criterion 10

````text
ID: criteria_9
Category: Goal fidelity
Weight: major
Description:
States that on a partial redraw every element pending redraw must end up rendered in each active region it intersects, including an element reaching into more than one of them.
````

## Criterion 11

````text
ID: criteria_10
Category: Goal fidelity
Weight: major
Description:
States that the SDL1 driver's screen presentation must update only the individual active regions with exactly one update per region, even when a single region covers the whole display.
````

## Criterion 12

````text
ID: criteria_11
Category: Goal fidelity
Weight: major
Description:
States that the active region set remains fully populated during the presentation step and is emptied only after the redraw and presentation pass completes, at which point clipping is restored to the full display.
````

## Criterion 13

````text
ID: criteria_12
Category: Goal fidelity
Weight: minor
Description:
Specifies that `gslc_InvalidateRgnCount` takes the GUI context and returns a `uint8_t` count of active tracked regions, or 0 when invalidation is disabled.
````

## Criterion 14

````text
ID: criteria_13
Category: Goal fidelity
Weight: minor
Description:
Specifies that `gslc_InvalidateRgnGet` takes the GUI context, a rectangle array, and a `uint8_t` maximum count, writes the active regions canonically sorted ascending by y, then x, then h, then w into that array when it is non-null, and returns the total count of active tracked regions.
````

## Criterion 15

````text
ID: criteria_14
Category: Goal fidelity
Weight: minor
Description:
Specifies that `gslc_InvalidateRgnIsDirty` takes the GUI context and a test rectangle and returns a `bool` reporting whether that rectangle has a positive-area intersection with at least one active region.
````

## Criterion 16

````text
ID: criteria_15
Category: Goal fidelity
Weight: minor
Description:
States that the forced-merge tie-break is independent of add order, putting the canonically smaller region of each pair first and taking the pair whose first region is canonically smallest, or whose second region is smallest when the first regions are equal, comparing ascending by y, then x, then h, then w.
````

## Criterion 17

````text
ID: criteria_16
Category: Goal fidelity
Weight: minor
Description:
States that transitive coalescing is re-run after each forced merge.
````

## Criterion 18

````text
ID: criteria_17
Category: Goal fidelity
Weight: minor
Description:
States that `gslc_InvalidateRgnReset` empties the region set and disables invalidation.
````

## Criterion 19

````text
ID: criteria_18
Category: Goal fidelity
Weight: minor
Description:
States that with no active region the SDL1 driver refreshes the whole display as before.
````

## Criterion 20

````text
ID: criteria_19
Category: Goal fidelity
Weight: minor
Description:
States that whole-display-only drivers such as SDL2 keep doing whole-display presentation unchanged.
````

## Criterion 21

````text
ID: criteria_20
Category: Goal fidelity
Weight: minor
Description:
Specifies that `malloc` family calls, memory mapping, and buffer-returning helpers such as `strdup` and `asprintf` are excluded from the core library's and the SDL driver's own code, while SDL's internal allocations on the library's behalf do not count.
````

## Criterion 22

````text
ID: criteria_21
Category: Goal fidelity
Weight: negative
Description:
States that `GSLC_INVALIDATE_RGN_MAX` is fixed at 8 and cannot be overridden by a project config.
````

## Criterion 23

````text
ID: criteria_22
Category: Goal fidelity
Weight: negative
Description:
States that the SDL2 driver will perform exactly one update per active region on presentation.
````

## Criterion 24

````text
ID: criteria_23
Category: Artifact preservation
Weight: minor
Description:
Identifies `bInvalidateEn` and `rInvalidateRect` in `gslc_tsGui` as the current invalidation state, referenced only in `GUIslice.c` and `GUIslice.h`.
````

## Criterion 25

````text
ID: criteria_24
Category: Artifact preservation
Weight: minor
Description:
Names `gslc_InvalidateRgnReset`, `gslc_InvalidateRgnScreen`, `gslc_InvalidateRgnPage`, and `gslc_InvalidateRgnAdd` as the existing invalidation functions built on `gslc_UnionRect`.
````

## Criterion 26

````text
ID: criteria_25
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_InvalidateRgnPage` calls `gslc_InvalidateRgnAdd` and then sets `bInvalidateEn` true redundantly.
````

## Criterion 27

````text
ID: criteria_26
Category: Artifact preservation
Weight: minor
Description:
Identifies `gslc_tsRect` as holding `int16_t` x and y with `uint16_t` w and h.
````

## Criterion 28

````text
ID: criteria_27
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_ElemSetRedraw` calls `gslc_InvalidateRgnAdd(pGui,pElem->rElem)` on redraw requests and sets `bRedrawNeeded` true.
````

## Criterion 29

````text
ID: criteria_28
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_SetStackPage` invalidates the old and new stack pages and sets `gslc_PageRedrawSet(true)` on a page change.
````

## Criterion 30

````text
ID: criteria_29
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_ElemSetRect` adds both the old and the new element rects.
````

## Criterion 31

````text
ID: criteria_30
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_ElemSetVisible` adds the hidden element's rect.
````

## Criterion 32

````text
ID: criteria_31
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_Quit`, `gslc_SetBkgnd*`, rotate, and `gslc_Init` use `gslc_InvalidateRgnScreen`.
````

## Criterion 33

````text
ID: criteria_32
Category: Artifact preservation
Weight: minor
Description:
Names `GUIslice_drv_sdl.c` as the file where `gslc_DrvPageFlipNow` calls `SDL_Flip(pScreen)` for SDL1.
````

## Criterion 34

````text
ID: criteria_33
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_DrvSetClipRect` uses `SDL_SetClipRect` for SDL1 and `SDL_RenderSetClipRect` for SDL2 with `gslc_DrvAdaptRect`.
````

## Criterion 35

````text
ID: criteria_34
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_DrvDrawBkgnd` blits the background surface honoring the clip rect.
````

## Criterion 36

````text
ID: criteria_35
Category: Artifact preservation
Weight: minor
Description:
Records that `bRedrawPartialEn` is true for the SDL1 driver and false for the SDL2 driver.
````

## Criterion 37

````text
ID: criteria_36
Category: Artifact preservation
Weight: minor
Description:
States that `gslc_PageFlipGo` calls `gslc_DrvPageFlipNow` only when `pGui->bScreenNeedFlip` and then calls `gslc_PageFlipSet(false)`.
````

## Criterion 38

````text
ID: criteria_37
Category: Artifact preservation
Weight: minor
Description:
States that `GUIslice.h` includes `GUIslice_config.h` with stock configs such as `linux-sdl1-default-mouse.h` and that the `#ifndef` override defaults pattern already exists in `GUIslice.h`.
````

## Criterion 39

````text
ID: criteria_38
Category: Artifact preservation
Weight: minor
Description:
States that `nDispW` and `nDispH` are `uint16_t`.
````

## Criterion 40

````text
ID: criteria_39
Category: Artifact preservation
Weight: minor
Description:
States that the build environment has `gcc 12.2.0` with `libsdl1.2-dev` and `libsdl2-dev` plus SDL_ttf installed.
````

## Criterion 41

````text
ID: criteria_40
Category: Artifact preservation
Weight: minor
Description:
States that `examples/linux/Makefile` builds with `GSLC_DRV=SDL1/SDL2` and `GSLC_CORE` listing `../../src/GUIslice.c` and the `../../src/elem/*.c` files.
````

## Criterion 42

````text
ID: criteria_41
Category: Artifact preservation
Weight: minor
Description:
Names `test_sdl1.c` and `test_sdl2.c` as tests in `examples/linux/`.
````

## Criterion 43

````text
ID: criteria_42
Category: Decision rationale
Weight: major
Description:
Records the decision to add an internal hold flag in `gslc_tsGui` that makes the `GSLC_REDRAW_NONE` branch of `gslc_ElemSetRedraw` early-return and skip clearing and parent propagation during every region pass except the last.
````

## Criterion 44

````text
ID: criteria_43
Category: Decision rationale
Weight: minor
Description:
Explains that `gslc_ElemDrawByRef` clears the element redraw flag via `gslc_ElemSetRedraw` with `GSLC_REDRAW_NONE`, so a naive per-region loop loses pending redraws after the first region.
````

## Criterion 45

````text
ID: criteria_44
Category: Decision rationale
Weight: minor
Description:
Explains that spare eElemFlags bits were rejected as a redraw snapshot because `gslc_SetElemRefFlag` truncates flags to `uint8_t`.
````

## Criterion 46

````text
ID: criteria_45
Category: Decision rationale
Weight: minor
Description:
Records the assumption that right and bottom edges fit the signed 16-bit coordinate range as elsewhere in the library.
````

## Criterion 47

````text
ID: criteria_46
Category: Decision rationale
Weight: minor
Description:
Identifies `SDL_UpdateRect` as the correct per-region partial-update call because the SDL1 screen surface is a software surface.
````

## Criterion 48

````text
ID: criteria_47
Category: Decision rationale
Weight: minor
Description:
Records the plan to define `GSLC_INVALIDATE_RGN_MAX` through the `#ifndef` override pattern in `GUIslice.h` with a range-check `#error`.
````

## Criterion 49

````text
ID: criteria_48
Category: Decision rationale
Weight: minor
Description:
Specifies maintaining `asInvalidateRgn[GSLC_INVALIDATE_RGN_MAX]` and `nInvalidateRgnCnt` in `gslc_tsGui` as the replacement for `rInvalidateRect`.
````

## Criterion 50

````text
ID: criteria_49
Category: Decision rationale
Weight: minor
Description:
Records the invariant that `bInvalidateEn` is true exactly when the region count is greater than 0.
````

## Criterion 51

````text
ID: criteria_50
Category: Decision rationale
Weight: minor
Description:
States that `gslc_InvalidateRgnGet` sorts into a local buffer so the internal region order need not stay sorted, because the drawing order of disjoint regions does not matter.
````

## Criterion 52

````text
ID: criteria_51
Category: Decision rationale
Weight: minor
Description:
Specifies that the redraw loop snapshots the active regions into a local `gslc_tsRect asRgn[GSLC_INVALIDATE_RGN_MAX]` via `gslc_InvalidateRgnGet`.
````

## Criterion 53

````text
ID: criteria_52
Category: Decision rationale
Weight: minor
Description:
Specifies `uint32_t` area math for the wasted-area comparison given the 16-bit edge assumption.
````

## Criterion 54

````text
ID: criteria_53
Category: Decision rationale
Weight: negative
Description:
States that spare eElemFlags bits 8 and 9 were chosen to snapshot pending redraw flags.
````

## Criterion 55

````text
ID: criteria_54
Category: Temporal coherence
Weight: major
Description:
Records that code exploration is complete and no code changes have been made.
````

## Criterion 56

````text
ID: criteria_55
Category: Temporal coherence
Weight: major
Description:
States that `gslc_InvalidateRgnReset` currently runs before the flip in `gslc_PageRedrawGo` and must be reordered to after the flip so the regions survive presentation.
````

## Criterion 57

````text
ID: criteria_56
Category: Temporal coherence
Weight: minor
Description:
Traces the redraw flow in `gslc_PageRedrawGo` from `gslc_PageRedrawCalc` and `gslc_PageRedrawGet` through the `GSLC_EVT_DRAW` dispatch via `gslc_PageEvent`, `gslc_CollectEvent`, and `gslc_ElemEvent` to `gslc_ElemDrawByRef`.
````

## Criterion 58

````text
ID: criteria_57
Category: Temporal coherence
Weight: minor
Description:
States that `gslc_PageRedrawGo` sets the clip rectangle to `rInvalidateRect` or NULL before the draw dispatch and adds `gslc_DrvDrawBkgnd` with `gslc_PageFlipSet(true)` on a full redraw.
````

## Criterion 59

````text
ID: criteria_58
Category: Temporal coherence
Weight: minor
Description:
States that the `DBG_REDRAW` prints, the `delay(1000)`, and the `gslc_DrvDrawFrameRect` marker in `gslc_PageRedrawGo` reference `rInvalidateRect` and need updating.
````

## Criterion 60

````text
ID: criteria_59
Category: Temporal coherence
Weight: minor
Description:
States that the repo is clean on master at commit `4568d6f`.
````

## Criterion 61

````text
ID: criteria_60
Category: Temporal coherence
Weight: negative
Description:
States that the multi-region invalidation changes have already been applied to `GUIslice.c`.
````

## Criterion 62

````text
ID: criteria_61
Category: Compression efficiency
Weight: minor
Description:
Contains at most 9300 characters.
````

## Criterion 63

````text
ID: criteria_62
Category: Structural clarity
Weight: minor
Description:
Groups the three new public query functions `gslc_InvalidateRgnCount`, `gslc_InvalidateRgnGet`, and `gslc_InvalidateRgnIsDirty` with their parameter and return details.
````
