"""PersLQY desktop application with an embedded graphical interface.

The application calculates persistent luminescence quantum yield (PersLQY)
and total luminescence quantum yield (TotalQY) from spectroscopic and kinetic
measurements.

Method reference:
    Castaing et al., Advanced Optical Materials 12 (2024), 2401638
    https://doi.org/10.1002/adom.202401638
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import pandas as pd


DATA_FILE_TYPES = (("Data files", "*.txt"), ("All files", "*.*"))
PLOT_FILE_TYPES = (
    ("PNG image", "*.png"),
    ("PDF document", "*.pdf"),
    ("SVG image", "*.svg"),
    ("All files", "*.*"),
)


@dataclass(frozen=True)
class InputFiles:
    """Paths required for one PersLQY calculation."""

    luminescence_spectrum: Path
    persistent_spectrum: Path
    source_spectrum: Path
    source_sample_spectrum: Path
    absorption: Path
    emission: Path

    @property
    def directory(self) -> Path:
        """Directory containing the selected measurement files."""

        return self.luminescence_spectrum.parent


@dataclass(frozen=True)
class CalculationResults:
    """Calculated values and arrays used by the interface."""

    total_qy: float
    persl_qy: float
    corrected_emission: np.ndarray
    absorbed_signal: float
    background: float
    background_start: float
    background_stop: float


def read_table(
    path: Path,
    required_columns: set[str],
    description: str,
) -> pd.DataFrame:
    """Read and validate a tab-separated measurement file."""

    if not path.is_file():
        raise FileNotFoundError(f"{description} file not found:\n{path}")

    table = pd.read_table(path)

    if table.empty:
        raise ValueError(f"The {description} file is empty:\n{path}")

    missing = required_columns.difference(table.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(
            f"The {description} file is missing required column(s): "
            f"{missing_text}\n\nFile: {path}"
        )

    return table


def first_value(table: pd.DataFrame, column: str):
    """Return the first value in a table column."""

    return table[column].iloc[0]


def closest_index(values: pd.Series | np.ndarray, target: float) -> int:
    """Return the index of the value closest to a target."""

    array = np.asarray(values, dtype=float)
    return int(np.abs(array - target).argmin())


def ordered_bounds(first_index: int, second_index: int) -> tuple[int, int]:
    """Return inclusive array bounds in ascending order."""

    return min(first_index, second_index), max(first_index, second_index)


def spectral_correction(
    spectrum: pd.DataFrame,
    wavelength_min: float,
    wavelength_max: float,
) -> float:
    """Calculate the correction from the detected band to the full spectrum."""

    wavelengths = spectrum["wl"].to_numpy(dtype=float)
    counts = spectrum["counts"].to_numpy(dtype=float)

    index_1 = closest_index(wavelengths, wavelength_min)
    index_2 = closest_index(wavelengths, wavelength_max)
    start, stop = ordered_bounds(index_1, index_2)
    stop += 1

    if stop - start < 2:
        raise ValueError("The selected spectral interval contains too few points.")

    full_integral = np.trapezoid(y=counts, x=wavelengths)
    band_integral = np.trapezoid(y=counts[start:stop], x=wavelengths[start:stop])

    if np.isclose(band_integral, 0.0):
        raise ValueError("A spectral correction cannot be calculated: zero integral.")

    return float(abs(full_integral / band_integral))


def optional_od_table(
    measurement: pd.DataFrame,
    directory: Path,
    description: str,
) -> pd.DataFrame | None:
    """Load an optional optical-density spectrum named in a measurement file."""

    od_value = first_value(measurement, "OD")

    if pd.isna(od_value) or str(od_value).strip() in {"", "0", "0.0"}:
        return None

    od_path = directory / str(od_value)
    return read_table(od_path, {"wl", "OD"}, description)


def filter_correction(
    od_table: pd.DataFrame | None,
    source_spectrum: pd.DataFrame,
    wavelength_min: float,
    wavelength_max: float,
) -> float:
    """Calculate the neutral-density-filter correction factor."""

    if od_table is None:
        return 1.0

    od_wavelength = od_table["wl"].to_numpy(dtype=float)
    transmission = 10.0 ** (-od_table["OD"].to_numpy(dtype=float))

    index_1 = closest_index(od_wavelength, wavelength_min)
    index_2 = closest_index(od_wavelength, wavelength_max)
    start, stop = ordered_bounds(index_1, index_2)
    stop += 1

    selected_wavelength = od_wavelength[start:stop]

    if selected_wavelength.size < 2:
        raise ValueError("The OD correction interval contains too few points.")

    interpolated_source = np.interp(
        selected_wavelength,
        source_spectrum["wl"].to_numpy(dtype=float),
        source_spectrum["counts"].to_numpy(dtype=float),
    )

    numerator = np.trapezoid(y=interpolated_source, x=selected_wavelength)
    denominator = np.trapezoid(
        y=transmission[start:stop] * interpolated_source,
        x=selected_wavelength,
    )

    if np.isclose(denominator, 0.0):
        raise ValueError("The OD correction cannot be calculated: zero integral.")

    return float(numerator / denominator)


def sum_between_times(
    table: pd.DataFrame,
    start_time: float,
    stop_time: float,
) -> float:
    """Sum counts between the rows nearest to two times, inclusively."""

    start_index = closest_index(table["t"], start_time)
    stop_index = closest_index(table["t"], stop_time)
    start, stop = ordered_bounds(start_index, stop_index)
    return float(table["counts"].iloc[start : stop + 1].sum())


def calculate_quantum_yields(
    files: InputFiles,
    background_start: float,
    background_stop: float,
) -> tuple[CalculationResults, dict[str, pd.DataFrame]]:
    """Load measurements and calculate TotalQY and PersLQY."""

    spectra_columns = {"wl", "counts"}
    kinetic_columns = {"t", "counts"}

    lum_spectrum = read_table(
        files.luminescence_spectrum,
        spectra_columns,
        "luminescence spectrum",
    )
    pers_spectrum = read_table(
        files.persistent_spectrum,
        spectra_columns,
        "persistent luminescence spectrum",
    )
    source_spectrum = read_table(
        files.source_spectrum,
        spectra_columns,
        "source spectrum",
    )
    source_sample_spectrum = read_table(
        files.source_sample_spectrum,
        spectra_columns,
        "source + sample spectrum",
    )
    absorption = read_table(
        files.absorption,
        kinetic_columns | {"wl0", "bth", "t0", "t1", "OD", "ref_file"},
        "absorption measurement",
    )
    emission = read_table(
        files.emission,
        kinetic_columns | {"wl0", "bth", "t0", "t1", "OD"},
        "emission measurement",
    )

    reference_filename = str(first_value(absorption, "ref_file"))
    absorption_reference = read_table(
        files.directory / reference_filename,
        kinetic_columns | {"t0", "t1"},
        "absorption reference",
    )

    emission_center = float(first_value(emission, "wl0"))
    emission_bandwidth = float(first_value(emission, "bth"))
    emission_wavelength_min = emission_center - emission_bandwidth / 2.0
    emission_wavelength_max = emission_center + emission_bandwidth / 2.0
    charging_start = float(first_value(emission, "t0"))
    charging_stop = float(first_value(emission, "t1"))

    excitation_center = float(first_value(absorption, "wl0"))
    excitation_bandwidth = float(first_value(absorption, "bth"))
    excitation_wavelength_min = excitation_center - excitation_bandwidth / 2.0
    excitation_wavelength_max = excitation_center + excitation_bandwidth / 2.0

    lum_correction = spectral_correction(
        lum_spectrum,
        emission_wavelength_min,
        emission_wavelength_max,
    )
    pers_correction = spectral_correction(
        pers_spectrum,
        emission_wavelength_min,
        emission_wavelength_max,
    )

    emission_od = optional_od_table(
        emission,
        files.directory,
        "emission OD spectrum",
    )
    emission_filter_correction = filter_correction(
        emission_od,
        lum_spectrum,
        emission_wavelength_min,
        emission_wavelength_max,
    )

    emission_times = emission["t"].to_numpy(dtype=float)
    emission_counts = emission["counts"].to_numpy(dtype=float)

    minimum_time = float(np.min(emission_times))
    maximum_time = float(np.max(emission_times))

    if background_start < minimum_time or background_stop > maximum_time:
        raise ValueError(
            "The background interval must be inside the emission time range "
            f"({minimum_time:g} to {maximum_time:g} s)."
        )
    if background_stop <= background_start:
        raise ValueError("Background stop time must be greater than start time.")

    background_start_index = closest_index(emission_times, background_start)
    background_stop_index = closest_index(emission_times, background_stop)
    background_first, background_last = ordered_bounds(
        background_start_index,
        background_stop_index,
    )

    background_values = emission_counts[background_first : background_last + 1]
    if background_values.size == 0:
        raise ValueError("The selected background interval contains no data points.")

    background = float(np.mean(background_values))
    corrected_emission = emission_counts - background

    charging_start_index = closest_index(emission_times, charging_start)
    charging_stop_index = closest_index(emission_times, charging_stop)

    if charging_start_index > charging_stop_index:
        raise ValueError("Emission t0 must occur before emission t1.")

    corrected_emission[charging_start_index : charging_stop_index + 1] *= (
        lum_correction * emission_filter_correction
    )
    corrected_emission[charging_stop_index + 1 :] *= (
        pers_correction * emission_filter_correction
    )

    source_correction = spectral_correction(
        source_spectrum,
        excitation_wavelength_min,
        excitation_wavelength_max,
    )
    source_sample_correction = spectral_correction(
        source_sample_spectrum,
        excitation_wavelength_min,
        excitation_wavelength_max,
    )

    absorption_od = optional_od_table(
        absorption,
        files.directory,
        "absorption OD spectrum",
    )
    absorption_filter_correction = filter_correction(
        absorption_od,
        source_spectrum,
        excitation_wavelength_min,
        excitation_wavelength_max,
    )

    reference_start = float(first_value(absorption_reference, "t0"))
    reference_stop = float(first_value(absorption_reference, "t1"))
    absorption_start = float(first_value(absorption, "t0"))
    absorption_stop = float(first_value(absorption, "t1"))

    reference_signal = (
        source_correction
        * sum_between_times(absorption_reference, reference_start, reference_stop)
        * absorption_filter_correction
    )
    sample_signal = (
        source_sample_correction
        * sum_between_times(absorption, absorption_start, absorption_stop)
        * absorption_filter_correction
    )

    charging_duration = charging_stop - charging_start
    reference_duration = reference_stop - reference_start
    absorption_duration = absorption_stop - absorption_start

    if charging_duration <= 0:
        raise ValueError("Emission t1 must be greater than emission t0.")
    if reference_duration <= 0 or absorption_duration <= 0:
        raise ValueError("Absorption integration times must be positive.")

    if not (
        np.isclose(charging_stop, absorption_stop)
        and np.isclose(charging_stop, reference_stop)
    ):
        reference_signal *= charging_duration / reference_duration
        sample_signal *= charging_duration / absorption_duration

    absorbed_signal = reference_signal - sample_signal

    if absorbed_signal <= 0 or np.isclose(absorbed_signal, 0.0):
        raise ValueError(
            "The calculated absorbed signal is zero or negative. Check the "
            "reference, sample, correction files, and integration times."
        )

    total_emission = float(np.sum(corrected_emission[charging_start_index:]))
    persistent_emission = float(
        np.sum(corrected_emission[charging_stop_index + 1 :])
    )

    results = CalculationResults(
        total_qy=100.0 * total_emission / absorbed_signal,
        persl_qy=100.0 * persistent_emission / absorbed_signal,
        corrected_emission=corrected_emission,
        absorbed_signal=absorbed_signal,
        background=background,
        background_start=background_start,
        background_stop=background_stop,
    )

    tables = {
        "lum_spectrum": lum_spectrum,
        "pers_spectrum": pers_spectrum,
        "source_spectrum": source_spectrum,
        "source_sample_spectrum": source_sample_spectrum,
        "absorption": absorption,
        "absorption_reference": absorption_reference,
        "emission": emission,
    }

    return results, tables


def populate_figure(
    figure: Figure,
    tables: dict[str, pd.DataFrame],
    results: CalculationResults,
) -> None:
    """Draw the four measurement plots in a Matplotlib figure."""

    figure.clear()
    axes = figure.subplots(2, 2)

    lum_spectrum = tables["lum_spectrum"]
    pers_spectrum = tables["pers_spectrum"]
    source_spectrum = tables["source_spectrum"]
    source_sample_spectrum = tables["source_sample_spectrum"]
    absorption = tables["absorption"]
    absorption_reference = tables["absorption_reference"]
    emission = tables["emission"]

    emission_times = emission["t"].to_numpy(dtype=float)
    raw_emission = emission["counts"].to_numpy(dtype=float)

    axes[0, 0].plot(
        lum_spectrum["wl"],
        lum_spectrum["counts"],
        label="Luminescence",
    )
    axes[0, 0].plot(
        pers_spectrum["wl"],
        pers_spectrum["counts"],
        "--",
        label="Persistent luminescence",
    )
    axes[0, 0].set_title("Emission spectra")
    axes[0, 0].set_xlabel("Wavelength (nm)")
    axes[0, 0].set_ylabel("Counts")
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.2)

    axes[0, 1].plot(
        source_spectrum["wl"],
        source_spectrum["counts"],
        label="Source",
    )
    axes[0, 1].plot(
        source_sample_spectrum["wl"],
        source_sample_spectrum["counts"],
        "--",
        label="Source + sample",
    )
    axes[0, 1].set_title("Excitation spectra")
    axes[0, 1].set_xlabel("Wavelength (nm)")
    axes[0, 1].set_ylabel("Counts")
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.2)

    axes[1, 0].plot(
        absorption_reference["t"],
        absorption_reference["counts"],
        label="Reference",
    )
    axes[1, 0].plot(
        absorption["t"],
        absorption["counts"],
        "--",
        label="Sample",
    )
    axes[1, 0].set_title("Absorption kinetics")
    axes[1, 0].set_xlabel("Time (s)")
    axes[1, 0].set_ylabel("Counts")
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.2)

    positive_raw = raw_emission > 0
    axes[1, 1].scatter(
        emission_times[positive_raw],
        raw_emission[positive_raw],
        s=8,
        alpha=0.65,
        label="Raw emission",
    )

    positive_corrected = results.corrected_emission > 0
    axes[1, 1].plot(
        emission_times[positive_corrected],
        results.corrected_emission[positive_corrected],
        linewidth=1.0,
        label="Background corrected",
    )
    axes[1, 1].axvspan(
        results.background_start,
        results.background_stop,
        alpha=0.18,
        label="Background interval",
    )
    axes[1, 1].axhline(
        results.background,
        linestyle=":",
        linewidth=1.2,
        label=f"Background = {results.background:.3g}",
    )
    axes[1, 1].set_title("Emission kinetics")
    axes[1, 1].set_xlabel("Time (s)")
    axes[1, 1].set_ylabel("Counts")
    axes[1, 1].set_yscale("log")
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.2)

    figure.suptitle(
        f"TotalQY = {results.total_qy:.2f}%    "
        f"PersLQY = {results.persl_qy:.2f}%",
        fontsize=14,
        fontweight="bold",
    )
    figure.tight_layout(rect=(0, 0, 1, 0.96))


class ScrollableFrame(ttk.Frame):
    """A vertically scrollable frame for controls that may not fit onscreen."""

    def __init__(self, parent: tk.Misc, **kwargs) -> None:
        super().__init__(parent, **kwargs)

        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            borderwidth=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.content = ttk.Frame(self.canvas)

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_content)

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _update_scroll_region(self, _event: tk.Event) -> None:
        """Update the scrolling limits when the content size changes."""

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event: tk.Event) -> None:
        """Keep the embedded content as wide as the visible canvas."""

        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event: tk.Event) -> None:
        """Enable mouse-wheel scrolling while the pointer is over the panel."""

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event: tk.Event) -> None:
        """Disable panel scrolling when the pointer leaves it."""

        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Scroll the panel with the mouse wheel on Windows and macOS."""

        if event.delta:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")


