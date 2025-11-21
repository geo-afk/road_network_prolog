import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import LEFT, W, BOTH, X, CENTER, TOP
from ttkbootstrap.scrolled import ScrolledText
from app.prolog.prolog_interface import RoadNetworkPathFinder


class PathFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jamaican Rural Road Network Path-Finder")
        self.root.geometry("1200x850")

        # Set minimum window size
        self.root.minsize(1000, 750)

        try:
            self.pathfinder = RoadNetworkPathFinder()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {e}")
            root.destroy()
            return

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()

        # Enhanced styles
        style.configure("Modern.TLabel", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#6c757d")
        style.configure("SectionHeader.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Card.TFrame", relief="flat", borderwidth=0)

        # Main container with gradient-like background
        container = ttk.Frame(self.root, style="Card.TFrame")
        container.pack(fill=BOTH, expand=True)

        # Header Section with icon and subtitle
        header_frame = ttk.Frame(container, style="Card.TFrame")
        header_frame.pack(fill=X, pady=(30, 10), padx=30)

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

        # Main content area with two columns
        content_frame = ttk.Frame(container, style="Card.TFrame")
        content_frame.pack(fill=BOTH, expand=True, padx=30, pady=10)

        # Left Column - Input Controls
        left_column = ttk.Frame(content_frame, style="Card.TFrame")
        left_column.pack(side=LEFT, fill=BOTH, expand=False, padx=(0, 15))

        # --- Location Selection Card ---
        location_card = ttk.LabelFrame(
            left_column,
            text="  📍 Location Selection  ",
            padding="20",
            bootstyle="primary",
        )
        location_card.pack(fill=X, pady=(0, 15))

        locations = self.pathfinder.get_available_locations()

        # Start Location with enhanced styling
        start_container = ttk.Frame(location_card)
        start_container.grid(row=0, column=0, pady=(0, 15), sticky="ew")

        start_label = ttk.Label(
            start_container,
            text="🏁 Starting Point",
            style="SectionHeader.TLabel",
            foreground="#28a745",
        )
        start_label.pack(anchor=W, pady=(0, 8))

        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(
            start_container,
            textvariable=self.start_var,
            values=locations,
            state="readonly",
            font=("Segoe UI", 11),
            height=15,
        )
        self.start_combo.pack(fill=X)
        self.start_combo.configure(bootstyle="success")

        # Destination with enhanced styling
        dest_container = ttk.Frame(location_card)
        dest_container.grid(row=1, column=0, pady=(0, 0), sticky="ew")

        dest_label = ttk.Label(
            dest_container,
            text="🎯 Destination",
            style="SectionHeader.TLabel",
            foreground="#dc3545",
        )
        dest_label.pack(anchor=W, pady=(0, 8))

        self.goal_var = tk.StringVar()
        self.goal_combo = ttk.Combobox(
            dest_container,
            textvariable=self.goal_var,
            values=locations,
            state="readonly",
            font=("Segoe UI", 11),
            height=15,
        )
        self.goal_combo.pack(fill=X)
        self.goal_combo.configure(bootstyle="danger")

        location_card.columnconfigure(0, weight=1)

        # --- Algorithm Selection Card ---
        algo_card = ttk.LabelFrame(
            left_column,
            text="  ⚙️ Algorithm Selection  ",
            padding="20",
            bootstyle="info",
        )
        algo_card.pack(fill=X, pady=(0, 15))

        self.algo_var = tk.StringVar(value="dijkstra")

        algorithms = [
            ("dijkstra", "Dijkstra's Algorithm", "Guaranteed shortest path"),
            ("astar", "A* Algorithm", "Fast heuristic search"),
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

        # --- Avoidance Criteria Card ---
        criteria_card = ttk.LabelFrame(
            left_column,
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
            ("🚫 Closed Roads", self.avoid_closed, "Avoid roads marked as closed"),
            ("🛤️ Unpaved Roads", self.avoid_unpaved, "Avoid dirt or gravel roads"),
            (
                "💧 Broken Cisterns",
                self.avoid_cisterns,
                "Avoid areas with water issues",
            ),
            ("🕳️ Deep Potholes", self.avoid_potholes, "Avoid roads with severe damage"),
        ]

        for text, var, tooltip in criteria:
            check_frame = ttk.Frame(criteria_card)
            check_frame.pack(fill=X, pady=4)

            ttk.Checkbutton(
                check_frame, text=text, variable=var, bootstyle="warning-round-toggle"
            ).pack(side=LEFT)

        # --- Search Button ---
        button_frame = ttk.Frame(left_column)
        button_frame.pack(pady=15)

        self.search_btn = ttk.Button(
            button_frame,
            text="🔍  Find Optimal Path",
            command=self.find_path,
            bootstyle="success",
            width=30,
        )
        self.search_btn.pack()

        # Add clear button
        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear Results",
            command=self.clear_results,
            bootstyle="secondary-outline",
            width=30,
        )
        self.clear_btn.pack(pady=(10, 0))

        # Right Column - Results
        right_column = ttk.Frame(content_frame, style="Card.TFrame")
        right_column.pack(side=LEFT, fill=BOTH, expand=True)

        results_card = ttk.LabelFrame(
            right_column,
            text="  📊 Path Visualization & Results  ",
            padding="20",
            bootstyle="success",
        )
        results_card.pack(fill=BOTH, expand=True)

        # Canvas for visual path with improved styling
        canvas_frame = ttk.Frame(results_card)
        canvas_frame.pack(fill=X, pady=(0, 15))

        canvas_label = ttk.Label(
            canvas_frame, text="Route Visualization", style="SectionHeader.TLabel"
        )
        canvas_label.pack(anchor=W, pady=(0, 10))

        self.path_canvas = tk.Canvas(
            canvas_frame, height=320, bg="#f8f9fa", highlightthickness=0, relief="flat"
        )
        self.path_canvas.pack(fill=X)

        # Add placeholder text to canvas
        self.canvas_placeholder = self.path_canvas.create_text(
            600,
            160,
            text="🗺️  Your route will appear here after searching",
            font=("Segoe UI", 13),
            fill="#adb5bd",
            tags="placeholder",
        )

        # Textual results with improved styling
        text_frame = ttk.Frame(results_card)
        text_frame.pack(fill=BOTH, expand=True)

        text_label = ttk.Label(
            text_frame, text="Detailed Information", style="SectionHeader.TLabel"
        )
        text_label.pack(anchor=W, pady=(0, 10))

        self.results_text = ScrolledText(
            text_frame, height=12, font=("Consolas", 10), autohide=True
        )
        self.results_text.pack(fill=BOTH, expand=True)

        # Add placeholder text
        placeholder_text = "Select your start and destination points, choose an algorithm,\nand click 'Find Optimal Path' to see results here."
        self.results_text.insert(1.0, placeholder_text)
        self.results_text.text.configure(state="disabled")

    def clear_results(self):
        """Clear all results and reset to initial state"""
        self.results_text.text.configure(state="normal")
        self.results_text.delete(1.0, tk.END)
        placeholder_text = "Select your start and destination points, choose an algorithm,\nand click 'Find Optimal Path' to see results here."
        self.results_text.insert(1.0, placeholder_text)
        self.results_text.text.configure(state="disabled")

        self.path_canvas.delete("all")
        self.canvas_placeholder = self.path_canvas.create_text(
            600,
            160,
            text="🗺️  Your route will appear here after searching",
            font=("Segoe UI", 13),
            fill="#adb5bd",
            tags="placeholder",
        )

    def find_path(self):
        start = self.start_var.get()
        goal = self.goal_var.get()

        if not start or not goal:
            messagebox.showwarning(
                "Input Required",
                "Please select both a starting point and destination to continue.",
            )
            return

        if start == goal:
            messagebox.showinfo(
                "Same Location",
                "Starting point and destination are the same. No path needed!",
            )
            return

        criteria = []
        if self.avoid_closed.get():
            criteria.append("avoid_closed")
        if self.avoid_unpaved.get():
            criteria.append("avoid_unpaved")
        if self.avoid_cisterns.get():
            criteria.append("avoid_broken_cisterns")
        if self.avoid_potholes.get():
            criteria.append("avoid_potholes")

        # Show loading state
        self.search_btn.configure(text="⏳ Searching...", state="disabled")
        self.root.update()

        try:
            result = self.pathfinder.find_path(
                start, goal, self.algo_var.get(), criteria
            )

            self.results_text.text.configure(state="normal")
            self.results_text.delete(1.0, tk.END)
            self.path_canvas.delete("all")

            if result["success"]:
                path = result["path"]
                distance = result["distance"]
                travel_time = distance / 40

                # --- Draw visual path ---
                self._draw_path_nodes(path)

                # Enhanced output formatting
                output = "=" * 70 + "\n"
                output += f"✅ ROUTE FOUND - {result['algorithm'].upper()}\n"
                output += "=" * 70 + "\n\n"

                output += f"🛣️  ROUTE PATH\n"
                output += f"   {' → '.join(str(loc) for loc in path)}\n\n"

                output += f"📊 JOURNEY DETAILS\n"
                output += f"   • Total Distance: {distance} km\n"
                output += f"   • Estimated Time: {travel_time:.1f} hours (at 40 km/h)\n"
                output += f"   • Number of Stops: {len(path)}\n"
                output += f"   • Algorithm Used: {result['algorithm'].title()}\n\n"

                if criteria:
                    output += f"🚧 ACTIVE AVOIDANCE CRITERIA\n"
                    criteria_names = {
                        "avoid_closed": "Closed Roads",
                        "avoid_unpaved": "Unpaved Roads",
                        "avoid_broken_cisterns": "Broken Cisterns",
                        "avoid_potholes": "Deep Potholes",
                    }
                    for c in criteria:
                        output += f"   • {criteria_names.get(c, c)}\n"
                    output += "\n"

                output += "=" * 70 + "\n"
                output += "Have a safe journey! 🚗\n"

                self.results_text.insert(1.0, output)
            else:
                error_output = "=" * 70 + "\n"
                error_output += "⚠️  NO ROUTE AVAILABLE\n"
                error_output += "=" * 70 + "\n\n"
                error_output += f"Message: {result['message']}\n\n"
                error_output += "Suggestions:\n"
                error_output += "  • Try removing some avoidance criteria\n"
                error_output += "  • Select different start or destination points\n"
                error_output += (
                    "  • Check if the locations are connected in the network\n"
                )

                self.results_text.insert(1.0, error_output)

        finally:
            self.results_text.text.configure(state="disabled")
            self.search_btn.configure(text="🔍  Find Optimal Path", state="normal")

    def _draw_path_nodes(self, path):
        """Draws the route visually as connected nodes with modern card-based styling."""
        if not path:
            return

        width = self.path_canvas.winfo_width() or 1000
        height = 320
        margin = 80
        node_count = len(path)

        # Calculate positions for horizontal flow
        available_width = width - 2 * margin

        if node_count == 1:
            positions = [(width // 2, height // 2)]
        elif node_count == 2:
            positions = [(margin, height // 2), (width - margin, height // 2)]
        else:
            spacing = available_width // (node_count - 1)
            positions = [(margin + i * spacing, height // 2) for i in range(node_count)]

        # Draw connecting lines first (so they appear behind nodes)
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]

            # Gradient line effect with multiple overlapping lines
            self.path_canvas.create_line(
                x1, y1, x2, y2, width=8, fill="#e9ecef", capstyle=tk.ROUND
            )
            self.path_canvas.create_line(
                x1, y1, x2, y2, width=4, fill="#6c757d", capstyle=tk.ROUND
            )

            # Draw distance label on the line
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2 - 20

            # You can add distance calculation here if available
            self.path_canvas.create_text(
                mid_x, mid_y, text="━━", font=("Segoe UI", 10), fill="#6c757d"
            )

        # Draw nodes
        for i, (x, y) in enumerate(positions):
            node = path[i]

            # Determine colors based on position
            if i == 0:
                # Start node - Green
                main_color = "#28a745"
                border_color = "#218838"
                text_color = "white"
                icon = "🏁"
            elif i == len(path) - 1:
                # End node - Red
                main_color = "#dc3545"
                border_color = "#c82333"
                text_color = "white"
                icon = "🎯"
            else:
                # Middle nodes - Blue
                main_color = "#007bff"
                border_color = "#0056b3"
                text_color = "white"
                icon = "📍"

            # Draw outer glow/shadow
            glow_radius = 50
            self.path_canvas.create_oval(
                x - glow_radius,
                y - glow_radius,
                x + glow_radius,
                y + glow_radius,
                fill="#f8f9fa",
                outline="",
            )

            # Draw main circle border
            radius = 40
            self.path_canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=border_color,
                outline="",
            )

            # Draw inner circle
            inner_radius = 36
            self.path_canvas.create_oval(
                x - inner_radius,
                y - inner_radius,
                x + inner_radius,
                y + inner_radius,
                fill=main_color,
                outline="",
            )

            # Draw icon
            self.path_canvas.create_text(x, y - 8, text=icon, font=("Segoe UI", 16))

            # Draw node name inside circle
            node_text = str(node)
            if len(node_text) > 8:
                node_text = node_text[:7] + "..."

            self.path_canvas.create_text(
                x, y + 12, text=node_text, font=("Segoe UI", 9, "bold"), fill=text_color
            )

            # Draw label card below node
            label_y = y + radius + 30

            if i == 0:
                label_text = "START"
                label_bg = "#d4edda"
                label_fg = "#155724"
            elif i == len(path) - 1:
                label_text = "DESTINATION"
                label_bg = "#f8d7da"
                label_fg = "#721c24"
            else:
                label_text = f"STOP {i}"
                label_bg = "#d1ecf1"
                label_fg = "#0c5460"

            # Draw label background (rounded rectangle effect)
            bbox = self.path_canvas.bbox(
                self.path_canvas.create_text(
                    x, label_y, text=label_text, font=("Segoe UI", 8, "bold")
                )
            )
            if bbox:
                padding = 8
                self.path_canvas.create_rectangle(
                    bbox[0] - padding,
                    bbox[1] - padding,
                    bbox[2] + padding,
                    bbox[3] + padding,
                    fill=label_bg,
                    outline=label_fg,
                    width=1,
                )

            # Draw label text
            self.path_canvas.create_text(
                x, label_y, text=label_text, font=("Segoe UI", 8, "bold"), fill=label_fg
            )


if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = PathFinderGUI(root)
    root.mainloop()
