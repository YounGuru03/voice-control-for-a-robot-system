"""
============================================================================
Modern UI Widgets - Custom Components for Professional Interface
============================================================================
"""

import tkinter as tk
from tkinter import ttk
from ui_theme import MODERN_COLORS, MODERN_FONTS, SPACING

class ModernButton(tk.Button):
    """Modern flat button with hover effects"""
    
    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        # Color schemes for different button styles
        color_schemes = {
            "primary": {
                "bg": MODERN_COLORS["primary"],
                "fg": MODERN_COLORS["text_light"],
                "hover_bg": MODERN_COLORS["primary_dark"],
            },
            "success": {
                "bg": MODERN_COLORS["success"],
                "fg": MODERN_COLORS["text_light"],
                "hover_bg": "#45B369",
            },
            "danger": {
                "bg": MODERN_COLORS["danger"],
                "fg": MODERN_COLORS["text_light"],
                "hover_bg": "#D43F31",
            },
            "secondary": {
                "bg": MODERN_COLORS["bg_tertiary"],
                "fg": MODERN_COLORS["text_primary"],
                "hover_bg": MODERN_COLORS["border"],
            },
        }
        
        scheme = color_schemes.get(style, color_schemes["primary"])
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=MODERN_FONTS["body"],
            bg=scheme["bg"],
            fg=scheme["fg"],
            activebackground=scheme["hover_bg"],
            activeforeground=scheme["fg"],
            relief=tk.FLAT,
            bd=0,
            padx=SPACING["md"],
            pady=SPACING["sm"],
            cursor="hand2",
            **kwargs
        )
        
        self.default_bg = scheme["bg"]
        self.hover_bg = scheme["hover_bg"]
        
        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self['bg'] = self.hover_bg
    
    def _on_leave(self, e):
        self['bg'] = self.default_bg


class ModernCard(tk.Frame):
    """Modern card container with shadow effect"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=MODERN_COLORS["bg_primary"],
            relief=tk.FLAT,
            bd=0,
            **kwargs
        )
        
        # Add subtle border
        self.config(highlightbackground=MODERN_COLORS["border"], highlightthickness=1)


class ModernLabel(tk.Label):
    """Modern label with consistent styling"""
    
    def __init__(self, parent, text="", style="body", **kwargs):
        font_map = {
            "title": MODERN_FONTS["title"],
            "heading": MODERN_FONTS["heading"],
            "subheading": MODERN_FONTS["subheading"],
            "body": MODERN_FONTS["body"],
            "small": MODERN_FONTS["small"],
        }
        
        super().__init__(
            parent,
            text=text,
            font=font_map.get(style, MODERN_FONTS["body"]),
            bg=MODERN_COLORS["bg_primary"],
            fg=MODERN_COLORS["text_primary"],
            **kwargs
        )


class ModernEntry(tk.Entry):
    """Modern entry field with clean design"""
    
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(
            parent,
            font=MODERN_FONTS["body"],
            bg=MODERN_COLORS["bg_secondary"],
            fg=MODERN_COLORS["text_primary"],
            relief=tk.FLAT,
            bd=0,
            insertbackground=MODERN_COLORS["primary"],
            **kwargs
        )
        
        self.placeholder = placeholder
        self.placeholder_color = MODERN_COLORS["text_secondary"]
        self.default_fg = MODERN_COLORS["text_primary"]
        
        # Add padding effect
        self.config(highlightbackground=MODERN_COLORS["border"], highlightthickness=1)
        
        # Placeholder functionality
        if placeholder:
            self.insert(0, placeholder)
            self.config(fg=self.placeholder_color)
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, e):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)
    
    def _on_focus_out(self, e):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)


class ModernCombobox(ttk.Combobox):
    """Modern dropdown with clean styling"""
    
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(
            parent,
            values=values or [],
            font=MODERN_FONTS["body"],
            state="readonly",
            **kwargs
        )
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(
            "Modern.TCombobox",
            fieldbackground=MODERN_COLORS["bg_secondary"],
            background=MODERN_COLORS["primary"],
            foreground=MODERN_COLORS["text_primary"],
            arrowcolor=MODERN_COLORS["primary"],
            bordercolor=MODERN_COLORS["border"],
            lightcolor=MODERN_COLORS["bg_secondary"],
            darkcolor=MODERN_COLORS["bg_secondary"],
        )
        
        self.configure(style="Modern.TCombobox")


class StatusIndicator(tk.Canvas):
    """Animated status indicator dot"""
    
    def __init__(self, parent, size=12, **kwargs):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=MODERN_COLORS["bg_primary"],
            highlightthickness=0,
            **kwargs
        )
        
        self.size = size
        self.indicator = self.create_oval(
            2, 2, size-2, size-2,
            fill=MODERN_COLORS["text_secondary"],
            outline=""
        )
    
    def set_status(self, status="idle"):
        """Set status: idle, active, success, error"""
        colors = {
            "idle": MODERN_COLORS["text_secondary"],
            "active": MODERN_COLORS["info"],
            "success": MODERN_COLORS["success"],
            "error": MODERN_COLORS["danger"],
            "warning": MODERN_COLORS["warning"],
        }
        
        self.itemconfig(self.indicator, fill=colors.get(status, MODERN_COLORS["text_secondary"]))


class ModernProgressBar(tk.Canvas):
    """Custom progress bar with modern design"""
    
    def __init__(self, parent, width=200, height=4, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=MODERN_COLORS["bg_tertiary"],
            highlightthickness=0,
            **kwargs
        )
        
        self.width = width
        self.height = height
        self.progress = 0
        
        self.bar = self.create_rectangle(
            0, 0, 0, height,
            fill=MODERN_COLORS["primary"],
            outline=""
        )
    
    def set_progress(self, value):
        """Set progress 0-100"""
        self.progress = max(0, min(100, value))
        bar_width = (self.width * self.progress) / 100
        self.coords(self.bar, 0, 0, bar_width, self.height)


class IconLabel(tk.Label):
    """Label with emoji/icon support"""
    
    def __init__(self, parent, icon="", text="", **kwargs):
        full_text = f"{icon}  {text}" if icon else text
        super().__init__(
            parent,
            text=full_text,
            font=MODERN_FONTS["body"],
            bg=MODERN_COLORS["bg_primary"],
            fg=MODERN_COLORS["text_primary"],
            **kwargs
        )
