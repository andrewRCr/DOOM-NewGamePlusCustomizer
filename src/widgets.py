"""
widgets.py:
- reusable widget subclasses for the app
- DropdownMenu: styled CTkOptionMenu
- Checkbox: styled CTkCheckBox with tooltip
"""

from CTkToolTip import CTkToolTip
import customtkinter as ctk

from common import DARK_GRAY, RED, RED_HIGHLIGHT, FONT_SIZES


class DropdownMenu(ctk.CTkOptionMenu):
    """ App drop-down menu widget base class. """

    def __init__(self, parent, values, command):

        self.dropdownWidgetFont = ctk.CTkFont(
            'Eternal UI Regular', FONT_SIZES['Dropdowns'])

        super().__init__(
            master=parent,
            fg_color=DARK_GRAY,
            button_color=RED,
            button_hover_color=RED_HIGHLIGHT,
            font=self.dropdownWidgetFont,
            values=values,
            command=command,
            dropdown_font=self.dropdownWidgetFont)


class Checkbox(ctk.CTkCheckBox):
    """ App checkbox widget base class. """

    def __init__(
            self,
            parent,
            text,
            column,
            row,
            command,
            tooltipMsg,
            padx: tuple = (20, 0),
            pady: tuple = (0, 0),
            sticky=None,
            state='normal',
            font=None,
            checkboxHeight=24,
            checkboxWidth=24):

        if font is None:
            font = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Checkboxes'])

        super().__init__(
            master=parent,
            fg_color=RED,
            hover_color=RED_HIGHLIGHT,
            font=font,
            text=text,
            command=command,
            state=state,
            checkbox_height=checkboxHeight,
            checkbox_width=checkboxWidth)

        self.grid(column=column, row=row, padx=padx, pady=pady, sticky=sticky)
        tooltipText = tooltipMsg
        CTkToolTip(self, message=tooltipText)
