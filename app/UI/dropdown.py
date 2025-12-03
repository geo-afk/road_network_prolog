import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, W, BOTH, X, RIGHT, Y, END

import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchableDropdown(ttk.Frame):
    def __init__(
        self,
        parent,
        values,
        textvariable,
        bootstyle="primary",
        placeholder="Search or select...",
    ):
        super().__init__(parent)
        self.values = sorted(values, key=str.lower)
        self.textvariable = textvariable
        self.bootstyle = bootstyle
        self.placeholder = placeholder
        self.filtered_values = self.values[:]
        self.popup = None
        self.is_open = False
        self.animation_id = None
        self.has_placeholder = False

        # Main container with subtle styling
        self.container = ttk.Frame(self, bootstyle="secondary")  # type: ignore
        self.container.pack(fill=BOTH, expand=True)

        # Entry with placeholder support
        self.entry = ttk.Entry(
            self.container,
            textvariable=textvariable,
            font=("Segoe UI", 11),
            foreground="gray60",
        )
        self.entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 2))

        # Set initial placeholder
        if not self.textvariable.get():
            self._set_placeholder()

        # Bind events
        self.entry.bind("<KeyRelease>", self.on_keyrelease)
        self.entry.bind("<Down>", self._handle_down_key)
        self.entry.bind("<Up>", self._handle_up_key)
        self.entry.bind("<Return>", self._handle_return_key)
        self.entry.bind("<Escape>", lambda e: self.hide_listbox())
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Button-1>", lambda e: self.toggle_listbox())

        # Modern dropdown button with icon
        self.arrow_btn = ttk.Button(
            self.container,
            text="▼",
            width=3,
            bootstyle=bootstyle,  # type: ignore
            command=self.toggle_listbox,
        )
        self.arrow_btn.pack(side=RIGHT)

        # Variable trace for filtering
        self.textvariable.trace_add(
            "write", lambda *_: self.after(10, self.filter_list)
        )

        # Add subtle shadow effect (visual only)
        self.container.configure(relief="flat", borderwidth=1)

    def _set_placeholder(self):
        """Set placeholder text in gray"""
        if not self.textvariable.get():
            self.has_placeholder = True
            self.entry.configure(foreground="gray60")
            self.entry.insert(0, self.placeholder)

    def _clear_placeholder(self):
        """Clear placeholder text"""
        if self.has_placeholder:
            self.has_placeholder = False
            self.entry.configure(foreground="black")
            # Delete the placeholder text
            self.entry.delete(0, END)
            self.textvariable.set("")

    def _on_focus_in(self, event):
        """Handle focus in - clear placeholder"""
        if self.has_placeholder:
            self._clear_placeholder()

    def _on_focus_out(self, event):
        """Handle focus out - restore placeholder if empty"""
        if not self.textvariable.get():
            self._set_placeholder()

    def _handle_down_key(self, event):
        """Navigate down in listbox"""
        if not self.popup or not self.popup.winfo_exists():
            self.show_listbox()
        elif hasattr(self, "listbox"):
            current = self.listbox.curselection()
            if current:
                next_idx = min(current[0] + 1, self.listbox.size() - 1)
            else:
                next_idx = 0
            self.listbox.selection_clear(0, END)
            self.listbox.selection_set(next_idx)
            self.listbox.see(next_idx)
        return "break"

    def _handle_up_key(self, event):
        """Navigate up in listbox"""
        if hasattr(self, "listbox") and self.popup and self.popup.winfo_exists():
            current = self.listbox.curselection()
            if current:
                prev_idx = max(current[0] - 1, 0)
                self.listbox.selection_clear(0, END)
                self.listbox.selection_set(prev_idx)
                self.listbox.see(prev_idx)
            return "break"

    def _handle_return_key(self, event):
        """Select current item on Enter"""
        if hasattr(self, "listbox") and self.popup and self.popup.winfo_exists():
            self.on_select()
            return "break"

    def filter_list(self):
        """Filter list based on input"""
        if self.has_placeholder:
            self.filtered_values = self.values[:]
            return

        term = self.textvariable.get().lower().strip()
        if not term:
            self.filtered_values = self.values[:]
        else:
            # Smart filtering: prioritize starts-with, then contains
            starts_with = [v for v in self.values if v.lower().startswith(term)]
            contains = [
                v for v in self.values if term in v.lower() and v not in starts_with
            ]
            self.filtered_values = starts_with + contains

        if self.popup and self.popup.winfo_exists():
            self.update_listbox()
            # Adjust height dynamically based on filtered results
            self._adjust_popup_height()
            # Show "No results" message if needed
            if not self.filtered_values:
                self._show_no_results()

    def _show_no_results(self):
        """Display no results message"""
        if hasattr(self, "listbox"):
            self.listbox.delete(0, END)
            self.listbox.insert(END, "No results found")
            self.listbox.itemconfig(0, foreground="gray")

    def _adjust_popup_height(self):
        """Dynamically adjust popup height based on filtered results"""
        if not self.popup or not self.popup.winfo_exists():
            return

        # Calculate new height
        display_count = (
            len(self.filtered_values) if self.filtered_values else len(self.values)
        )
        item_count = min(display_count, 10)
        new_height = max(min(item_count * 24 + 10, 240), 100)

        # Get current geometry
        x = self.popup.winfo_x()
        y = self.popup.winfo_y()
        w = self.popup.winfo_width()

        # Update geometry with new height
        self.popup.wm_geometry(f"{w}x{new_height}+{x}+{y}")

    def on_keyrelease(self, event):
        """Handle key release events"""
        if event.keysym in ("Down", "Up", "Return", "Tab", "Escape"):
            return

        if self.has_placeholder:
            return

        self.filter_list()

        # Auto-show dropdown when typing
        if self.filtered_values and (not self.popup or not self.popup.winfo_exists()):
            self.show_listbox()

    def show_listbox(self):
        """Show dropdown with smooth animation"""
        if self.popup and self.popup.winfo_exists():
            return

        # Get positioning
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2
        w = self.winfo_width()

        # Create popup window
        self.popup = tk.Toplevel(self)
        self.popup.wm_overrideredirect(True)

        # Determine height based on items (max 240px, min 100px for empty/small lists)
        # Use all values count if filtered is empty to show proper height initially
        display_count = (
            len(self.filtered_values) if self.filtered_values else len(self.values)
        )
        item_count = min(display_count, 10)
        height = max(min(item_count * 24 + 10, 240), 100)

        self.popup.wm_geometry(f"{w}x{height}+{x}+{y}")
        self.is_open = True

        # Update arrow direction
        self.arrow_btn.configure(text="▲")

        # Add subtle shadow via frame styling
        shadow_frame = ttk.Frame(self.popup, bootstyle="secondary")  # type: ignore
        shadow_frame.pack(fill=BOTH, expand=True, padx=1, pady=1)

        # Main content frame
        frame = ttk.Frame(shadow_frame, bootstyle="light")  # type: ignore
        frame.pack(fill=BOTH, expand=True)

        # Modern styled listbox
        self.listbox = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            background="white",
            selectbackground="#0d6efd",
            selectforeground="white",
            highlightthickness=0,
            relief="flat",
            borderwidth=0,
            activestyle="none",
            selectborderwidth=0,
        )
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=2)

        # Scrollbar with modern styling
        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.listbox.yview,
            bootstyle="secondary-round",  # type: ignore
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.update_listbox()

        # Bindings
        self.listbox.bind("<ButtonRelease-1>", self.on_select)
        self.listbox.bind("<Double-Button-1>", self.on_select)
        self.listbox.bind("<Return>", self.on_select)
        self.listbox.bind("<Escape>", lambda e: self.hide_listbox())
        self.listbox.bind("<Motion>", self._on_mouse_motion)

        # Global click handler
        self.winfo_toplevel().bind("<Button-1>", self.on_global_click, "+")

        # Auto-select first item
        if self.filtered_values:
            self.listbox.selection_set(0)
            self.listbox.see(0)

        # Fade-in animation
        self._animate_open()

    def _animate_open(self):
        """Subtle fade-in animation"""
        # Note: Tkinter has limited animation support
        # This is a placeholder for potential future enhancement
        pass

    def _on_mouse_motion(self, event):
        """Highlight item on hover"""
        if hasattr(self, "listbox"):
            index = self.listbox.nearest(event.y)
            self.listbox.selection_clear(0, END)
            self.listbox.selection_set(index)

    def on_global_click(self, event):
        """Close dropdown when clicking outside"""
        if not self.popup or not self.popup.winfo_exists():
            return
        try:
            widget = self.popup.winfo_containing(event.x_root, event.y_root)
            if widget not in (self.popup, self.listbox):
                self.hide_listbox()
        except Exception as e:
            logger.error("Err in scrollbar: %s", e)
            self.hide_listbox()

    def update_listbox(self):
        """Update listbox contents"""
        if not hasattr(self, "listbox"):
            return

        self.listbox.delete(0, END)

        if not self.filtered_values:
            self._show_no_results()
            return

        # Limit to 100 items for performance
        display_items = self.filtered_values[:100]

        for item in display_items:
            self.listbox.insert(END, item)

        # Show count if truncated
        if len(self.filtered_values) > 100:
            self.listbox.insert(END, f"... and {len(self.filtered_values) - 100} more")
            last_idx = self.listbox.size() - 1
            self.listbox.itemconfig(last_idx, foreground="gray")

    def on_select(self, event=None):
        """Handle item selection"""
        if not hasattr(self, "listbox"):
            return

        sel = self.listbox.curselection()
        if sel:
            selected_text = self.listbox.get(sel[0])

            # Ignore placeholder items
            if selected_text in ("No results found",) or selected_text.startswith(
                "..."
            ):
                return

            self.has_placeholder = False
            self.entry.configure(foreground="black")
            self.textvariable.set(selected_text)
            self.hide_listbox()
            self.entry.focus_set()

    def hide_listbox(self):
        """Hide dropdown with animation"""
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
            self.is_open = False
            self.arrow_btn.configure(text="▼")

    def toggle_listbox(self):
        """Toggle dropdown visibility"""
        if self.popup and self.popup.winfo_exists():
            self.hide_listbox()
        else:
            # Clear placeholder first, then reset filtered values and show
            if self.has_placeholder:
                self._clear_placeholder()
            self.filtered_values = self.values[:]
            # Use after() to ensure placeholder is cleared before showing listbox
            self.after(10, self.show_listbox)


