FONT = "Segoe UI"

PRIMARY = "#3A8C7E"
HOVER = "#5BA89A"
TINT = "#D4EDE6"
SUBTLE = "#EAF6F2"
BACKGROUND = "#FBFAF7"
CARD = "#FFFFFF"
WARM_ACCENT = "#E8A87C"

SUCCESS = "#5DAE8B"
WARNING = "#E8B84A"
DANGER = "#D67663"

TEXT_DARK = "#2D3A36"
TEXT_LIGHT = "#F5F1EA"      # Warm off-white, pairs with BACKGROUND
TEXT_MUTED = "#6B7B75"

# Primary variations
PRIMARY_DARK = "#2A6B61"     # Deeper teal for pressed states / emphasis
PRIMARY_DARKER = "#1F4F47"   # Strong contrast, headers on light bg
PRESSED = "#2F7268"          # Active/pressed button state

# Surface / neutral layers
SURFACE = "#F4F0E9"          # Slightly warmer than BACKGROUND, for sections
SURFACE_ALT = "#EDE7DD"      # Card alt / sidebar
BORDER = "#DDD6CB"           # Soft warm border
BORDER_STRONG = "#C4BCB0"    # Dividers, input borders
DIVIDER = "#E5DFD4"          # Subtle horizontal rules

# Accent variations (warm complement to teal)
ACCENT_HOVER = "#D9956A"     # Darker WARM_ACCENT for hover
ACCENT_TINT = "#F5DCC8"      # Light wash of warm accent
ACCENT_SUBTLE = "#FAEDE0"    # Very light warm wash for backgrounds

# Status tints (for badges, alert backgrounds)
SUCCESS_TINT = "#D9EBE0"
SUCCESS_DARK = "#3F8B6B"
WARNING_TINT = "#F7E8C2"
WARNING_DARK = "#B8902F"
DANGER_TINT = "#F5D9D0"
DANGER_DARK = "#A8543F"

# Info (cool counterpart to warm accent, harmonized with teal)
INFO = "#6B9BB5"
INFO_TINT = "#D8E5ED"
INFO_DARK = "#4A7891"

# Text variations
TEXT_SUBTLE = "#94A099"      # Between MUTED and disabled
TEXT_DISABLED = "#B5BDB7"
TEXT_INVERSE = "#FBFAF7"     # For dark backgrounds
TEXT_LINK = "#3A8C7E"        # Same as PRIMARY, but named for clarity
TEXT_LINK_HOVER = "#2A6B61"

# Overlays / shadows (use with alpha if your toolkit supports it)
OVERLAY = "#2D3A36"          # Use at ~50% alpha for modals
SHADOW = "#2D3A36"           # Use at ~10-15% alpha
HIGHLIGHT = "#FFF8E8"        # Soft yellow highlight for selections

# Optional: dark mode counterparts
DARK_BG = "#1A2421"
DARK_SURFACE = "#243330"
DARK_CARD = "#2D3E3A"
DARK_BORDER = "#3D4F4A"

# Semantic aliases for specific use-cases
CANVAS_BG = SURFACE_ALT       # neutral backdrop behind images/PDFs
DRAG_INDICATOR = PRIMARY       # drag-and-drop insertion line

# Direct kwargs for ttk.Combobox — pass as **COMBOBOX
# Visual properties (colors, borders) require apply_combobox_style() called once at startup
COMBOBOX = {
    'font': (FONT, 10),
    'style': 'Ledgr.TCombobox',
    'cursor': 'hand2',
    'justify': 'left',
}

COMBOBOX_READONLY = {
    'font': (FONT, 10),
    'style': 'Ledgr.TCombobox',
    'cursor': 'hand2',
    'justify': 'left',
    'state': 'readonly',
}


