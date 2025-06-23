from __future__ import annotations
import tkinter as tk
from tkinter import Misc
import tkinter.ttk as ttk
from typing import Any, Union
from PIL import Image, ImageTk
import os
import sys


def resource_path(relative_path: str):
    try:
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class TkImage:
    instances: dict[str, TkImage] = {}

    def __init__(self, reference: str, path: str) -> None:
        try:
            self.image = ImageTk.PhotoImage(Image.open(resource_path(path[6:])))
        except Exception:
            self.image = ImageTk.PhotoImage(Image.open(resource_path(path)))

        TkImage.instances[reference] = self


class Label(tk.Label):
    instances: dict[str, Label] = {}

    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        super().__init__(parent, **kwargs)

        Label.instances[reference] = self

    @classmethod
    def remove(cls, reference: Union[str, None]):
        if reference:
            Label.instances[reference].destroy()
            del Label.instances[reference]
        else:
            for item in Label.instances.values():
                item.destroy()
            Label.instances = {}


class StandardLabel(Label):
    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        kwargs["borderwidth"] = 0
        kwargs["highlightthickness"] = 0
        kwargs["padx"] = 0
        kwargs["pady"] = 0
        kwargs["relief"] = "flat"
        super().__init__(reference, parent, **kwargs)


class Button(tk.Button):
    instances: dict[str, Button] = {}

    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        super().__init__(parent, **kwargs)
        self.reference = reference

        Button.instances[reference] = self

    @classmethod
    def remove(cls, reference: Union[str, None]):
        if reference:
            Button.instances[reference].destroy()
            del Button.instances[reference]
        else:
            for item in Button.instances.values():
                item.destroy()
            Button.instances = {}


class StandardButtons(Button):
    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        kwargs["borderwidth"] = 0
        kwargs["highlightthickness"] = 0
        kwargs["padx"] = 0
        kwargs["pady"] = 0
        kwargs["relief"] = "flat"
        super().__init__(reference, parent, **kwargs)


class ToggleButton(Button):
    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        kwargs["borderwidth"] = 0
        kwargs["highlightthickness"] = 0
        kwargs["padx"] = 0
        kwargs["pady"] = 0
        kwargs["relief"] = "flat"
        kwargs["image"] = TkImage(f"{reference}ToggleOff", r"Image\ToggleOff.jpg").image
        self.active: bool = False
        super().__init__(reference, parent, **kwargs)
        

    def toggle(self) -> None:
        if self.active:
            self.active = False
            self.configure(
                image=TkImage(
                    f"{self.reference}ToggleOff", r"Image\ToggleOff.jpg"
                ).image
            )
        else:
            self.active = True
            self.configure(
                image=TkImage(f"{self.reference}ToggleOn", r"Image\ToggleOn.jpg").image
            )
    






class TabButton(Button):
    def __init__(
        self,
        reference: str,
        parent: Union[Misc, None],
        LeftImage: TkImage,
        RightImage: TkImage,
        **kwargs: Any,
    ) -> None:
        kwargs["borderwidth"] = 0
        kwargs["highlightthickness"] = 0
        kwargs["padx"] = 0
        kwargs["pady"] = 0
        kwargs["relief"] = "flat"
        kwargs["image"] = LeftImage.image
        super().__init__(reference, parent, **kwargs)
        self.active: bool = False
        self.LeftImage = LeftImage
        self.RightImage = RightImage

    def toggle(self) -> None:
        if self.active:
            self.active = False
            self.configure(image=self.LeftImage.image)
        else:
            self.active = True
            self.configure(image=self.RightImage.image)


class Input(tk.Entry):
    instances: dict[str, Input] = {}

    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        super().__init__(parent, **kwargs)

        Input.instances[reference] = self

    @classmethod
    def remove(cls, reference: Union[str, None]):
        if reference:
            Input.instances[reference].destroy()
            del Input.instances[reference]
        else:
            for item in Input.instances.values():
                item.destroy()
            Input.instances = {}


class StandardInput(Input):
    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        kwargs["font"] = ("Arial CE", 14, "normal")
        kwargs["fg"] = "#5E6366"
        kwargs["borderwidth"] = 0
        kwargs["highlightthickness"] = 0
        kwargs["relief"] = "flat"
        super().__init__(reference, parent, **kwargs)


class Scale(ttk.Scale):  # by default range is 100
    instances: dict[str, Scale] = {}

    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        style = ttk.Style()
        style.configure(  # type: ignore
            "Custom.Horizontal.TScale", background="#FFFFFF"
        )
        if kwargs["orient"] == "horizontal":
            kwargs["style"] = "Custom.Horizontal.TScale"
        style = ttk.Style()
        style.configure("Custom.Vertical.TScale", background="#FFFFFF")  # type: ignore
        if kwargs["orient"] == "vertical":
            kwargs["style"] = "Custom.Vertical.TScale"
        super().__init__(parent, **kwargs)

        Scale.instances[reference] = self

    @classmethod
    def remove(cls, reference: Union[str, None]):
        if reference:
            Scale.instances[reference].destroy()
            del Scale.instances[reference]
        else:
            for item in Scale.instances.values():
                item.destroy()
            Scale.instances = {}


class dropdown(ttk.Combobox):
    instances: dict[str, dropdown] = {}

    def __init__(
        self, reference: str, parent: Union[Misc, None], **kwargs: Any
    ) -> None:
        super().__init__(parent, **kwargs)
        dropdown.instances[reference] = self

    @classmethod
    def remove(cls, reference: Union[str, None]):
        if reference:
            dropdown.instances[reference].destroy()
            del dropdown.instances[reference]
        else:
            for item in dropdown.instances.values():
                item.destroy()
            dropdown.instances = {}


class CheckBox(tk.Checkbutton):
    instances: dict[str, CheckBox] = {}
    def __init__( self, reference: str , parent : Misc | None, **kwargs: Any):
        kwargs["borderwidth"] = 0
        kwargs["highlightthickness"] = 0
        kwargs["padx"] = 0
        kwargs["pady"] = 0
        kwargs["relief"] = "flat"
        kwargs["offrelief"] = "flat"
        kwargs["overrelief"] = "flat"
        kwargs["bg"] = "#FFFFFF"
        kwargs["activebackground"] = "#FFFFFF"
        super().__init__(parent, **kwargs)

        CheckBox.instances[reference] = self

# root = tk.Tk()
# root.geometry("400x480")
# root.configure(bg="#FFFFFF")

# CheckBox("test", root).pack()

# root.mainloop()

# root.quit()
