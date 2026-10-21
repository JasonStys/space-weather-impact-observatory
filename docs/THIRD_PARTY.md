# Third-party material and redistribution

Original application code by Jason Stys is MIT-licensed. Original NOAA/NWS responses are public-domain government information attributed separately in [DATA.md](DATA.md); they are not covered by the author's copyright claim. NWS reuse conditions include attribution/no false endorsement/no presenting modified data as official. No government logos are bundled.

The Python runtime is the CPython standard library, with its license in `licenses/PYTHON.txt`. Frozen applications include that notice, the project license and PyInstaller's actual installed distribution `COPYING.txt`, selected during packaging. PyInstaller uses its GPL-with-bootloader-exception terms; redistribution notices are included rather than asserting all bundled runtime bytes are original MIT code.

The browser is compiled from original TypeScript/HTML/CSS/SVG with no external fonts, images or runtime UI framework. Pinned development dependencies include TypeScript, Vite, Vitest, Prettier, Playwright and axe; their package licenses remain in the installed distributions and lock graph. Python development/testing includes pytest, Hypothesis, Ruff, mypy, coverage, pip-audit and PyInstaller with a hashed universal dev lock. These build/test tools do not imply that all their libraries are embedded in the final browser bundle. The original responses and actual screenshots are included; no third-party photos or generated artwork is used.

Source/product definitions: [NOAA planetary Kp](https://www.swpc.noaa.gov/products/planetary-k-index), [NOAA scales](https://www.swpc.noaa.gov/noaa-scales-explanation), [NWS reuse notice](https://www.weather.gov/disclaimer/). No NOAA, NASA, government, military, contractor or data-provider endorsement/affiliation is implied.