# Example usage
if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    root.title("Enhanced Searchable Dropdown Demo")
    root.geometry("500x400")

    # Sample data
    cities = [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Phoenix",
        "Philadelphia",
        "San Antonio",
        "San Diego",
        "Dallas",
        "San Jose",
        "Austin",
        "Jacksonville",
        "Fort Worth",
        "Columbus",
        "Charlotte",
        "San Francisco",
        "Indianapolis",
        "Seattle",
        "Denver",
        "Washington",
        "Boston",
        "Nashville",
        "Baltimore",
        "Oklahoma City",
        "Portland",
        "Las Vegas",
        "Louisville",
        "Milwaukee",
        "Albuquerque",
        "Tucson",
    ]

    # Create main frame
    main_frame = ttk.Frame(root, padding=40)
    main_frame.pack(fill=BOTH, expand=True)

    # Title
    title = ttk.Label(
        main_frame,
        text="Enhanced Searchable Dropdown",
        font=("Segoe UI", 18, "bold"),
        bootstyle="primary", # type: ignore
    )
    title.pack(pady=(0, 30))

    # Instruction
    instruction = ttk.Label(
        main_frame,
        text="Start typing to filter, use arrow keys to navigate",
        font=("Segoe UI", 10),
        bootstyle="secondary", # type: ignore
    )
    instruction.pack(pady=(0, 20))

    # Dropdown container
    dropdown_frame = ttk.Frame(main_frame)
    dropdown_frame.pack(fill=X, pady=10)

    # Label
    label = ttk.Label(dropdown_frame, text="Select City:", font=("Segoe UI", 11))
    label.pack(anchor=W, pady=(0, 5))

    # Dropdown
    selected = tk.StringVar()
    dropdown = SearchableDropdown(
        dropdown_frame,
        cities,
        selected,
        bootstyle="primary",
        placeholder="Search cities...",
    )
    dropdown.pack(fill=X)

    # Result display
    result_frame = ttk.Frame(main_frame)
    result_frame.pack(pady=30, fill=X)

    result_label = ttk.Label(
        result_frame, text="Selected: None", font=("Segoe UI", 12), bootstyle="info" # type: ignore
    )
    result_label.pack()

    def update_result(*args):
        if selected.get() and not dropdown.has_placeholder:
            result_label.config(text=f"Selected: {selected.get()}")
        else:
            result_label.config(text="Selected: None")

    selected.trace_add("write", update_result)

    root.mainloop()