def apply_combobox_style(style_engine) -> None:
    """Call once after root window is created to register the Ledgr.TCombobox style."""
    style_engine.theme_use('clam')  # clam required for fieldbackground to take effect
    style_engine.configure(
        'Ledgr.TCombobox',
        fieldbackground=CARD,
        background=SURFACE,
        foreground=TEXT_DARK,
        selectbackground=PRIMARY,
        selectforeground=TEXT_LIGHT,
        insertcolor=TEXT_DARK,
        arrowcolor=PRIMARY,
        bordercolor=BORDER_STRONG,
        relief='flat',
        padding=(6, 4),
    )
    style_engine.map(
        'Ledgr.TCombobox',
        fieldbackground=[('readonly', SUBTLE), ('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)],
        bordercolor=[('focus', PRIMARY)],
        arrowcolor=[('disabled', TEXT_DISABLED)],
    )


def apply_combobox_listbox_style(root) -> None:
    """Call once after root window is created to style the dropdown listbox."""
    root.option_add('*TCombobox*Listbox.background', CARD)
    root.option_add('*TCombobox*Listbox.foreground', TEXT_DARK)
    root.option_add('*TCombobox*Listbox.selectBackground', PRIMARY)
    root.option_add('*TCombobox*Listbox.selectForeground', TEXT_LIGHT)
    root.option_add('*TCombobox*Listbox.font', (FONT, 10))
    root.option_add('*TCombobox*Listbox.relief', 'flat')


def apply_styles(root) -> None:
    """Call once after the root Tk window is created to apply the full Ledgr theme."""
    import tkinter.ttk as ttk
    s = ttk.Style(root)
    s.theme_use('clam')

    s.configure('TFrame', background=BACKGROUND)
    s.configure('Card.TFrame', background=CARD)
    s.configure('Surface.TFrame', background=SURFACE)
    s.configure('Subtle.TFrame', background=SUBTLE)
    s.configure('Primary.TFrame', background=PRIMARY)
    s.configure('Bordered.Card.TFrame', background=CARD, relief='solid', borderwidth=1)

    s.configure('TLabel', background=BACKGROUND, foreground=TEXT_DARK, font=(FONT, 10))
    s.configure('Muted.TLabel', foreground=TEXT_MUTED, font=(FONT, 9))
    s.configure('Heading.TLabel', foreground=TEXT_DARK, font=(FONT, 13, 'bold'))
    s.configure('Subheading.TLabel', foreground=TEXT_MUTED, font=(FONT, 11))
    s.configure('Bold.TLabel', foreground=TEXT_DARK, font=(FONT, 10, 'bold'))
    s.configure('Subtle.TLabel', background=SUBTLE, foreground=TEXT_DARK, font=(FONT, 10))
    s.configure('Subtle.Muted.TLabel', background=SUBTLE, foreground=TEXT_MUTED, font=(FONT, 9))
    s.configure('Success.Badge.TLabel', background=SUCCESS_TINT, foreground=SUCCESS_DARK, font=(FONT, 8, 'bold'), padding=(6, 2))
    s.configure('Warning.Badge.TLabel', background=WARNING_TINT, foreground=WARNING_DARK, font=(FONT, 8, 'bold'), padding=(6, 2))
    s.configure('Danger.Badge.TLabel', background=DANGER_TINT, foreground=DANGER_DARK, font=(FONT, 8, 'bold'), padding=(6, 2))
    s.configure('Info.Badge.TLabel', background=INFO_TINT, foreground=INFO_DARK, font=(FONT, 8, 'bold'), padding=(6, 2))

    s.configure('TEntry',
        fieldbackground=CARD, foreground=TEXT_DARK, insertcolor=TEXT_DARK,
        bordercolor=BORDER_STRONG, selectbackground=PRIMARY, selectforeground=TEXT_LIGHT,
        padding=(6, 4))
    s.map('TEntry',
        bordercolor=[('focus', PRIMARY)],
        fieldbackground=[('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)])

    s.configure('TButton',
        background=PRIMARY, foreground=TEXT_LIGHT, font=(FONT, 10),
        borderwidth=0, relief='flat', padding=(12, 6), cursor='hand2')
    s.map('TButton',
        background=[('active', HOVER), ('pressed', PRESSED), ('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'flat')])

    s.configure('Danger.TButton',
        background=DANGER, foreground=TEXT_LIGHT, font=(FONT, 10),
        borderwidth=0, relief='flat', padding=(12, 6), cursor='hand2')
    s.map('Danger.TButton',
        background=[('active', DANGER_DARK), ('pressed', DANGER_DARK), ('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'flat')])

    s.configure('Success.TButton',
        background=SUCCESS, foreground=TEXT_LIGHT, font=(FONT, 10),
        borderwidth=0, relief='flat', padding=(12, 6), cursor='hand2')
    s.map('Success.TButton',
        background=[('active', SUCCESS_DARK), ('pressed', SUCCESS_DARK), ('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'flat')])

    s.configure('Warning.TButton',
        background=WARNING, foreground=TEXT_DARK, font=(FONT, 10),
        borderwidth=0, relief='flat', padding=(12, 6), cursor='hand2')
    s.map('Warning.TButton',
        background=[('active', WARNING_DARK), ('pressed', WARNING_DARK), ('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'flat')])

    s.configure('Ghost.TButton',
        background=BACKGROUND, foreground=PRIMARY, font=(FONT, 10),
        borderwidth=0, relief='flat', padding=(12, 6), cursor='hand2')
    s.map('Ghost.TButton',
        background=[('active', SUBTLE), ('pressed', SUBTLE), ('disabled', SURFACE)],
        foreground=[('active', PRIMARY_DARK), ('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'flat')])

    s.configure('Outline.TButton',
        background=CARD, foreground=PRIMARY, font=(FONT, 10),
        borderwidth=1, relief='solid', padding=(12, 5), cursor='hand2')
    s.map('Outline.TButton',
        background=[('active', PRIMARY), ('pressed', PRIMARY), ('disabled', SURFACE)],
        foreground=[('active', TEXT_LIGHT), ('pressed', TEXT_LIGHT), ('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'solid')])

    s.configure('Accent.TButton',
        background=WARM_ACCENT, foreground=TEXT_DARK, font=(FONT, 10),
        borderwidth=0, relief='flat', padding=(12, 6), cursor='hand2')
    s.map('Accent.TButton',
        background=[('active', ACCENT_HOVER), ('pressed', ACCENT_HOVER), ('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'flat')])

    s.configure('Table.TButton',
        background=PRIMARY, foreground=TEXT_LIGHT, font=(FONT, 10),
        borderwidth=0, relief='flat', padding=(8, 2), cursor='hand2')
    s.map('Table.TButton',
        background=[('active', HOVER), ('pressed', PRESSED), ('disabled', SURFACE)],
        foreground=[('disabled', TEXT_DISABLED)],
        relief=[('pressed', 'flat')])

    s.configure('Treeview',
        background=CARD, foreground=TEXT_DARK, fieldbackground=CARD,
        rowheight=28, font=(FONT, 10), borderwidth=0, relief='flat')
    s.configure('Treeview.Heading',
        background=SURFACE, foreground=TEXT_DARK, font=(FONT, 10, 'bold'),
        borderwidth=0, relief='flat')
    s.map('Treeview',
        background=[('selected', PRIMARY)],
        foreground=[('selected', TEXT_LIGHT)])
    s.map('Treeview.Heading',
        background=[('active', SURFACE_ALT)],
        relief=[('active', 'flat')])

    s.configure('TScrollbar',
        background=SURFACE, troughcolor=SURFACE_ALT, arrowcolor=PRIMARY,
        borderwidth=0, relief='flat')
    s.map('TScrollbar', background=[('active', HOVER)])

    s.configure('TLabelframe', background=BACKGROUND, bordercolor=BORDER, relief='groove')
    s.configure('TLabelframe.Label', background=BACKGROUND, foreground=TEXT_MUTED, font=(FONT, 9))

    s.configure('Card.TLabel', background=CARD, foreground=TEXT_DARK, font=(FONT, 10))
    s.configure('Card.Bold.TLabel', background=CARD, foreground=TEXT_DARK, font=(FONT, 10, 'bold'))
    s.configure('Card.Muted.TLabel', background=CARD, foreground=TEXT_MUTED, font=(FONT, 9))

    apply_combobox_style(s)
    apply_combobox_listbox_style(root)