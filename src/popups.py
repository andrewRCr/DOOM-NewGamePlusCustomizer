"""
popups.py:
- pop-up message window classes
- base popupMessage + error, info, and prompt variants
"""

import customtkinter as ctk
from PIL import Image

from common import (
    WHITE, DARK_GRAY, LIGHT_GRAY, RED, RED_HIGHLIGHT,
    FONT_SIZES, WINDOW_SIZE, resource_path
)


class popupMessage(ctk.CTkToplevel):
    """ Represents a top-level window containing a pop-up message. """

    def __init__(self, parent, width: int, height: int, xOffset: int, yOffset: int, message: str):

        super().__init__(master=parent)

        self.popupFont = ctk.CTkFont('Eternal UI Regular', FONT_SIZES['Popups'])
        self.mainAppWindow = parent

        # setup window size / position
        self.width = width
        self.height = height
        spawn_x = int(self.mainAppWindow.winfo_width() * .5 +
                      self.mainAppWindow.winfo_x() - .5 * self.width) + xOffset
        spawn_y = int(self.mainAppWindow.winfo_height() * .5 +
                      self.mainAppWindow.winfo_y() - .5 * self.height) + yOffset
        self.geometry(f'{self.width}x{self.height}+{spawn_x}+{spawn_y}')

        # set appearance
        ctk.set_appearance_mode('dark')
        self.transparentColor = self._apply_appearance_mode(self.cget("fg_color"))
        self.attributes("-transparentcolor", self.transparentColor)
        self.cornerRadius = 15
        self.overrideredirect(True)

        # setting up frame for widgets
        self.popupFrame = ctk.CTkFrame(
            self,
            corner_radius=self.cornerRadius,
            width=self.width,
            height=self.height,
            fg_color=DARK_GRAY,
            bg_color=self.transparentColor,
            border_width=2,
            border_color=WHITE)
        self.popupFrame.pack(fill='both', expand=True)


class errorPopupMsg(popupMessage):
    """ 'Error' pop-up type specific class. """

    def __init__(self, parent, xOffset: int, yOffset: int, message: str):

        super().__init__(
            parent=parent,
            width=500,
            height=140,
            xOffset=xOffset,
            yOffset=yOffset,
            message=message)

        messageImage = ctk.CTkImage(
            light_image=Image.open(resource_path('images/info.png')),
            dark_image=Image.open(resource_path('images/info.png')))

        self.imageLabel = ctk.CTkLabel(
            self.popupFrame, image=messageImage, text='', anchor='w')
        self.imageLabel.grid(column=0, row=0, padx=20, pady=20)

        self.messageLabel = ctk.CTkLabel(
            self.popupFrame, font=self.popupFont, text=f'{message}', wraplength=400, padx=5, pady=5)
        self.messageLabel.grid(column=1, row=0, pady=20, sticky='w')

        self.okButton = ctk.CTkButton(self.popupFrame, font=self.popupFont, text='OK',
                                      fg_color=RED, hover_color=RED_HIGHLIGHT, command=self.destroy)
        self.okButton.grid(column=1, row=1)


class infoPopupMsg(popupMessage):
    """ 'Info' pop-up type specific class. """

    def __init__(self, parent, xOffset: int, yOffset: int, message: str):

        message = message  # + "making this extra long for no reason other than to test wrapping etc etc etc etc"

        super().__init__(
            parent=parent,
            width=520,
            height=120,
            xOffset=xOffset,
            yOffset=yOffset,
            message=message)

        messageImage = ctk.CTkImage(
            light_image=Image.open(resource_path('images/slayer_icon.png')),
            dark_image=Image.open(resource_path('images/slayer_icon.png')),
            size=(60, 60))

        self.imageLabel = ctk.CTkLabel(self.popupFrame, image=messageImage, text='')
        self.imageLabel.grid(column=0, row=0, padx=(10, 0), pady=(20, 0))

        self.messageLabel = ctk.CTkLabel(
            self.popupFrame, font=self.popupFont, text=f'{message}', wraplength=400, padx=0, pady=0)
        self.messageLabel.grid(column=1, row=0, padx=(40, 0), pady=10, sticky='nsew')

        self.okButton = ctk.CTkButton(self.popupFrame, font=self.popupFont, text='OK',
                                      fg_color=RED, hover_color=RED_HIGHLIGHT, command=self.destroy)
        self.okButton.grid(column=0, row=1, padx=(
            120, 0), pady=(0, 15), columnspan=2)


class promptPopupMsg(popupMessage):
    """ Prompt pop-up type specific class. """

    def __init__(self, parent, xOffset: int, yOffset: int, message: str):

        super().__init__(
            parent=parent,
            width=520,
            height=130,
            xOffset=xOffset,
            yOffset=yOffset,
            message=message)

        messageImage = ctk.CTkImage(light_image=Image.open(resource_path('images/info.png')),
                                    dark_image=Image.open(resource_path('images/info.png')))

        self.imageLabel = ctk.CTkLabel(self.popupFrame, image=messageImage, text='')
        self.imageLabel.grid(column=0, row=0, padx=(30, 0), pady=(30, 0))

        self.messageLabel = ctk.CTkLabel(
            self.popupFrame, font=self.popupFont, text=f'{message}', wraplength=400, padx=0, pady=0)
        self.messageLabel.grid(column=1, row=0, padx=(
            30, 0), pady=(30, 0), sticky='w', columnspan=2)

        self.browseButton = ctk.CTkButton(self.popupFrame, width=80, font=self.popupFont, text='Browse',
                                          fg_color=RED, hover_color=RED_HIGHLIGHT, command=parent.promptUserForPath)
        self.browseButton.grid(column=1, row=1, padx=(40, 0), pady=(15, 15), sticky='e')

        self.cancelButton = ctk.CTkButton(self.popupFrame, width=80, font=self.popupFont,
                                          text='Cancel', fg_color=LIGHT_GRAY, hover_color=RED_HIGHLIGHT, command=self.destroy)
        self.cancelButton.grid(column=2, row=1, padx=(10, 0), pady=(15, 15), sticky='w')
