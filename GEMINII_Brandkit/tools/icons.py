"""UI icons (WEB layer; the kit itself defines only the error icon).

24 px grid. Two families:
  line   2 px stroke, round caps and joins, currentColor. Navigation and actions.
  status solid shapes with the glyph knocked out (evenodd), currentColor. Status is carried by shape, not color.
The error icon follows kit page 11: solid circle with a knocked-out exclamation mark.
"""

LINE = {
    "menu": "M4 7h16M4 12h16M4 17h16",
    "close": "M6 6l12 12M18 6L6 18",
    "chevron-down": "M6 9l6 6 6-6",
    "chevron-right": "M9 6l6 6-6 6",
    "arrow-right": "M4 12h16M14 6l6 6-6 6",
    "arrow-up-right": "M7 17L17 7M8 7h9v9",
    "check": "M5 12.5l4.5 4.5L19 7.5",
    "plus": "M12 5v14M5 12h14",
    "minus": "M5 12h14",
    "search": "M10.5 4.5a6 6 0 1 0 0 12a6 6 0 1 0 0-12zM15 15l5 5",
    "mail": "M5 5h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2zM3.5 7.5l8.5 6 8.5-6",
}

CIRCLE = "M12 2a10 10 0 1 0 0 20a10 10 0 1 0 0-20z"
STATUS = {
    "error": CIRCLE + "M10.9 6.2h2.2v8h-2.2z" + "M12 15.9a1.3 1.3 0 1 0 0 2.6a1.3 1.3 0 1 0 0-2.6z",
    "success": CIRCLE + "M7.2 12.6l1.5-1.5 2.3 2.3 4.6-4.6 1.5 1.5-6.1 6.1z",
    "warning": "M12 2.5L22.5 20.5H1.5z" + "M10.9 8.8h2.2v5.6h-2.2z" + "M12 15.9a1.3 1.3 0 1 0 0 2.6a1.3 1.3 0 1 0 0-2.6z",
    "info": CIRCLE + "M12 6a1.3 1.3 0 1 0 0 2.6a1.3 1.3 0 1 0 0-2.6z" + "M10.9 10.4h2.2v7.2h-2.2z",
}

NAMES = list(LINE) + list(STATUS)
LABELS = {
    "menu": "Menu", "close": "Close", "chevron-down": "Chevron down", "chevron-right": "Chevron right",
    "arrow-right": "Arrow right", "arrow-up-right": "Arrow up right (external)", "check": "Check", "plus": "Plus",
    "minus": "Minus", "search": "Search", "mail": "Mail", "error": "Error", "success": "Success",
    "warning": "Warning", "info": "Information",
}


def _body(name):
    if name in LINE:
        return f'<path d="{LINE[name]}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    return f'<path d="{STATUS[name]}" fill="currentColor" fill-rule="evenodd"/>'


def single(name):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" '
            f'aria-label="{LABELS[name]}"><title>{LABELS[name]}</title>{_body(name)}</svg>\n')


def sprite():
    syms = "".join(f'<symbol id="{n}" viewBox="0 0 24 24">{_body(n)}</symbol>' for n in NAMES)
    return f'<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{syms}</svg>\n'