class PersLQYApp(tk.Tk):
    """Main PersLQY desktop window."""

    FILE_FIELDS = (
        ("luminescence_spectrum", "Luminescence spectrum"),
        ("persistent_spectrum", "Persistent spectrum"),
        ("source_spectrum", "Source spectrum"),
        ("source_sample_spectrum", "Source + sample spectrum"),
        ("absorption", "Absorption measurement"),
        ("emission", "Emission measurement"),
    )

    def __init__(self) -> None:
        super().__init__()

        self.title("PersLQY Calculator")
        self.geometry("1280x820")
        self.minsize(850, 560)

        self.file_variables = {
            key: tk.StringVar()
            for key, _label in self.FILE_FIELDS
        }
        self.background_start_var = tk.StringVar(value="0")
        self.background_stop_var = tk.StringVar(value="30")
        self.total_qy_var = tk.StringVar(value="—")
        self.persl_qy_var = tk.StringVar(value="—")
        self.status_var = tk.StringVar(
            value="Select the six measurement files, then click Calculate."
        )

        self.results: CalculationResults | None = None
        self.tables: dict[str, pd.DataFrame] | None = None

        self.figure = Figure(figsize=(9, 7), dpi=100)

        self._configure_style()
        self._build_interface()

    def _configure_style(self) -> None:
        """Configure a clean ttk appearance."""

        style = ttk.Style(self)

        available = style.theme_names()
        if "vista" in available:
            style.theme_use("vista")
        elif "clam" in available:
            style.theme_use("clam")

        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("ResultValue.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("ResultName.TLabel", font=("Segoe UI", 10))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Secondary.TButton", padding=7)

    def _build_interface(self) -> None:
        """Create all widgets."""

        outer = ttk.Frame(self, padding=14)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(
            header,
            text="PersLQY Calculator",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text=(
                "Persistent and total luminescence quantum-yield calculation "
                "with embedded measurement plots"
            ),
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        body = ttk.Panedwindow(outer, orient="horizontal")
        body.pack(fill="both", expand=True)

        controls = ScrollableFrame(body)
        plot_area = ttk.Frame(body)
        body.add(controls, weight=0)
        body.add(plot_area, weight=1)

        controls.content.configure(padding=(0, 0, 12, 0))
        self._build_controls(controls.content)
        self._build_plot_area(plot_area)

        status = ttk.Label(
            outer,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padding=(8, 5),
        )
        status.pack(fill="x", pady=(10, 0))

    def _build_controls(self, parent: ttk.Frame) -> None:
        """Create file, background, and result controls."""

        files_frame = ttk.LabelFrame(
            parent,
            text="Measurement files",
            style="Section.TLabelframe",
            padding=10,
        )
        files_frame.pack(fill="x")

        for row, (key, label) in enumerate(self.FILE_FIELDS):
            ttk.Label(files_frame, text=label).grid(
                row=row,
                column=0,
                sticky="w",
                pady=4,
            )
            entry = ttk.Entry(
                files_frame,
                textvariable=self.file_variables[key],
                width=32,
                state="readonly",
            )
            entry.grid(row=row, column=1, sticky="ew", padx=(8, 6), pady=4)
            ttk.Button(
                files_frame,
                text="Browse…",
                command=lambda field=key: self.select_file(field),
                style="Secondary.TButton",
            ).grid(row=row, column=2, pady=4)

        files_frame.columnconfigure(1, weight=1)

        ttk.Button(
            files_frame,
            text="Select all files in sequence",
            command=self.select_all_files,
            style="Secondary.TButton",
        ).grid(
            row=len(self.FILE_FIELDS),
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(10, 0),
        )

        background_frame = ttk.LabelFrame(
            parent,
            text="Background correction",
            style="Section.TLabelframe",
            padding=10,
        )
        background_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(
            background_frame,
            text="The first 30 s are used by default.",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        ttk.Label(background_frame, text="Start time (s)").grid(
            row=1,
            column=0,
            sticky="w",
            pady=4,
        )
        ttk.Entry(
            background_frame,
            textvariable=self.background_start_var,
            width=12,
        ).grid(row=1, column=1, sticky="e", pady=4)

        ttk.Label(background_frame, text="Stop time (s)").grid(
            row=2,
            column=0,
            sticky="w",
            pady=4,
        )
        ttk.Entry(
            background_frame,
            textvariable=self.background_stop_var,
            width=12,
        ).grid(row=2, column=1, sticky="e", pady=4)

        results_frame = ttk.LabelFrame(
            parent,
            text="Results",
            style="Section.TLabelframe",
            padding=10,
        )
        results_frame.pack(fill="x", pady=(12, 0))

        ttk.Label(
            results_frame,
            text="TotalQY",
            style="ResultName.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            results_frame,
            textvariable=self.total_qy_var,
            style="ResultValue.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        ttk.Label(
            results_frame,
            text="PersLQY",
            style="ResultName.TLabel",
        ).grid(row=2, column=0, sticky="w")
        ttk.Label(
            results_frame,
            textvariable=self.persl_qy_var,
            style="ResultValue.TLabel",
        ).grid(row=3, column=0, sticky="w")

        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(
            actions,
            text="Calculate",
            command=self.calculate,
            style="Primary.TButton",
        ).pack(fill="x")

        self.save_button = ttk.Button(
            actions,
            text="Save plots…",
            command=self.save_plots,
            style="Secondary.TButton",
            state="disabled",
        )
        self.save_button.pack(fill="x", pady=(8, 0))

        ttk.Button(
            actions,
            text="Clear",
            command=self.clear,
            style="Secondary.TButton",
        ).pack(fill="x", pady=(8, 0))

    def _build_plot_area(self, parent: ttk.Frame) -> None:
        """Create the embedded Matplotlib canvas and toolbar."""

        plot_frame = ttk.LabelFrame(
            parent,
            text="Measurement overview",
            style="Section.TLabelframe",
            padding=6,
        )
        plot_frame.pack(fill="both", expand=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = ttk.Frame(plot_frame)
        toolbar_frame.pack(fill="x")
        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            toolbar_frame,
            pack_toolbar=False,
        )
        self.toolbar.update()
        self.toolbar.pack(side="left", fill="x")

        self._draw_placeholder()

    def _draw_placeholder(self) -> None:
        """Show an initial message in the plot area."""

        self.figure.clear()
        axis = self.figure.add_subplot(111)
        axis.axis("off")
        axis.text(
            0.5,
            0.55,
            "Select your measurement files\nand click Calculate",
            ha="center",
            va="center",
            fontsize=16,
        )
        axis.text(
            0.5,
            0.42,
            "The four measurement plots will appear here.",
            ha="center",
            va="center",
            fontsize=10,
        )
        self.canvas.draw_idle()

    def select_file(self, field: str) -> None:
        """Select one measurement file."""

        initial_directory = self._preferred_directory()
        selected = filedialog.askopenfilename(
            parent=self,
            title=dict(self.FILE_FIELDS)[field],
            initialdir=str(initial_directory),
            filetypes=DATA_FILE_TYPES,
        )

        if not selected:
            return

        self.file_variables[field].set(selected)

        if field == "emission":
            self._set_default_background_from_emission(Path(selected))

    def select_all_files(self) -> None:
        """Select all six files in their required order."""

        for field, label in self.FILE_FIELDS:
            initial_directory = self._preferred_directory()
            selected = filedialog.askopenfilename(
                parent=self,
                title=f"Select {label.lower()}",
                initialdir=str(initial_directory),
                filetypes=DATA_FILE_TYPES,
            )

            if not selected:
                self.status_var.set("File selection cancelled.")
                return

            self.file_variables[field].set(selected)

            if field == "emission":
                self._set_default_background_from_emission(Path(selected))

        self.status_var.set("All measurement files selected.")

    def _preferred_directory(self) -> Path:
        """Return a useful starting folder for file dialogs."""

        for variable in self.file_variables.values():
            value = variable.get().strip()
            if value:
                path = Path(value)
                if path.parent.is_dir():
                    return path.parent

        return Path.cwd()

    def _set_default_background_from_emission(self, path: Path) -> None:
        """Set the default background to the first 30 seconds of the data."""

        try:
            emission = read_table(path, {"t", "counts"}, "emission measurement")
            times = emission["t"].to_numpy(dtype=float)
            minimum_time = float(np.min(times))
            maximum_time = float(np.max(times))
            default_stop = min(minimum_time + 30.0, maximum_time)

            self.background_start_var.set(f"{minimum_time:g}")
            self.background_stop_var.set(f"{default_stop:g}")
        except Exception:
            # Full validation occurs when Calculate is pressed.
            self.background_start_var.set("0")
            self.background_stop_var.set("30")

    def _input_files(self) -> InputFiles:
        """Build and validate the InputFiles object from UI fields."""

        missing = [
            label
            for key, label in self.FILE_FIELDS
            if not self.file_variables[key].get().strip()
        ]

        if missing:
            raise ValueError(
                "Select all six measurement files before calculating.\n\n"
                "Missing:\n- " + "\n- ".join(missing)
            )

        return InputFiles(
            **{
                key: Path(self.file_variables[key].get())
                for key, _label in self.FILE_FIELDS
            }
        )

    def calculate(self) -> None:
        """Run the calculation and update the embedded plots."""

        try:
            files = self._input_files()
            background_start = float(self.background_start_var.get())
            background_stop = float(self.background_stop_var.get())

            self.status_var.set("Calculating…")
            self.update_idletasks()

            results, tables = calculate_quantum_yields(
                files,
                background_start,
                background_stop,
            )

            self.results = results
            self.tables = tables

            self.total_qy_var.set(f"{results.total_qy:.2f}%")
            self.persl_qy_var.set(f"{results.persl_qy:.2f}%")

            populate_figure(self.figure, tables, results)
            self.canvas.draw_idle()

            self.save_button.configure(state="normal")
            self.status_var.set(
                "Calculation completed. Use the plot toolbar to zoom or pan, "
                "or click Save plots to export the figure."
            )
        except ValueError as error:
            self.status_var.set("Calculation failed.")
            messagebox.showerror("Invalid input", str(error), parent=self)
        except Exception as error:
            self.status_var.set("Calculation failed.")
            messagebox.showerror(
                "PersLQY calculation error",
                str(error),
                parent=self,
            )

    def save_plots(self) -> None:
        """Save the currently displayed figure."""

        if self.results is None or self.tables is None:
            messagebox.showinfo(
                "Nothing to save",
                "Run a calculation before saving the plots.",
                parent=self,
            )
            return

        initial_directory = self._preferred_directory()
        selected = filedialog.asksaveasfilename(
            parent=self,
            title="Save measurement plots",
            initialdir=str(initial_directory),
            initialfile="measurement.png",
            defaultextension=".png",
            filetypes=PLOT_FILE_TYPES,
        )

        if not selected:
            return

        output_path = Path(selected)

        try:
            self.figure.savefig(output_path, dpi=300, bbox_inches="tight")
        except Exception as error:
            messagebox.showerror(
                "Could not save plot",
                str(error),
                parent=self,
            )
            return

        self.status_var.set(f"Plots saved to {output_path}")
        messagebox.showinfo(
            "Plots saved",
            f"The plots were saved successfully:\n\n{output_path}",
            parent=self,
        )

    def clear(self) -> None:
        """Clear selected files, results, and plots."""

        for variable in self.file_variables.values():
            variable.set("")

        self.background_start_var.set("0")
        self.background_stop_var.set("30")
        self.total_qy_var.set("—")
        self.persl_qy_var.set("—")
        self.results = None
        self.tables = None
        self.save_button.configure(state="disabled")
        self.status_var.set(
            "Select the six measurement files, then click Calculate."
        )
        self._draw_placeholder()


def main() -> None:
    """Start the PersLQY desktop application."""

    app = PersLQYApp()
    app.mainloop()


if __name__ == "__main__":
    main()
