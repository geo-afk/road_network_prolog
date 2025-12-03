import math
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from app.UI.dropdown import SearchableDropdown
from app.prolog.prolog_interface import RoadNetworkPathFinder
from ttkbootstrap.constants import LEFT, W, BOTH, X, CENTER, NSEW, RIGHT


class PathFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jamaican Rural Road Network Path-Finder")
        self.root.geometry("1200x850")
        self.root.minsize(1000, 750)

        # Configure root window to be responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        try:
            self.pathfinder = RoadNetworkPathFinder()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {e}")
            root.destroy()
            return

        self.last_path = None
        self.last_result = None
        self.animation_id = None
        self.create_widgets()

        # Bind configure event for dynamic canvas resizing
        self.path_canvas.bind("<Configure>", self.on_canvas_resize)

    def create_widgets(self):
        style = ttk.Style()

        # Enhanced styles
        style.configure("Modern.TLabel", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#6c757d")
        style.configure("SectionHeader.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Card.TFrame", relief="flat", borderwidth=0)

        # Main container - use grid for better control
        container = ttk.Frame(self.root, style="Card.TFrame")
        container.grid(row=0, column=0, sticky=NSEW, padx=0, pady=0)

        # Configure container to be fully responsive
        container.grid_rowconfigure(0, weight=0)  # Header - fixed size
        container.grid_rowconfigure(1, weight=1)  # Content - expands
        container.grid_columnconfigure(0, weight=1)

        # Header Section
        header_frame = ttk.Frame(container, style="Card.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(30, 10), padx=30)

        title_label = ttk.Label(
            header_frame,
            text="🗺️ Jamaican Rural Road Network",
            style="Title.TLabel",
            anchor=CENTER,
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            header_frame,
            text="Find the optimal route between locations using advanced pathfinding algorithms",
            style="Subtitle.TLabel",
            anchor=CENTER,
        )
        subtitle_label.pack(pady=(5, 0))

        # Main content area with responsive grid
        content_frame = ttk.Frame(container, style="Card.TFrame")
        content_frame.grid(row=1, column=0, sticky=NSEW, padx=30, pady=10)

        # Configure content_frame for responsive columns
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(
            0, weight=0, minsize=350
        )  # Left column - fixed width
        content_frame.grid_columnconfigure(1, weight=1)  # Right column - expands

        # Left Column - Input Controls
        left_column = ttk.Frame(content_frame, style="Card.TFrame")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # Add tabbed interface for Path Finding and Route Management
        notebook = ttk.Notebook(left_column)
        notebook.pack(fill=BOTH, expand=True)

        # Tab 1: Path Finding
        pathfind_tab = ttk.Frame(notebook, padding=10)
        notebook.add(pathfind_tab, text="🔍 Find Path")

        # Tab 2: Route Management
        manage_tab = ttk.Frame(notebook, padding=10)
        notebook.add(manage_tab, text="➕ Manage Routes")

        # === PATH FINDING TAB ===
        self._create_pathfinding_tab(pathfind_tab)

        # === ROUTE MANAGEMENT TAB ===
        self._create_route_management_tab(manage_tab)

        # Right Column - Results (RESPONSIVE)
        right_column = ttk.Frame(content_frame, style="Card.TFrame")
        right_column.grid(row=0, column=1, sticky=NSEW)

        # Configure right column for responsive layout
        right_column.grid_rowconfigure(0, weight=1)
        right_column.grid_columnconfigure(0, weight=1)

        results_card = ttk.LabelFrame(
            right_column,
            text="  📊 Path Visualization & Results  ",
            padding="20",
            bootstyle="success",
        )
        results_card.grid(row=0, column=0, sticky=NSEW)

        # Configure results_card for responsive content
        results_card.grid_rowconfigure(
            0, weight=2, minsize=200
        )  # Canvas area - 60% of space
        results_card.grid_rowconfigure(
            1, weight=1, minsize=150
        )  # Text area - 40% of space
        results_card.grid_columnconfigure(0, weight=1)

        # Canvas for visual path (RESPONSIVE)
        canvas_container = ttk.Frame(results_card)
        canvas_container.grid(row=0, column=0, sticky=NSEW, pady=(0, 15))

        # Configure canvas container
        canvas_container.grid_rowconfigure(0, weight=0)  # Label
        canvas_container.grid_rowconfigure(1, weight=1)  # Canvas
        canvas_container.grid_columnconfigure(0, weight=1)

        canvas_label = ttk.Label(
            canvas_container, text="Route Visualization", style="SectionHeader.TLabel"
        )
        canvas_label.grid(row=0, column=0, sticky=W, pady=(0, 10))

        self.path_canvas = tk.Canvas(
            canvas_container, bg="#f8f9fa", highlightthickness=0, relief="flat"
        )
        self.path_canvas.grid(row=1, column=0, sticky=NSEW)

        self.canvas_placeholder = self.path_canvas.create_text(
            300,
            100,
            text="🗺️  Your route will appear here after searching",
            font=("Segoe UI", 13),
            fill="#adb5bd",
            tags="placeholder",
        )

        # Textual results (RESPONSIVE)
        text_container = ttk.Frame(results_card)
        text_container.grid(row=1, column=0, sticky=NSEW, pady=(0, 10))

        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        # Main scrollable canvas
        details_canvas = tk.Canvas(text_container, highlightthickness=0, bg="#f8f9fa")
        details_canvas.grid(row=0, column=0, sticky=NSEW)

        # Scrollbars (only appear when needed)
        v_scrollbar = ttk.Scrollbar(
            text_container, orient="vertical", command=details_canvas.yview
        )
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = ttk.Scrollbar(
            text_container, orient="horizontal", command=details_canvas.xview
        )
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        details_canvas.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Inner frame that holds all content
        scrollable_frame = ttk.Frame(details_canvas, padding=20)
        canvas_window = details_canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="n", tags="content"
        )

        # This is the magic: reconfigure window position on resize
        def configure_scroll_region(event=None):
            details_canvas.configure(scrollregion=details_canvas.bbox("all"))

            # Get canvas and content sizes
            canvas_width = details_canvas.winfo_width()
            content_width = scrollable_frame.winfo_reqwidth()

            # Only center horizontally if content is narrower than canvas
            if content_width < canvas_width:
                x_offset = (canvas_width - content_width) // 2
                details_canvas.coords(canvas_window, x_offset, 0)
                details_canvas.itemconfigure(canvas_window, anchor="n")
            else:
                details_canvas.coords(canvas_window, 0, 0)
                details_canvas.itemconfigure(canvas_window, anchor="nw")

        scrollable_frame.bind("<Configure>", configure_scroll_region)
        details_canvas.bind("<Configure>", configure_scroll_region)

        # === MOUSE WHEEL SCROLLING (Cross-platform) ===
        def _on_mousewheel(event):
            details_canvas.yview_scroll(int(-1 * (event.delta or event.num)), "units")

        def _on_shift_mousewheel(event):
            details_canvas.xview_scroll(int(-1 * (event.delta or event.num)), "units")

        details_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows/Mac
        details_canvas.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
        details_canvas.bind(
            "<Button-4>", lambda e: details_canvas.yview_scroll(-1, "units")
        )  # Linux up
        details_canvas.bind(
            "<Button-5>", lambda e: details_canvas.yview_scroll(1, "units")
        )  # Linux down

        # Optional: improve scroll feel when hovering content
        scrollable_frame.bind(
            "<Enter>", lambda e: details_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        )
        scrollable_frame.bind(
            "<Leave>", lambda e: details_canvas.unbind_all("<MouseWheel>")
        )

        self.details_container = scrollable_frame
        details_canvas.focus_set()

    def _create_pathfinding_tab(self, parent):
        """Create the path finding interface"""
        # Location Selection Card
        location_card = ttk.LabelFrame(
            parent,
            text="  📍 Location Selection  ",
            padding="20",
            bootstyle="primary",
        )
        location_card.pack(fill=X, pady=(0, 15))

        locations = self.pathfinder.get_available_locations()

        # Start Location
        start_container = ttk.Frame(location_card)
        start_container.pack(fill=X, pady=(0, 15))

        start_label = ttk.Label(
            start_container,
            text="🚀 Starting Point",
            style="SectionHeader.TLabel",
            foreground="#28a745",
        )
        start_label.pack(anchor=W, pady=(0, 8))

        self.start_var = tk.StringVar()

        self.start_combo = SearchableDropdown(
            start_container,
            values=locations,
            textvariable=self.start_var,
            bootstyle="success",
        )
        self.start_combo.pack(fill=X, pady=(0, 10))
        self.start_combo.entry.configure(bootstyle="success")

        # Destination
        dest_container = ttk.Frame(location_card)
        dest_container.pack(fill=X)

        dest_label = ttk.Label(
            dest_container,
            text="🎯 Destination",
            style="SectionHeader.TLabel",
            foreground="#dc3545",
        )
        dest_label.pack(anchor=W, pady=(0, 8))

        self.goal_var = tk.StringVar()
        self.goal_combo = SearchableDropdown(
            dest_container,
            values=locations,
            textvariable=self.goal_var,
            bootstyle="danger",
        )
        self.goal_combo.pack(fill=X, pady=(0, 10))
        self.goal_combo.entry.configure(bootstyle="danger")

        # Algorithm Selection Card
        algo_card = ttk.LabelFrame(
            parent,
            text="  ⚙️ Algorithm Selection  ",
            padding="20",
            bootstyle="info",
        )
        algo_card.pack(fill=X, pady=(0, 15))

        self.algo_var = tk.StringVar(value="dijkstra")

        algorithms = [
            (
                "dijkstra",
                "Dijkstra's Algorithm",
                "Guaranteed shortest path (weighted)",
            ),
            ("astar", "A* Algorithm", "Fast heuristic search (weighted)"),
            ("bfs", "Breadth-First Search", "Unweighted exploration"),
        ]

        for i, (value, name, desc) in enumerate(algorithms):
            algo_frame = ttk.Frame(algo_card)
            algo_frame.pack(fill=X, pady=5)

            ttk.Radiobutton(
                algo_frame,
                text=name,
                variable=self.algo_var,
                value=value,
                bootstyle="info-toolbutton",
            ).pack(side=LEFT)

            ttk.Label(
                algo_frame,
                text=f"  —  {desc}",
                font=("Segoe UI", 9),
                foreground="#6c757d",
            ).pack(side=LEFT)

        # Avoidance Criteria Card
        criteria_card = ttk.LabelFrame(
            parent,
            text="  🚧 Avoidance Criteria  ",
            padding="20",
            bootstyle="warning",
        )
        criteria_card.pack(fill=X, pady=(0, 15))

        self.avoid_closed = tk.BooleanVar()
        self.avoid_unpaved = tk.BooleanVar()
        self.avoid_cisterns = tk.BooleanVar()
        self.avoid_potholes = tk.BooleanVar()

        criteria = [
            ("🚫 Closed Roads", self.avoid_closed),
            ("🛤️ Unpaved Roads", self.avoid_unpaved),
            ("💧 Broken Cisterns", self.avoid_cisterns),
            ("🕳️ Deep Potholes", self.avoid_potholes),
        ]

        for text, var in criteria:
            check_frame = ttk.Frame(criteria_card)
            check_frame.pack(fill=X, pady=4)

            ttk.Checkbutton(
                check_frame, text=text, variable=var, bootstyle="warning-round-toggle"
            ).pack(side=LEFT)

        # Search Button
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=15)

        self.search_btn = ttk.Button(
            button_frame,
            text="🔍 Find Optimal Path",
            command=self.find_path,
            bootstyle="success",
            width=30,
        )
        self.search_btn.pack()

        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results,
            bootstyle="secondary-outline",
            width=30,
        )
        self.clear_btn.pack(pady=(10, 0))

    def _create_route_management_tab(self, parent):
        """Create the route management interface"""
        # Scrollable container for the tab with proper geometry
        canvas = tk.Canvas(parent, highlightthickness=0, bg="#f8f9fa")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=10)

        def configure_scroll(*args):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ensure canvas is wide enough for dropdowns
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(scroll_window, width=canvas_width - 20)

        scrollable_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)

        scroll_window = canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw", width=330
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        scrollable_frame.bind("<Enter>", bind_mousewheel)
        scrollable_frame.bind("<Leave>", unbind_mousewheel)

        locations = self.pathfinder.get_available_locations()

        # === ADD ROAD CARD ===
        add_card = ttk.LabelFrame(
            scrollable_frame,
            text="  ➕ Add New Route  ",
            padding="20",
            bootstyle="success",
        )
        add_card.pack(fill=X, pady=(0, 15))

        # From Location
        from_container = ttk.Frame(add_card)
        from_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            from_container,
            text="From Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.add_from_var = tk.StringVar()
        self.add_from_combo = SearchableDropdown(
            from_container,
            values=locations,
            textvariable=self.add_from_var,
            bootstyle="primary",
            placeholder="Select starting location...",
        )
        self.add_from_combo.pack(fill=X)

        # To Location
        to_container = ttk.Frame(add_card)
        to_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            to_container,
            text="To Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.add_to_var = tk.StringVar()
        self.add_to_combo = SearchableDropdown(
            to_container,
            values=locations,
            textvariable=self.add_to_var,
            bootstyle="primary",
            placeholder="Select destination location...",
        )
        self.add_to_combo.pack(fill=X)

        # Distance
        dist_container = ttk.Frame(add_card)
        dist_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            dist_container,
            text="Distance (km):",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.add_distance_var = tk.StringVar()
        ttk.Entry(
            dist_container,
            textvariable=self.add_distance_var,
            font=("Segoe UI", 11),
        ).pack(fill=X)

        # Road Type
        type_container = ttk.Frame(add_card)
        type_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            type_container,
            text="Road Type:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.add_type_var = tk.StringVar(value="paved")
        type_frame = ttk.Frame(type_container)
        type_frame.pack(fill=X)

        road_types = [
            ("paved", "Paved"),
            ("unpaved", "Unpaved"),
            ("broken_cisterns", "Broken Cisterns"),
            ("deep_potholes", "Deep Potholes"),
        ]

        for value, label in road_types:
            ttk.Radiobutton(
                type_frame,
                text=label,
                variable=self.add_type_var,
                value=value,
                bootstyle="success-toolbutton",
            ).pack(side=LEFT, padx=5, pady=2)

        # Road Status
        status_container = ttk.Frame(add_card)
        status_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            status_container,
            text="Road Status:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.add_status_var = tk.StringVar(value="open")
        status_frame = ttk.Frame(status_container)
        status_frame.pack(fill=X)

        ttk.Radiobutton(
            status_frame,
            text="Open",
            variable=self.add_status_var,
            value="open",
            bootstyle="success-toolbutton",
        ).pack(side=LEFT, padx=5)

        ttk.Radiobutton(
            status_frame,
            text="Closed",
            variable=self.add_status_var,
            value="closed",
            bootstyle="danger-toolbutton",
        ).pack(side=LEFT, padx=5)

        # Add Button
        ttk.Button(
            add_card,
            text="➕ Add Route",
            command=self.add_route,
            bootstyle="success",
            width=25,
        ).pack(pady=(10, 0))

        # === UPDATE ROAD STATUS CARD ===
        update_card = ttk.LabelFrame(
            scrollable_frame,
            text="  🔄 Update Route Status  ",
            padding="20",
            bootstyle="warning",
        )
        update_card.pack(fill=X, pady=(0, 15))

        # From Location for Update
        update_from_container = ttk.Frame(update_card)
        update_from_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            update_from_container,
            text="From Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.update_from_var = tk.StringVar()
        self.update_from_combo = SearchableDropdown(
            update_from_container,
            values=locations,
            textvariable=self.update_from_var,
            bootstyle="primary",
            placeholder="Select starting location...",
        )
        self.update_from_combo.pack(fill=X)

        # To Location for Update
        update_to_container = ttk.Frame(update_card)
        update_to_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            update_to_container,
            text="To Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.update_to_var = tk.StringVar()
        self.update_to_combo = SearchableDropdown(
            update_to_container,
            values=locations,
            textvariable=self.update_to_var,
            bootstyle="primary",
            placeholder="Select destination location...",
        )
        self.update_to_combo.pack(fill=X)

        # New Status
        new_status_container = ttk.Frame(update_card)
        new_status_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            new_status_container,
            text="New Status:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.update_status_var = tk.StringVar(value="open")
        update_status_frame = ttk.Frame(new_status_container)
        update_status_frame.pack(fill=X)

        ttk.Radiobutton(
            update_status_frame,
            text="Open",
            variable=self.update_status_var,
            value="open",
            bootstyle="success-toolbutton",
        ).pack(side=LEFT, padx=5)

        ttk.Radiobutton(
            update_status_frame,
            text="Closed",
            variable=self.update_status_var,
            value="closed",
            bootstyle="danger-toolbutton",
        ).pack(side=LEFT, padx=5)

        # Update Button
        ttk.Button(
            update_card,
            text="🔄 Update Status",
            command=self.update_route_status,
            bootstyle="warning",
            width=25,
        ).pack(pady=(10, 0))

        # === UPDATE ROAD TYPE CARD ===
        update_type_card = ttk.LabelFrame(
            scrollable_frame,
            text="  🛠️ Update Route Type  ",
            padding="20",
            bootstyle="info",
        )
        update_type_card.pack(fill=X, pady=(0, 15))

        # From Location for Type Update
        type_from_container = ttk.Frame(update_type_card)
        type_from_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            type_from_container,
            text="From Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.type_from_var = tk.StringVar()
        self.type_from_combo = SearchableDropdown(
            type_from_container,
            values=locations,
            textvariable=self.type_from_var,
            bootstyle="primary",
            placeholder="Select starting location...",
        )
        self.type_from_combo.pack(fill=X)

        # To Location for Type Update
        type_to_container = ttk.Frame(update_type_card)
        type_to_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            type_to_container,
            text="To Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.type_to_var = tk.StringVar()
        self.type_to_combo = SearchableDropdown(
            type_to_container,
            values=locations,
            textvariable=self.type_to_var,
            bootstyle="primary",
            placeholder="Select destination location...",
        )
        self.type_to_combo.pack(fill=X)

        # New Type
        new_type_container = ttk.Frame(update_type_card)
        new_type_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            new_type_container,
            text="New Road Type:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.new_type_var = tk.StringVar(value="paved")
        new_type_frame = ttk.Frame(new_type_container)
        new_type_frame.pack(fill=X)

        for value, label in road_types:
            ttk.Radiobutton(
                new_type_frame,
                text=label,
                variable=self.new_type_var,
                value=value,
                bootstyle="info-toolbutton",
            ).pack(side=LEFT, padx=5, pady=2)

        # Update Type Button
        ttk.Button(
            update_type_card,
            text="🛠️ Update Type",
            command=self.update_route_type,
            bootstyle="info",
            width=25,
        ).pack(pady=(10, 0))

        # === DELETE ROAD CARD ===
        delete_card = ttk.LabelFrame(
            scrollable_frame,
            text="  🗑️ Delete Route  ",
            padding="20",
            bootstyle="danger",
        )
        delete_card.pack(fill=X, pady=(0, 15))

        # From Location for Delete
        delete_from_container = ttk.Frame(delete_card)
        delete_from_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            delete_from_container,
            text="From Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.delete_from_var = tk.StringVar()
        self.delete_from_combo = SearchableDropdown(
            delete_from_container,
            values=locations,
            textvariable=self.delete_from_var,
            bootstyle="primary",
            placeholder="Select starting location...",
        )
        self.delete_from_combo.pack(fill=X)

        # To Location for Delete
        delete_to_container = ttk.Frame(delete_card)
        delete_to_container.pack(fill=X, pady=(0, 10))

        ttk.Label(
            delete_to_container,
            text="To Location:",
            style="SectionHeader.TLabel",
        ).pack(anchor=W, pady=(0, 5))

        self.delete_to_var = tk.StringVar()
        self.delete_to_combo = SearchableDropdown(
            delete_to_container,
            values=locations,
            textvariable=self.delete_to_var,
            bootstyle="primary",
            placeholder="Select destination location...",
        )
        self.delete_to_combo.pack(fill=X)

        # Delete Button
        ttk.Button(
            delete_card,
            text="🗑️ Delete Route",
            command=self.delete_route,
            bootstyle="danger",
            width=25,
        ).pack(pady=(10, 0))

        # === UTILITY BUTTONS ===
        utility_card = ttk.LabelFrame(
            scrollable_frame,
            text="  💾 Utilities  ",
            padding="20",
            bootstyle="secondary",
        )
        utility_card.pack(fill=X, pady=(0, 15))

        button_frame = ttk.Frame(utility_card)
        button_frame.pack(fill=X)

        ttk.Button(
            button_frame,
            text="💾 Backup Prolog File",
            command=self.backup_prolog_file,
            bootstyle="info",
            width=25,
        ).pack(pady=5)

        ttk.Button(
            button_frame,
            text="📤 Export All Routes",
            command=self.export_routes,
            bootstyle="secondary",
            width=25,
        ).pack(pady=5)

        ttk.Button(
            button_frame,
            text="🔄 Refresh Locations",
            command=self._refresh_location_dropdowns,
            bootstyle="primary-outline",
            width=25,
        ).pack(pady=5)

    def add_route(self):
        """Add a new route to the network"""
        from_loc = self.add_from_var.get()
        to_loc = self.add_to_var.get()
        distance = self.add_distance_var.get()
        road_type = self.add_type_var.get()
        status = self.add_status_var.get()

        # Validation
        if not from_loc or not to_loc:
            messagebox.showwarning("Input Required", "Please select both locations.")
            return

        if from_loc == to_loc:
            messagebox.showwarning(
                "Invalid Route", "Starting and destination locations must be different."
            )
            return

        try:
            distance_float = float(distance)
            if distance_float <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning(
                "Invalid Distance",
                "Please enter a valid positive distance in kilometers.",
            )
            return

        # Convert location names to Prolog format
        from_loc_pl = self.pathfinder.unformat_name(from_loc)
        to_loc_pl = self.pathfinder.unformat_name(to_loc)

        # Add the route
        try:
            success = self.pathfinder.add_road(
                from_loc_pl, to_loc_pl, distance_float, road_type, status
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    f"Route added successfully!\n\nFrom: {from_loc}\nTo: {to_loc}\nDistance: {distance_float} km\nType: {road_type.replace('_', ' ').title()}\nStatus: {status.title()}\n\n✅ Changes saved to Prolog file.",
                )

                # Clear the form
                self.add_from_var.set("")
                self.add_to_var.set("")
                self.add_distance_var.set("")
                self.add_type_var.set("paved")
                self.add_status_var.set("open")

                # Refresh location dropdowns
                self._refresh_location_dropdowns()
            else:
                messagebox.showerror("Error", "Failed to add route. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_route_status(self):
        """Update the status of an existing route"""
        from_loc = self.update_from_var.get()
        to_loc = self.update_to_var.get()
        new_status = self.update_status_var.get()

        # Validation
        if not from_loc or not to_loc:
            messagebox.showwarning("Input Required", "Please select both locations.")
            return

        # Convert location names to Prolog format
        from_loc_pl = self.pathfinder.unformat_name(from_loc)
        to_loc_pl = self.pathfinder.unformat_name(to_loc)

        # Update the status
        try:
            success = self.pathfinder.update_road_status(
                from_loc_pl, to_loc_pl, new_status
            )

            if success:
                messagebox.showinfo(
                    "Success",
                    f"Route status updated successfully!\n\nFrom: {from_loc}\nTo: {to_loc}\nNew Status: {new_status.title()}\n\n✅ Changes saved to Prolog file.",
                )

                # Clear the form
                self.update_from_var.set("")
                self.update_to_var.set("")
                self.update_status_var.set("open")
            else:
                messagebox.showerror(
                    "Error", "Failed to update route status. Route may not exist."
                )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_route_type(self):
        """Update the type of an existing route"""
        from_loc = self.type_from_var.get()
        to_loc = self.type_to_var.get()
        new_type = self.new_type_var.get()

        # Validation
        if not from_loc or not to_loc:
            messagebox.showwarning("Input Required", "Please select both locations.")
            return

        # Convert location names to Prolog format
        from_loc_pl = self.pathfinder.unformat_name(from_loc)
        to_loc_pl = self.pathfinder.unformat_name(to_loc)

        # Update the type
        try:
            success = self.pathfinder.update_road_type(from_loc_pl, to_loc_pl, new_type)

            if success:
                messagebox.showinfo(
                    "Success",
                    f"Route type updated successfully!\n\nFrom: {from_loc}\nTo: {to_loc}\nNew Type: {new_type.replace('_', ' ').title()}\n\n✅ Changes saved to Prolog file.",
                )

                # Clear the form
                self.type_from_var.set("")
                self.type_to_var.set("")
                self.new_type_var.set("paved")
            else:
                messagebox.showerror(
                    "Error", "Failed to update route type. Route may not exist."
                )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def delete_route(self):
        """Delete a route from the network"""
        from_loc = self.delete_from_var.get()
        to_loc = self.delete_to_var.get()

        # Validation
        if not from_loc or not to_loc:
            messagebox.showwarning("Input Required", "Please select both locations.")
            return

        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete this route?\n\nFrom: {from_loc}\nTo: {to_loc}\n\n⚠️ This action cannot be undone!",
        )

        if not confirm:
            return

        # Convert location names to Prolog format
        from_loc_pl = self.pathfinder.unformat_name(from_loc)
        to_loc_pl = self.pathfinder.unformat_name(to_loc)

        # Delete the route
        try:
            success = self.pathfinder.delete_road(from_loc_pl, to_loc_pl)

            if success:
                messagebox.showinfo(
                    "Success",
                    f"Route deleted successfully!\n\nFrom: {from_loc}\nTo: {to_loc}\n\n✅ Changes saved to Prolog file.",
                )

                # Clear the form
                self.delete_from_var.set("")
                self.delete_to_var.set("")

                # Refresh location dropdowns
                self._refresh_location_dropdowns()
            else:
                messagebox.showerror(
                    "Error", "Failed to delete route. Route may not exist."
                )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def backup_prolog_file(self):
        """Create a backup of the Prolog file"""
        try:
            backup_file = self.pathfinder.backup_prolog_file()
            messagebox.showinfo(
                "Backup Created",
                f"Backup created successfully!\n\n📁 {backup_file}\n\nYou can restore from this file if needed.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")

    def export_routes(self):
        """Export all routes to a file"""
        from tkinter import filedialog

        try:
            # Ask user for file location
            export_file = filedialog.asksaveasfilename(
                defaultextension=".pl",
                filetypes=[("Prolog Files", "*.pl"), ("All Files", "*.*")],
                title="Export Routes To...",
            )

            if export_file:
                success = self.pathfinder.export_roads_to_file(export_file)

                if success:
                    messagebox.showinfo(
                        "Export Successful",
                        f"All routes exported successfully!\n\n📁 {export_file}",
                    )
                else:
                    messagebox.showerror("Error", "Failed to export routes.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _refresh_location_dropdowns(self):
        """Refresh all location dropdowns with updated locations"""
        try:
            locations = self.pathfinder.get_available_locations()

            # Update all dropdowns
            dropdowns = [
                self.start_combo,
                self.goal_combo,
                self.add_from_combo,
                self.add_to_combo,
                self.update_from_combo,
                self.update_to_combo,
                self.type_from_combo,
                self.type_to_combo,
                self.delete_from_combo,
                self.delete_to_combo,
            ]

            for combo in dropdowns:
                combo.values = locations
                combo.filtered_values = locations

            messagebox.showinfo(
                "Refreshed", "Location lists have been updated with the latest data."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing dropdowns: {e}")

    def on_canvas_resize(self, event):
        """Handle canvas resize events to redraw the path"""
        if self.last_path:
            self.path_canvas.delete("all")
            self._draw_road_path(self.last_path)
        elif not self.last_path:
            # Redraw placeholder at new center
            self.path_canvas.delete("all")
            width = event.width
            height = event.height
            self.canvas_placeholder = self.path_canvas.create_text(
                width // 2,
                height // 2,
                text="🗺️  Your route will appear here after searching",
                font=("Segoe UI", 13),
                fill="#adb5bd",
                tags="placeholder",
            )

    def clear_results(self):
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

        self.path_canvas.delete("all")
        self.last_path = None
        self.last_result = None

        # Clear new details container
        for widget in self.details_container.winfo_children():
            widget.destroy()

        placeholder_frame = ttk.Frame(self.details_container)
        placeholder_frame.pack(expand=True)

        placeholder = ttk.Label(
            placeholder_frame,
            text="Select start and destination,\nthen click 'Find Optimal Path' to see results.",
            font=("Segoe UI", 16),
            foreground="#adb5bd",
            justify=CENTER,
            padding=40,
        )
        placeholder.pack()

        # Redraw canvas placeholder
        width = self.path_canvas.winfo_width()
        height = self.path_canvas.winfo_height()
        self.path_canvas.create_text(
            width // 2,
            height // 2,
            text="Your route will appear here after searching",
            font=("Segoe UI", 13),
            fill="#adb5bd",
            tags="placeholder",
        )

    def find_path(self):
        start = self.start_var.get()
        goal = self.goal_var.get()

        if not start or not goal:
            messagebox.showwarning(
                "Input Required", "Please select both a starting point and destination."
            )
            return

        if start == goal:
            messagebox.showinfo(
                "Same Location", "You're already there! No travel needed."
            )
            return

        start = self.pathfinder.unformat_name(start)
        goal = self.pathfinder.unformat_name(goal)

        criteria = []
        if self.avoid_closed.get():
            criteria.append("avoid_closed")
        if self.avoid_unpaved.get():
            criteria.append("avoid_unpaved")
        if self.avoid_cisterns.get():
            criteria.append("avoid_broken_cisterns")
        if self.avoid_potholes.get():
            criteria.append("avoid_potholes")

        self.search_btn.configure(text="Searching...", state="disabled")
        self.root.update()

        try:
            result = self.pathfinder.find_path(
                start, goal, self.algo_var.get(), criteria
            )
            self.last_result = result

            # Clear previous canvas path
            self.path_canvas.delete("all")

            # === CLEAR AND REBUILD DETAILED INFO ===
            for widget in self.details_container.winfo_children():
                widget.destroy()

            if result["success"]:
                path = result["path"]
                self.last_path = path

                distance = float(result.get("distance", 0)) or 0
                travel_time = float(result.get("travel_time", 0)) or 0

                if distance == 0 or travel_time == 0:
                    if self.algo_var.get() == "bfs":
                        distance = len(path) * 2.5
                        travel_time = len(path) * 0.25
                    else:
                        distance = len(path) * 3.0
                        travel_time = distance / 40

                # Draw visualization
                self._draw_road_path(path)

                # === SUCCESS HEADER ===
                header = ttk.Frame(self.details_container, padding=(0, 0, 0, 20))
                header.pack(fill=X)

                ttk.Label(
                    header,
                    text="✅ Route Found Successfully!",
                    font=("Segoe UI", 19, "bold"),
                    foreground="#28a745",
                ).pack(side=LEFT)

                algo_tag = ttk.Label(
                    header,
                    text=f" {result['algorithm'].upper()} ",
                    font=("Segoe UI", 11, "bold"),
                    foreground="white",
                    background="#17a2b8",
                    padding=(12, 8),
                )
                algo_tag.pack(side=RIGHT)

                path_frame = ttk.LabelFrame(
                    self.details_container, text=" 🛣️ Route Path", padding=15
                )
                path_frame.pack(fill=X, pady=12)

                # Use a frame with grid to allow wrapping
                path_wrapper = ttk.Frame(path_frame)
                path_wrapper.pack(fill=X)

                flow_frame = ttk.Frame(path_wrapper)
                flow_frame.pack(anchor="w", padx=15, pady=10)

                # We'll use grid for wrapping
                flow_frame.grid_columnconfigure(0, weight=1)

                col = 0
                max_cols = 6  # Adjust: how many locations per row before wrapping

                for i, loc in enumerate(path):
                    if i > 0:
                        arrow = ttk.Label(
                            flow_frame,
                            text=" → ",
                            font=("Segoe UI", 14),
                            foreground="#495057",
                        )
                        arrow.grid(row=0, column=col, padx=2)
                        col += 1

                    bg_color = (
                        "#198754"
                        if i == 0
                        else "#dc3545"
                        if i == len(path) - 1
                        else "#0d6efd"
                    )
                    text = (
                        "START"
                        if i == 0
                        else "END"
                        if i == len(path) - 1
                        else self.pathfinder.format_name(loc)
                    )

                    loc_label = ttk.Label(
                        flow_frame,
                        text=f" {text} ",
                        font=("Segoe UI", 11, "bold"),
                        foreground="white",
                        background=bg_color,
                        padding=(14, 10),
                    )
                    loc_label.grid(row=0, column=col, padx=2, sticky="w")
                    col += 1

                    # Wrap to next row if too long
                    if col >= max_cols * 2 - 1:  # account for arrows
                        col = 0
                        flow_frame = ttk.Frame(path_wrapper)
                        flow_frame.pack(anchor="w", padx=15, pady=(0, 5))
                        flow_frame.grid_columnconfigure(0, weight=1)

                # === JOURNEY STATS (2-column grid) ===
                stats_frame = ttk.Frame(self.details_container)
                stats_frame.pack(fill=X, pady=15)

                stats = [
                    ("Total Distance", f"{distance:.2f} km", "#0d6efd"),
                    ("Est. Travel Time", f"{travel_time:.1f} h", "#198754"),
                    ("Total Stops", f"{len(path)}", "#6c757d"),
                    ("Algorithm", result["algorithm"].title(), "#fd7e14"),
                ]

                for i, (label, value, color) in enumerate(stats):
                    row, col = divmod(i, 2)
                    card = ttk.Frame(stats_frame, padding=15, bootstyle="light")
                    card.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
                    stats_frame.grid_columnconfigure(col, weight=1)

                    ttk.Label(
                        card, text=label, font=("Segoe UI", 9), foreground="#6c757d"
                    ).pack(anchor=W)
                    ttk.Label(
                        card,
                        text=value,
                        font=("Segoe UI", 17, "bold"),
                        foreground=color,
                    ).pack(anchor=W, pady=(2, 0))

                # === AVOIDANCE CRITERIA ===
                if criteria:
                    crit_frame = ttk.LabelFrame(
                        self.details_container,
                        text=" ⚠️ Active Avoidance Rules",
                        padding=12,
                    )
                    crit_frame.pack(fill=X, pady=12)

                    crit_names = {
                        "avoid_closed": "Closed Roads",
                        "avoid_unpaved": "Unpaved Roads",
                        "avoid_broken_cisterns": "Broken Cisterns",
                        "avoid_potholes": "Deep Potholes",
                    }
                    for c in criteria:
                        name = crit_names.get(c, c.replace("_", " ").title())
                        ttk.Label(
                            crit_frame,
                            text=f" {name} ",
                            font=("Segoe UI", 10),
                            background="#fff3cd",
                            foreground="#856404",
                            padding=(10, 6),
                        ).pack(side=LEFT, padx=4)

                # === FINAL MESSAGE ===
                ttk.Label(
                    self.details_container,
                    text="🌴 Safe travels on Jamaica's beautiful rural roads!",
                    font=("Segoe UI", 11, "italic"),
                    foreground="#495057",
                ).pack(pady=(25, 10))

            else:
                # === NO PATH FOUND ===
                error_frame = ttk.Frame(self.details_container)
                error_frame.pack(expand=True, fill=BOTH, pady=40)

                ttk.Label(
                    error_frame,
                    text="❌ No Route Available",
                    font=("Segoe UI", 22, "bold"),
                    foreground="#dc3545",
                ).pack(pady=(0, 15))

                ttk.Label(
                    error_frame,
                    text=result.get(
                        "message", "No path could be found with current settings."
                    ),
                    font=("Segoe UI", 12),
                    foreground="#6c757d",
                    wraplength=600,
                    justify="center",
                ).pack(pady=(0, 25))

                tips = ttk.LabelFrame(error_frame, text=" 💡 Suggestions", padding=15)
                tips.pack(fill=X, padx=40)

                for tip in [
                    "Try removing some avoidance criteria",
                    "Choose locations that are closer together",
                    "Some rural areas may have limited connectivity",
                ]:
                    ttk.Label(
                        tips,
                        text=f"• {tip}",
                        foreground="#495057",
                        font=("Segoe UI", 10),
                    ).pack(anchor=W, pady=3)

        except Exception as e:
            for widget in self.details_container.winfo_children():
                widget.destroy()

            ttk.Label(
                self.details_container,
                text="⚠️ Search Error",
                font=("Segoe UI", 20, "bold"),
                foreground="#dc3545",
            ).pack(pady=(40, 10))
            ttk.Label(
                self.details_container,
                text=f"Details: {str(e)}",
                foreground="#6c757d",
                wraplength=600,
            ).pack()

        finally:
            self.search_btn.configure(text="🔍 Find Optimal Path", state="normal")

    def _draw_road_path(self, path):
        """Draws a realistic road path with smooth curves connecting locations."""
        if not path:
            return

        # Get current canvas dimensions
        width = self.path_canvas.winfo_width()
        height = self.path_canvas.winfo_height()

        # Ensure minimum dimensions
        if width < 100:
            width = 600
        if height < 100:
            height = 300

        # Dynamic margins based on canvas size
        margin_x = max(80, int(width * 0.08))
        margin_y = max(40, int(height * 0.15))
        node_count = len(path)

        # Calculate positions with slight vertical variation
        available_width = width - 2 * margin_x
        center_y = height // 2

        if node_count == 1:
            positions = [(width // 2, center_y)]
        else:
            spacing = available_width // (node_count - 1) if node_count > 1 else 0
            positions = []
            for i in range(node_count):
                x = margin_x + i * spacing
                # Add slight vertical variation
                y_offset = (
                    math.sin(i * 0.8) * min(30, height * 0.1) if node_count > 2 else 0
                )
                y = center_y + y_offset
                positions.append((x, y))

        # Draw the road path
        self._draw_smooth_road(positions, width, height)

        # Draw location markers with size scaled to canvas
        marker_size = max(20, min(28, int(min(width, height) * 0.04)))

        for i, (x, y) in enumerate(positions):
            node = path[i]

            if i == 0:
                main_color = "#28a745"
                border_color = "#218838"
                text_color = "white"
                icon = "🚀"
                label_text = "START"
                label_bg = "#d4edda"
                label_fg = "#155724"
            elif i == len(path) - 1:
                main_color = "#dc3545"
                border_color = "#c82333"
                text_color = "white"
                icon = "🎯"
                label_text = "DESTINATION"
                label_bg = "#f8d7da"
                label_fg = "#721c24"
            else:
                main_color = "#007bff"
                border_color = "#0056b3"
                text_color = "white"
                icon = "📍"
                label_text = f"STOP {i}"
                label_bg = "#d1ecf1"
                label_fg = "#0c5460"

            # Shadow
            shadow_offset = 3
            self.path_canvas.create_oval(
                x - marker_size + shadow_offset,
                y - marker_size + shadow_offset,
                x + marker_size + shadow_offset,
                y + marker_size + shadow_offset,
                fill="#000020",
                outline="",
            )

            # Outer circle
            self.path_canvas.create_oval(
                x - marker_size,
                y - marker_size,
                x + marker_size,
                y + marker_size,
                fill=border_color,
                outline="",
            )

            # Inner circle
            inner_size = marker_size - 4
            self.path_canvas.create_oval(
                x - inner_size,
                y - inner_size,
                x + inner_size,
                y + inner_size,
                fill=main_color,
                outline="white",
                width=2,
            )

            # Icon and text with dynamic sizing
            icon_size = max(12, min(14, int(marker_size * 0.5)))
            text_size = max(7, min(8, int(marker_size * 0.3)))

            self.path_canvas.create_text(
                x, y - 5, text=icon, font=("Segoe UI", icon_size)
            )

            node_text = str(node)
            if len(node_text) > 10:
                node_text = node_text[:8] + ".."

            self.path_canvas.create_text(
                x,
                y + 10,
                text=node_text,
                font=("Segoe UI", text_size, "bold"),
                fill=text_color,
            )

            # Label below marker
            label_y = y + marker_size + 25
            label_padding = 10

            temp_text = self.path_canvas.create_text(
                x, label_y, text=label_text, font=("Segoe UI", text_size, "bold")
            )
            bbox = self.path_canvas.bbox(temp_text)
            self.path_canvas.delete(temp_text)

            if bbox:
                self._draw_rounded_rect(
                    bbox[0] - label_padding,
                    bbox[1] - label_padding // 2,
                    bbox[2] + label_padding,
                    bbox[3] + label_padding // 2,
                    radius=8,
                    fill=label_bg,
                    outline=label_fg,
                    width=2,
                )

            self.path_canvas.create_text(
                x,
                label_y,
                text=label_text,
                font=("Segoe UI", text_size, "bold"),
                fill=label_fg,
            )

    def _draw_smooth_road(self, positions, canvas_width, canvas_height):
        """Draw a realistic smooth road connecting all positions."""
        if len(positions) < 2:
            return

        road_points = []
        for x, y in positions:
            road_points.extend([x, y])

        # Scale road width based on canvas size
        base_width = max(12, min(20, int(min(canvas_width, canvas_height) * 0.03)))

        # Base road layer
        self.path_canvas.create_line(
            road_points,
            width=base_width,
            fill="#495057",
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
            splinesteps=12,
        )

        # Middle layer
        self.path_canvas.create_line(
            road_points,
            width=base_width - 4,
            fill="#6c757d",
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
            splinesteps=12,
        )

        # Top surface
        self.path_canvas.create_line(
            road_points,
            width=base_width - 6,
            fill="#343a40",
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=True,
            splinesteps=12,
        )

        # Center line and distance markers
        self._draw_center_line(positions)
        self._draw_distance_markers(positions, canvas_width, canvas_height)

    def _draw_center_line(self, positions):
        """Draw dashed center line on the road."""
        if len(positions) < 2:
            return

        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]

            segments = 8
            for seg in range(segments):
                if seg % 2 == 0:
                    t1 = seg / segments
                    t2 = (seg + 0.7) / segments

                    dash_x1 = x1 + (x2 - x1) * t1
                    dash_y1 = y1 + (y2 - y1) * t1
                    dash_x2 = x1 + (x2 - x1) * t2
                    dash_y2 = y1 + (y2 - y1) * t2

                    self.path_canvas.create_line(
                        dash_x1,
                        dash_y1,
                        dash_x2,
                        dash_y2,
                        width=2,
                        fill="#ffc107",
                        capstyle=tk.ROUND,
                    )

    def _draw_distance_markers(self, positions, canvas_width, canvas_height):
        """Draw distance information between consecutive locations."""
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]

            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2

            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / 50
            badge_y = mid_y - 40

            # Scale badge size
            badge_radius = max(
                20, min(25, int(min(canvas_width, canvas_height) * 0.035))
            )

            self.path_canvas.create_oval(
                mid_x - badge_radius,
                badge_y - 12,
                mid_x + badge_radius,
                badge_y + 12,
                fill="#ffffff",
                outline="#007bff",
                width=2,
            )

            font_size = max(7, min(8, int(badge_radius * 0.35)))
            self.path_canvas.create_text(
                mid_x,
                badge_y,
                text=f"~{distance:.1f}km",
                font=("Segoe UI", font_size, "bold"),
                fill="#007bff",
            )

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Draw a rounded rectangle."""
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.path_canvas.create_polygon(points, **kwargs, smooth=True)


if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = PathFinderGUI(root)
    root.mainloop()
