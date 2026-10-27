# FontForge validation flags used here

Primary references: [Python API](https://fontforge.org/docs/scripting/python/fontforge.html) and [source enum](https://raw.githubusercontent.com/fontforge/fontforge/master/fontforge/splinefont.h).

The API defines 0x2 open contours, 0x4 intersections, 0x8 wrong direction, 0x10 flipped references, 0x20 missing extrema, 0x40 missing referenced glyphs, and 0x40000 coordinate range. The source enum additionally defines 0x80000 nonintegral editable-source coordinates and 0x100000 missing anchor. The physical-error mask used in validation is 0x4007e. Integer TTF physical results are checked separately from fractional editable SFD coordinates and partial anchor-class coverage. Nonzero missing-anchor results are not silently discarded or called a full positioning pass.
