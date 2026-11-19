## Original Request
- Replace GUIslice's single-bounding-box invalidation model (`bInvalidateEn` with `rInvalidateRect`) with a bounded multi-region dirty-rectangle manager wired through the partial-redraw path.
- Introduce `GSLC_INVALIDATE_RGN_MAX` as the maximum number of simultaneously-tracked active regions with a default value of 8.
- Allow a user configuration header (a stock `configs/` file or a project's own header) to set `GSLC_INVALIDATE_RGN_MAX` to any value from 1 to 32.
- Allow a compiler define to set `GSLC_INVALIDATE_RGN_MAX` to any value from 1 to 32.
- Add public query function `gslc_InvalidateRgnCount` taking the GUI context and returning a `uint8_t` count of active tracked regions (or 0 if invalidation is disabled).
- Add public query function `gslc_InvalidateRgnGet` taking the GUI context, a rectangle array, and a `uint8_t` maximum count.
- `gslc_InvalidateRgnGet` writes active regions canonically sorted ascending by `y`, then `x`, then `h`, then `w` into the caller's array up to the maximum count when the array pointer is non-null.
- `gslc_InvalidateRgnGet` returns the `uint8_t` total count of active tracked regions.
- Add public query function `gslc_InvalidateRgnIsDirty` taking the GUI context and a test rectangle and returning a `bool` reporting whether that rectangle has a positive-area intersection with at least one active region.
- Maintain at most `GSLC_INVALIDATE_RGN_MAX` pairwise non-overlapping active regions.
- Perform no dynamic memory allocation in the core library's own code when updating, querying, redrawing, or presenting the region set.
- Perform no dynamic memory allocation in the SDL driver's own code when updating, querying, redrawing, or presenting the region set.
- Disallowed allocation calls in core or SDL driver code include the `malloc` family, memory mapping, and buffer-returning helpers such as `strdup` or `asprintf` (SDL's internal allocations on the library's behalf do not count).
- `gslc_InvalidateRgnAdd` clamps each input rectangle to the display bounds.
- `gslc_InvalidateRgnAdd` drops any clamped rectangle that is empty or falls entirely offscreen.
- Right and bottom edges of rectangles are assumed to fit the signed 16-bit coordinate range, matching the rest of the library.
- Any added rectangle with positive-area overlap transitively coalesces with existing active regions into their bounding-box union until every region is pairwise disjoint.
- Non-overlapping areas invalidated during a single element operation must remain separate active regions.
- When the active region count exceeds `GSLC_INVALIDATE_RGN_MAX`, repeatedly merge the pair minimizing wasted area (bounding-box union area minus the sum of the two individual areas).
- Break forced-merge ties independently of add order by placing the canonically smaller region of each pair first under ascending `(y, x, h, w)` order.
- Among equal-waste pairs, select the pair whose canonically first region is smallest, or whose canonically second region is smallest when the first regions are equal.
- Re-run transitive coalescing after each forced merge.
- `gslc_InvalidateRgnScreen` yields exactly one active region covering the full display.
- `gslc_InvalidateRgnReset` empties the active region set.
- `gslc_InvalidateRgnReset` disables invalidation.
- When invalidation is active, draw each active region independently with the clipping rectangle set to that region before background rendering.
- When invalidation is active, draw each active region independently with the clipping rectangle set to that region before element rendering so nothing outside the active regions is repainted.
- On a partial redraw, every element pending redraw must be rendered in each active region it intersects, including elements spanning multiple active regions.
- Under SDL1, screen presentation must update only the individual active regions with exactly one update per active region, even when a single active region covers the whole display.
- Under SDL1 with no active regions, screen presentation refreshes the whole display as before.
- Whole-display-only display drivers such as SDL2 must keep presenting the whole display unchanged.
- The active region set must remain fully populated during the screen presentation step.
- The active region set must be emptied only after the redraw and presentation pass completes.
- Clipping must be restored to the full display upon completion of the redraw and presentation pass.

## Early Progress

### Codebase Findings
- `src/GUIslice.h` defines `bool bInvalidateEn` in `gslc_tsGui`.
- `src/GUIslice.h` defines `gslc_tsRect rInvalidateRect` in `gslc_tsGui`.
- Grepping outside `src/GUIslice.c` and `src/GUIslice.h` showed no references to `rInvalidateRect`.
- Grepping outside `src/GUIslice.c` and `src/GUIslice.h` showed no references to `bInvalidateEn`.
- Grepping `src/elem/` showed no references to `InvalidateRgn`.
- Grepping `examples/` showed no references to `InvalidateRgn`.
- `src/GUIslice.h` declares `gslc_InvalidateRgnReset`.
- `src/GUIslice.h` declares `gslc_InvalidateRgnPage`.
- `src/GUIslice.h` declares `gslc_InvalidateRgnScreen`.
- `src/GUIslice.h` declares `gslc_InvalidateRgnAdd`.
- `src/GUIslice.c::gslc_InvalidateRgnReset` currently sets `pGui->bInvalidateEn = false`.
- `src/GUIslice.c::gslc_InvalidateRgnReset` currently sets `pGui->rInvalidateRect` to `{ 0, 0, 1, 1 }`.
- `src/GUIslice.c::gslc_InvalidateRgnScreen` currently sets `pGui->bInvalidateEn = true`.
- `src/GUIslice.c::gslc_InvalidateRgnScreen` currently sets `pGui->rInvalidateRect` to `{ 0, 0, pGui->nDispW, pGui->nDispH }`.
- `src/GUIslice.c::gslc_InvalidateRgnPage` currently calls `gslc_InvalidateRgnAdd(pGui, pPage->rBounds)`.
- `src/GUIslice.c::gslc_InvalidateRgnPage` currently executes a redundant trailing `pGui->bInvalidateEn = true` statement.
- When `pGui->bInvalidateEn` is true, `src/GUIslice.c::gslc_InvalidateRgnAdd` currently merges into `pGui->rInvalidateRect` via `gslc_UnionRect`.
- When `pGui->bInvalidateEn` is false, `src/GUIslice.c::gslc_InvalidateRgnAdd` currently assigns `rAddRect` to `pGui->rInvalidateRect`.
- When `pGui->bInvalidateEn` is false, `src/GUIslice.c::gslc_InvalidateRgnAdd` currently sets `pGui->bInvalidateEn = true`.
- `src/GUIslice.c::gslc_PageRedrawGo` starts by calling `gslc_PageRedrawCalc(pGui)`.
- `src/GUIslice.c::gslc_PageRedrawGo` reads `bPageRedraw` via `gslc_PageRedrawGet(pGui)`.
- When `pGui->bInvalidateEn` is true, `src/GUIslice.c::gslc_PageRedrawGo` currently sets clipping via `gslc_SetClipRect(pGui, &(pGui->rInvalidateRect))`.
- When `pGui->bInvalidateEn` is false, `src/GUIslice.c::gslc_PageRedrawGo` currently sets clipping via `gslc_SetClipRect(pGui, NULL)`.
- Under `DBG_REDRAW`, `src/GUIslice.c::gslc_PageRedrawGo` prints `pGui->rInvalidateRect` bounds via `GSLC_DEBUG_PRINT`.
- Under `DBG_REDRAW`, `src/GUIslice.c::gslc_PageRedrawGo` draws a debug outline via `gslc_DrvDrawFrameRect(pGui, pGui->rInvalidateRect, GSLC_COL_RED)`.
- Under `DBG_REDRAW`, `src/GUIslice.c::gslc_PageRedrawGo` calls `delay(1000)`.
- Based on the agent's finding (the file read of `src/GUIslice.c::gslc_PageRedrawGo` was truncated after the clip setup), a full page redraw calls `gslc_DrvDrawBkgnd`.
- Based on the agent's finding (the file read of `src/GUIslice.c::gslc_PageRedrawGo` was truncated after the clip setup), a full page redraw calls `gslc_PageFlipSet(pGui, true)` after background drawing.
- For a full redraw, `src/GUIslice.c::gslc_PageRedrawGo` dispatches `GSLC_EVT_DRAW` with subtype `GSLC_EVTSUB_DRAW_FORCE` via `gslc_PageEvent`.
- For a partial redraw, `src/GUIslice.c::gslc_PageRedrawGo` dispatches `GSLC_EVT_DRAW` with subtype `GSLC_EVTSUB_DRAW_NEEDED` via `gslc_PageEvent`.
- `src/GUIslice.c::gslc_PageEvent` forwards `GSLC_EVT_DRAW` to `gslc_CollectEvent`.
- `src/GUIslice.c::gslc_CollectEvent` propagates `GSLC_EVT_DRAW` to each element reference in `pCollect->asElemRef` (up to `pCollect->nElemRefCnt`) via `gslc_ElemEvent`.
- For `GSLC_EVTSUB_DRAW_FORCE`, `src/GUIslice.c::gslc_ElemEvent` invokes `gslc_ElemDrawByRef` with `GSLC_REDRAW_FULL`.
- For `GSLC_EVTSUB_DRAW_NEEDED`, `src/GUIslice.c::gslc_ElemEvent` invokes `gslc_ElemDrawByRef` with the element's pending `eRedraw`.
- Based on the agent's finding (`gslc_PageRedrawGo` read truncated before the tail), `gslc_PageRedrawGo` currently clears page redraw state via `gslc_PageRedrawSet(pGui, false)`.
- Based on the agent's finding (`gslc_PageRedrawGo` read truncated before the tail), `gslc_PageRedrawGo` currently sets `pGui->bRedrawNeeded = false`.
- `src/GUIslice.c::gslc_PageRedrawGo` currently calls `gslc_InvalidateRgnReset(pGui)` before `gslc_SetClipRect(pGui, NULL)`.
- `src/GUIslice.c::gslc_PageRedrawGo` currently calls `gslc_SetClipRect(pGui, NULL)` before `gslc_PageFlipGo(pGui)`.
- `src/GUIslice.c::gslc_PageRedrawCalc` forces a full-page redraw (`bRedrawFullPage = true`) when any element on a drawable stack page in `apPageStack` (where `abPageStackDoDraw` is enabled) lacks `GSLC_ELEM_FEA_FILL_EN`, even when `bRedrawPartialEn` is true.
- `src/GUIslice.c::gslc_PageRedrawCalc` forces a full-page redraw when `pGui->bRedrawPartialEn` is false.
- `src/GUIslice.c::gslc_ElemDrawByRef` clears pending redraw state by calling `gslc_ElemSetRedraw(pGui, pElemRef, GSLC_REDRAW_NONE)` at the end of drawing.
- `src/GUIslice.c::gslc_ElemDrawByRef` also calls `gslc_ElemSetRedraw(pGui, pElemRef, GSLC_REDRAW_NONE)` on its invisible-element early exit.
- `src/GUIslice.c::gslc_ElemDrawByRef` also calls `gslc_ElemSetRedraw(pGui, pElemRef, GSLC_REDRAW_NONE)` on its focus-only redraw exit.
- `src/GUIslice.c::gslc_ElemSetRedraw` clears the redraw bits in `GSLC_ELEMREF_REDRAW_MASK` when `eRedraw == GSLC_REDRAW_NONE`.
- `src/GUIslice.c::gslc_ElemSetRedraw` sets `pGui->bRedrawNeeded = true` for non-NONE redraw requests.
- `src/GUIslice.c::gslc_ElemSetRedraw` propagates `eRedraw` to `pElem->pElemRefParent` when a parent exists.
- Based on the agent's finding (the file read of `src/GUIslice.c::gslc_ElemSetRedraw` was truncated after the switch statement), non-NONE redraw requests also call `gslc_InvalidateRgnAdd(pGui, pElem->rElem)`.
- `src/GUIslice.c::gslc_SetElemRefFlag` copies `pElemRef->eElemFlags` into a `uint8_t nCurFlags` local variable so any bits above bit 7 are truncated.
- `src/GUIslice.h` defines `gslc_teElemRefFlags` bits 0–7: `GSLC_ELEMREF_SRC` (bits 0–1), `GSLC_ELEMREF_EDITING` (`1<<2`), `GSLC_ELEMREF_FOCUSED` (`1<<3`), `GSLC_ELEMREF_REDRAW_MASK` (bits 4–5), `GSLC_ELEMREF_GLOWING` (`1<<6`), and `GSLC_ELEMREF_VISIBLE` (`1<<7`).
- Based on the agent's finding, `gslc_tsElemRef` entries in `asElemRef` are RAM-resident even when elements use `GSLC_ELEMREF_SRC_PROG` or `GSLC_ELEMREF_SRC_CONST`.
- `src/GUIslice.h` defines `gslc_tsRect` width `w` as `uint16_t`.
- `src/GUIslice.h` defines `gslc_tsRect` height `h` as `uint16_t`.
- The agent noted that `gslc_tsRect` coordinate `x` is `int16_t` (above the grep match).
- The agent noted that `gslc_tsRect` coordinate `y` is `int16_t` (above the grep match).
- `src/GUIslice.h` defines `nDispW` as `uint16_t`.
- `src/GUIslice.h` defines `nDispH` as `uint16_t`.
- `src/GUIslice.c` initializes `pGui->bRedrawPartialEn = false` before calling `gslc_DrvInit(pGui)` so display drivers can override partial-redraw support during initialization.
- `src/GUIslice.c::gslc_SetStackPage` calls `gslc_PageRedrawSet(pGui, true)` when the page ID changes.
- `src/GUIslice.c::gslc_SetStackPage` calls `gslc_InvalidateRgnPage` on the previous stack page, the new stack page, and any stack pages above it.
- `src/GUIslice.c::gslc_ElemSetRect` calls `gslc_InvalidateRgnAdd(pGui, pElem->rElem)` for the old rectangle before updating `pElem->rElem`.
- `src/GUIslice.c::gslc_ElemSetRect` calls `gslc_InvalidateRgnAdd(pGui, rElem)` for the new rectangle.
- `src/GUIslice.c::gslc_ElemSetVisible` calls `gslc_InvalidateRgnAdd(pGui, pElem->rElem)` when hiding an element (`bVisible == false`).
- The agent noted (beyond the grep truncation cut) that `SetBkgndImage` calls `gslc_InvalidateRgnScreen`.
- The agent noted (beyond the grep truncation cut) that `SetBkgndColor` calls `gslc_InvalidateRgnScreen`.
- The agent noted (beyond the grep truncation cut) that `GuiRotate` calls `gslc_InvalidateRgnScreen`.
- `src/GUIslice.c::gslc_PageFlipGo` calls `gslc_DrvPageFlipNow(pGui)` only when `pGui->bScreenNeedFlip` is true.
- After calling `gslc_DrvPageFlipNow(pGui)`, `src/GUIslice.c::gslc_PageFlipGo` clears the flip flag via `gslc_PageFlipSet(pGui, false)`.
- The agent reasoned that `gslc_PageFlipSet` under `DBG_DRAW_IMM` may call `gslc_DrvPageFlipNow` at draw time while invalidation regions are still active (body of `gslc_PageFlipSet` not shown).
- `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` currently calls `SDL_Flip(pScreen)` under `DRV_DISP_SDL1`.
- Under `DRV_DISP_SDL2`, `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` calls `SDL_RenderPresent`.
- Under `DRV_DISP_SDL2`, `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` calls `SDL_RenderClear` after `SDL_RenderPresent`.
- `src/GUIslice_drv_sdl.c` creates the SDL1 screen surface via `SDL_SetVideoMode(nSystemX, nSystemY, nBpp, SDL_SWSURFACE | SDL_FULLSCREEN)`.
- `src/GUIslice_drv_sdl.c::gslc_DrvSetClipRect` calls `SDL_SetClipRect` with `gslc_DrvAdaptRect` under `DRV_DISP_SDL1`.
- `src/GUIslice_drv_sdl.c::gslc_DrvSetClipRect` calls `SDL_RenderSetClipRect` with `gslc_DrvAdaptRect` under `DRV_DISP_SDL2`.
- `src/GUIslice_drv_sdl.c::gslc_DrvDrawBkgnd` calls `gslc_DrvPasteSurface` under `DRV_DISP_SDL1`.
- The agent reasoned that `gslc_DrvPasteSurface` invokes `SDL_BlitSurface`, which honors the active SDL1 clip rectangle (body of `gslc_DrvPasteSurface` not shown).
- `src/GUIslice_drv_sdl.c` sets `pGui->bRedrawPartialEn = true` under `DRV_DISP_SDL1`.
- `src/GUIslice_drv_sdl.c` sets `pGui->bRedrawPartialEn = false` under `DRV_DISP_SDL2`.
- `src/GUIslice_drv_adagfx.cpp` sets `pGui->bRedrawPartialEn = true`.
- `src/GUIslice_drv_m5stack.cpp` sets `pGui->bRedrawPartialEn = true`.
- `src/GUIslice_drv_tft_espi.cpp` sets `pGui->bRedrawPartialEn = true`.
- `src/GUIslice_drv_utft.cpp` sets `pGui->bRedrawPartialEn = true`.
- The agent reasoned that non-SDL drivers such as Adafruit have no-op `gslc_DrvPageFlipNow` implementations (bodies not shown).
- Based on the agent's finding (the file read of `src/GUIslice.h` was truncated at the config include), `src/GUIslice.h` includes `GUIslice_config.h`, which loads a selected stock config such as `configs/linux-sdl1-default-mouse.h` or a user config via `USER_CONFIG_LOADED`.
- `src/GUIslice.h` already defines fallback default macros such as `GSLC_FEATURE_FOCUS_ON_TOUCH` after config inclusion.
- `src/GUIslice.h` already performs `#error` configuration validation checks after config inclusion.
- `src/GUIslice_drv_sdl.h` includes `GUIslice.h`, so definitions in `src/GUIslice.h` are visible to the SDL driver.
- The Linux environment has `gcc (Debian 12.2.0-14+deb12u1) 12.2.0` installed.
- The Linux environment has `libsdl1.2-dev` installed.
- The Linux environment has `libsdl-ttf2.0-dev` installed.
- The Linux environment has `libsdl2-dev` installed.
- The Linux environment has `libsdl2-ttf-dev` installed.
- `examples/linux/Makefile` builds with `CC = gcc`.
- `examples/linux/Makefile` accepts `GSLC_DRV=(SDL1,SDL2)` to select the display driver.
- `examples/linux/Makefile` defines `GSLC_CORE = ../../src/GUIslice.c ../../src/GUIslice_config.h ../../src/elem/*.c`.
- `examples/linux/` contains `test_sdl1.c`.
- `examples/linux/` contains `test_sdl2.c`.
- `examples/linux/` contains a non-contiguous set of 19 Linux example C files (ex01–ex11, ex15, ex18, ex22, ex24, ex27, ex31, ex42, ex43).

### Settled Design Decisions
- Place `#ifndef GSLC_INVALIDATE_RGN_MAX` defaulting to `8` in `src/GUIslice.h` right after `#include "GUIslice_config.h"` because user config headers and compiler `-D` defines precede it and drivers include `src/GUIslice.h` transitively without editing 80+ stock config headers.
- Place a `#if (GSLC_INVALIDATE_RGN_MAX < 1) || (GSLC_INVALIDATE_RGN_MAX > 32)` `#error` guard in `src/GUIslice.h` immediately after the `GSLC_INVALIDATE_RGN_MAX` default because invalid bounds must fail at compile time for any configuration header or compiler define.
- Replace `rInvalidateRect` in `gslc_tsGui` (`src/GUIslice.h`) with `gslc_tsRect asInvalidateRgn[GSLC_INVALIDATE_RGN_MAX]` to store bounded regions without dynamic allocation.
- Add `uint8_t nInvalidateRgnCnt` in `gslc_tsGui` (`src/GUIslice.h`) to track the number of active regions.
- Keep `bool bInvalidateEn` in `gslc_tsGui` with the invariant `bInvalidateEn == (nInvalidateRgnCnt > 0)`.
- Modifying `gslc_tsGui` layout is acceptable because `rInvalidateRect` has no external callers outside `src/GUIslice.c` and `src/GUIslice.h` and the agent noted GUIslice is source-distributed.
- Add an internal hold flag in `gslc_tsGui` (tentatively called `bRedrawRgnHold`) so multi-region partial redraws preserve pending element redraw flags across passes.
- In `src/GUIslice.c::gslc_ElemSetRedraw`, return early inside the `GSLC_REDRAW_NONE` branch when the hold flag is active so clearing and `pElemRefParent` propagation are deferred until the final region pass.
- In `src/GUIslice.c::gslc_PageRedrawGo`, set the hold flag to `true` for every region pass except the last so pending element redraw flags remain intact for subsequent regions.
- In `src/GUIslice.c::gslc_PageRedrawGo`, set the hold flag to `false` on the final region pass and after the loop so pending element redraw flags clear naturally on the last pass.
- Rejected storing a 2-bit redraw snapshot in spare bits 8 and 9 of `eElemFlags` because `src/GUIslice.c::gslc_SetElemRefFlag` truncates `pElemRef->eElemFlags` to `uint8_t`, which would clobber higher bits on flag updates.
- Rejected per-page fixed static bitmaps because element count per page is unknown at compile time.
- Rejected variable-length arrays (VLAs) because the agent reasoned that the codebase targets C89/C++ and dynamic allocation is disallowed.
- In `src/GUIslice.c::gslc_InvalidateRgnAdd`, clamp `rAddRect` to `[0, 0, nDispW, nDispH]`.
- In `src/GUIslice.c::gslc_InvalidateRgnAdd`, drop any clamped rectangle that is empty or fully offscreen without enabling invalidation.
- In `src/GUIslice.c::gslc_InvalidateRgnAdd`, include each valid clamped rectangle in the working region set before coalescing and overflow pruning.
- In `src/GUIslice.c::gslc_InvalidateRgnAdd`, run transitive coalescing via `static void gslc_InvalidateRgnCoalesce(gslc_tsGui* pGui)` to fixpoint on positive-area overlap after adding the clamped rectangle.
- In `src/GUIslice.c::gslc_InvalidateRgnAdd`, while `nInvalidateRgnCnt > GSLC_INVALIDATE_RGN_MAX`, run `static void gslc_InvalidateRgnForceMerge(gslc_tsGui* pGui)` to merge the minimum-waste pair with post-merge `gslc_InvalidateRgnCoalesce`.
- Use `uint32_t` area arithmetic for forced-merge wasted-area calculations (`(union bbox area) - (area A) - (area B)`) because 16-bit edges fit safely within `uint32_t` products.
- Define static helper `static int gslc_InvalidateRgnCmp(const gslc_tsRect r1, const gslc_tsRect r2)` in `src/GUIslice.c` returning `-1`/`0`/`1` ascending by `y`, then `x`, then `h`, then `w`.
- Define static helper `static bool gslc_InvalidateRgnOverlap(gslc_tsRect a, gslc_tsRect b)` in `src/GUIslice.c` to test positive-area intersection between two rectangles.
- Define static helper `static gslc_tsRect gslc_InvalidateRgnUnion(gslc_tsRect a, gslc_tsRect b)` in `src/GUIslice.c` to compute the bounding-box union of two rectangles.
- Remove the redundant trailing `pGui->bInvalidateEn = true` statement in `src/GUIslice.c::gslc_InvalidateRgnPage` because force-enabling after an empty page bound is dropped would violate `bInvalidateEn == (nInvalidateRgnCnt > 0)`.
- Keep `src/GUIslice.c::gslc_InvalidateRgnPage` delegating directly to `gslc_InvalidateRgnAdd(pGui, pPage->rBounds)` so page invalidation goes through the single clamping and coalescing path.
- Keep the internal `asInvalidateRgn` array unsorted during mutations because centralizing sorting simplifies mutation logic and drawing order of disjoint regions does not affect rendered output.
- Implement `uint8_t gslc_InvalidateRgnGet(gslc_tsGui* pGui, gslc_tsRect* paRects, uint8_t nMax)` in `src/GUIslice.c` to insertion-sort a local stack copy (at most 32 rectangles) of active regions into canonical order because callers require sorted output without dynamic allocation.
- Implement `gslc_InvalidateRgnCount` to return `pGui->bInvalidateEn ? pGui->nInvalidateRgnCnt : 0`.
- Snapshot active regions into a local `gslc_tsRect asRgn[GSLC_INVALIDATE_RGN_MAX]` via `gslc_InvalidateRgnGet` at the start of `src/GUIslice.c::gslc_PageRedrawGo` so loop iteration stays isolated from any mid-pass region mutations.
- In `src/GUIslice.c::gslc_PageRedrawGo`, when there are zero active invalidation regions, set full-display clipping via `gslc_SetClipRect(pGui, NULL)` so elements draw normally across the display.
- In `src/GUIslice.c::gslc_PageRedrawGo`, when there are zero active invalidation regions, set `bRedrawRgnHold` to `false` so pending element redraw flags clear on the single pass.
- In `src/GUIslice.c::gslc_PageRedrawGo`, when there are zero active invalidation regions, run the normal single-pass background redraw when `bPageRedraw` is true.
- In `src/GUIslice.c::gslc_PageRedrawGo`, when there are zero active invalidation regions, dispatch the normal stack-page draw events.
- In `src/GUIslice.c::gslc_PageRedrawGo`, restore full-display clipping via `gslc_SetClipRect(pGui, NULL)` before calling `gslc_PageFlipGo(pGui)` because the agent reasoned that SDL flip does not depend on the clip rectangle.
- In `src/GUIslice.c::gslc_PageRedrawGo`, reorder `gslc_InvalidateRgnReset(pGui)` to execute after `gslc_PageFlipGo(pGui)` so active regions remain populated during screen presentation.
- Update the `DBG_REDRAW` diagnostics block in `src/GUIslice.c::gslc_PageRedrawGo` because it currently references the removed `rInvalidateRect` field.
- In `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` under `DRV_DISP_SDL1`, read active regions via `gslc_InvalidateRgnGet` into a local stack array `asRgn[GSLC_INVALIDATE_RGN_MAX]` to avoid dynamic allocation.
- In `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` under `DRV_DISP_SDL1`, call `SDL_UpdateRect` once per active region because the SDL1 screen surface uses `SDL_SWSURFACE`.
- In `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` under `DRV_DISP_SDL1`, fall back to `SDL_Flip(pScreen)` when `gslc_InvalidateRgnCount(pGui)` returns 0.
- Leave `DRV_DISP_SDL2` in `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` untouched because SDL2 is whole-display-only via `SDL_RenderPresent`.
- Leave non-SDL drivers untouched because the agent reasoned that their `gslc_DrvPageFlipNow` implementations are whole-display or no-ops.

### Work State
#### Completed
- Listed repository root directory.
- Listed `src/` directory.
- Listed `configs/` directory.
- Listed `examples/linux/` directory.
- Grepped `src/GUIslice.h` for invalidation declarations.
- Grepped `src/GUIslice.h` for configuration macros.
- Grepped `src/GUIslice.c` for invalidation calls.
- Grepped `src/GUIslice.c` for redraw functions.
- Grepped `src/GUIslice.c` for clip helpers.
- Grepped `src/GUIslice.c` for `gslc_SetElemRefFlag`.
- Grepped `src/` for `bRedrawPartialEn`.
- Grepped `src/` for `gslc_DrvPageFlipNow`.
- Grepped outside `src/GUIslice.c` and `src/GUIslice.h` for `rInvalidateRect`.
- Grepped outside `src/GUIslice.c` and `src/GUIslice.h` for `bInvalidateEn`.
- Read targeted sections of `src/GUIslice.h`.
- Read targeted sections of `src/GUIslice.c`.
- Read targeted sections of `src/GUIslice_drv_sdl.c`.
- Read `src/GUIslice_config.h`.
- Read `src/GUIslice_drv_sdl.h`.
- Read `configs/linux-sdl1-default-mouse.h`.
- Read `platformio.ini`.
- Read `examples/linux/Makefile`.
- Verified installed `gcc` compiler version.
- Verified installed `libsdl1.2-dev` development package.
- Verified installed `libsdl2-dev` development package.
- Checked `git log` showing head commit `4568d6f`.
- Checked `git status` showing a clean working tree.

#### Active
- Ready to begin implementing the bounded multi-region invalidation design.
- No code changes have been made to the repository yet.

#### Blocked
- Nothing is currently blocked.

### Next Steps
1. Add the `#ifndef GSLC_INVALIDATE_RGN_MAX` default of 8 to `src/GUIslice.h`.
2. Add the `[1, 32]` range-check `#error` guard for `GSLC_INVALIDATE_RGN_MAX` to `src/GUIslice.h`.
3. Replace `rInvalidateRect` with `asInvalidateRgn[GSLC_INVALIDATE_RGN_MAX]` in `gslc_tsGui` in `src/GUIslice.h`.
4. Add `uint8_t nInvalidateRgnCnt` to `gslc_tsGui` in `src/GUIslice.h`.
5. Add the internal redraw hold flag to `gslc_tsGui` in `src/GUIslice.h`.
6. Declare `gslc_InvalidateRgnCount` in `src/GUIslice.h`.
7. Declare `gslc_InvalidateRgnGet` in `src/GUIslice.h`.
8. Declare `gslc_InvalidateRgnIsDirty` in `src/GUIslice.h`.
9. Implement `gslc_InvalidateRgnCmp` in `src/GUIslice.c`.
10. Implement `gslc_InvalidateRgnOverlap` in `src/GUIslice.c`.
11. Implement `gslc_InvalidateRgnUnion` in `src/GUIslice.c`.
12. Implement `gslc_InvalidateRgnCoalesce` in `src/GUIslice.c`.
13. Implement `gslc_InvalidateRgnForceMerge` in `src/GUIslice.c`.
14. Update `gslc_InvalidateRgnReset` in `src/GUIslice.c`.
15. Update `gslc_InvalidateRgnScreen` in `src/GUIslice.c`.
16. Update `gslc_InvalidateRgnPage` in `src/GUIslice.c`.
17. Update `gslc_InvalidateRgnAdd` in `src/GUIslice.c`.
18. Implement `gslc_InvalidateRgnCount` in `src/GUIslice.c`.
19. Implement `gslc_InvalidateRgnGet` in `src/GUIslice.c`.
20. Implement `gslc_InvalidateRgnIsDirty` in `src/GUIslice.c`.
21. Add the hold-flag early return to the `GSLC_REDRAW_NONE` branch of `gslc_ElemSetRedraw` in `src/GUIslice.c`.
22. Restructure `gslc_PageRedrawGo` in `src/GUIslice.c` to iterate over the local `asRgn` snapshot with per-region clipping and hold-flag control.
23. Add the zero-active-region branch in `src/GUIslice.c::gslc_PageRedrawGo` setting full-display clipping via `gslc_SetClipRect(pGui, NULL)`.
24. Set `bRedrawRgnHold` to `false` in the zero-active-region branch of `src/GUIslice.c::gslc_PageRedrawGo`.
25. Dispatch the normal single-pass redraw in the zero-active-region branch of `src/GUIslice.c::gslc_PageRedrawGo`.
26. Restore full-display clipping via `gslc_SetClipRect(pGui, NULL)` before `gslc_PageFlipGo(pGui)` in `src/GUIslice.c::gslc_PageRedrawGo`.
27. Reorder `gslc_InvalidateRgnReset(pGui)` to run after `gslc_PageFlipGo(pGui)` in `src/GUIslice.c::gslc_PageRedrawGo`.
28. Update the `DBG_REDRAW` diagnostics in `src/GUIslice.c::gslc_PageRedrawGo` to remove references to `rInvalidateRect`.
29. Update `gslc_DrvPageFlipNow` under `DRV_DISP_SDL1` in `src/GUIslice_drv_sdl.c` to call `SDL_UpdateRect` once per active region.
30. Keep the `SDL_Flip(pScreen)` fallback in `src/GUIslice_drv_sdl.c::gslc_DrvPageFlipNow` when no active regions exist.
31. Compile with `gcc` against `libsdl1.2-dev` to verify the SDL1 build.
32. Compile with `gcc` against `libsdl2-dev` to verify the SDL2 build.

### Relevant Files
- `src/GUIslice.h`: configuration macro `GSLC_INVALIDATE_RGN_MAX` default to add.
- `src/GUIslice.h`: `GSLC_INVALIDATE_RGN_MAX` range-check `#error` guard to add.
- `src/GUIslice.h`: `gslc_tsGui` struct fields to update.
- `src/GUIslice.h`: public query function declarations to add.
- `src/GUIslice.c`: multi-region invalidation manager functions to implement.
- `src/GUIslice.c`: `gslc_ElemSetRedraw` hold-flag early return to add.
- `src/GUIslice.c`: `gslc_PageRedrawGo` multi-region redraw loop to implement.
- `src/GUIslice.c`: `gslc_PageRedrawGo` `DBG_REDRAW` diagnostics to update.
- `src/GUIslice.c`: `gslc_PageRedrawGo` flip/reset ordering to change.
- `src/GUIslice_drv_sdl.c`: SDL1 `gslc_DrvPageFlipNow` per-region `SDL_UpdateRect` presentation to implement.
- `src/GUIslice_config.h`: central configuration header included by `src/GUIslice.h`.
- `src/GUIslice_drv_sdl.h`: SDL driver header that includes `src/GUIslice.h`.
- `configs/linux-sdl1-default-mouse.h`: reference stock SDL1 configuration file.
- `examples/linux/Makefile`: Linux build reference for SDL1 compilation.
- `examples/linux/Makefile`: Linux build reference for SDL2 compilation.
