"""Single-page web application for browsing and plotting BRML files."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from .io import read_brml, read_cif
from .pattern_calculator import calculate_powder_pattern

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}


HTML_APP = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Powder XRD Analyzer</title>
  <style>
    :root {
      --bg: #f5f1e8;
      --panel: rgba(255, 251, 245, 0.94);
      --panel-strong: rgba(249, 242, 229, 0.98);
      --ink: #1f2933;
      --muted: #5d6b78;
      --accent: #a53f2b;
      --line: rgba(165, 63, 43, 0.18);
      --shadow: 0 20px 45px rgba(102, 69, 43, 0.16);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(223, 176, 127, 0.35), transparent 35%),
        radial-gradient(circle at bottom right, rgba(165, 63, 43, 0.12), transparent 30%),
        linear-gradient(135deg, #f7f4ee, #f1e6d4 52%, #efe7db);
    }

    .shell {
      width: min(1440px, calc(100vw - 24px));
      margin: 12px auto;
      padding: 18px;
      border-radius: 28px;
      background: rgba(255, 255, 255, 0.38);
      backdrop-filter: blur(16px);
      box-shadow: var(--shadow);
    }

    .hero {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
      margin-bottom: 18px;
    }

    .hero h1 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3rem);
      letter-spacing: -0.04em;
    }

    .hero p {
      margin: 10px 0 0;
      color: var(--muted);
      max-width: 760px;
      line-height: 1.5;
    }

    .workspace {
      display: grid;
      grid-template-columns: minmax(320px, 450px) minmax(0, 1fr);
      gap: 18px;
      min-height: 78vh;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 18px;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
    }

    .panel h2, .panel h3 {
      margin: 0 0 10px;
      letter-spacing: -0.03em;
    }

    .path {
      font-family: "SFMono-Regular", "Consolas", monospace;
      font-size: 0.88rem;
      color: var(--muted);
      word-break: break-all;
    }

    .status {
      min-height: 1.4em;
      color: var(--muted);
      margin-top: 8px;
    }

    .sidebar {
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr);
      gap: 16px;
      min-height: 0;
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }

    .filter-row {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      margin-top: 12px;
    }

    .filter-label {
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 4px;
      display: block;
    }

    .select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 10px 12px;
      background: rgba(255, 255, 255, 0.78);
      color: var(--ink);
      font: inherit;
    }

    .button {
      border: 0;
      padding: 10px 14px;
      border-radius: 999px;
      cursor: pointer;
      font-weight: 700;
      color: white;
      background: linear-gradient(135deg, var(--accent), #d26b4c);
      box-shadow: 0 12px 26px rgba(165, 63, 43, 0.18);
    }

    .button.secondary {
      color: var(--ink);
      background: rgba(255, 255, 255, 0.7);
      box-shadow: none;
      border: 1px solid var(--line);
    }

    .file-list {
      display: grid;
      gap: 10px;
      max-height: 100%;
      overflow: auto;
      padding-right: 4px;
    }

    .file-card {
      width: 100%;
      text-align: left;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px;
      background: rgba(255, 255, 255, 0.68);
      transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
      cursor: pointer;
    }

    .file-card:hover {
      transform: translateY(-2px);
      border-color: rgba(165, 63, 43, 0.45);
      box-shadow: 0 16px 30px rgba(103, 76, 54, 0.12);
    }

    .file-card.selected {
      border-color: rgba(165, 63, 43, 0.7);
      background: var(--panel-strong);
      box-shadow: 0 16px 30px rgba(165, 63, 43, 0.12);
    }

    .file-card strong {
      display: block;
      margin-bottom: 6px;
      font-size: 1rem;
    }

    .file-meta {
      color: var(--muted);
      font-size: 0.86rem;
      margin-top: 3px;
    }

    .record-chip-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }

    .record-chip {
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.78);
      font-size: 0.8rem;
      color: var(--ink);
    }

    .comment {
      margin-top: 8px;
      color: var(--ink);
      font-size: 0.88rem;
      line-height: 1.35;
    }

    .selection-summary {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    .main {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 16px;
      min-height: 0;
    }

    .plot-summary {
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
      gap: 14px;
      align-items: start;
    }

    .plot-summary h2 {
      margin-bottom: 6px;
    }

    .plot-meta {
      min-width: 0;
    }

    .plot-meta .status {
      margin-top: 0;
    }

    .plot-meta .path {
      margin-top: 6px;
    }

    .plot-stats {
      display: grid;
      gap: 10px;
      min-width: 0;
    }

    .overlay-panel {
      display: grid;
      gap: 10px;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--line);
    }

    .textarea {
      width: 100%;
      min-height: 88px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 10px 12px;
      background: rgba(255, 255, 255, 0.78);
      color: var(--ink);
      font: inherit;
      line-height: 1.4;
    }

    .metrics {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
    }

    .metric {
      padding: 10px 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.68);
      border: 1px solid var(--line);
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 0.8rem;
      margin-bottom: 4px;
    }

    .metric strong {
      font-size: 0.98rem;
    }

    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid var(--line);
      font-size: 0.84rem;
    }

    .swatch {
      width: 12px;
      height: 12px;
      border-radius: 999px;
      flex: 0 0 auto;
    }

    .plot-wrap {
      background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(251,247,241,0.94));
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 12px;
      min-height: 0;
    }

    #plotSvg {
      width: 100%;
      height: 620px;
      display: block;
    }

    .hint {
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    .empty {
      padding: 32px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.7);
      border: 1px dashed rgba(165, 63, 43, 0.35);
      color: var(--muted);
      text-align: center;
    }

    @media (max-width: 1024px) {
      .workspace {
        grid-template-columns: 1fr;
      }

      .plot-summary {
        grid-template-columns: 1fr;
      }

      #plotSvg {
        height: 420px;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <div>
        <h1>Powder XRD Browser</h1>
        <p>Browse every <code>.brml</code> file under the current working directory, enrich the list from <code>experiment_record.csv</code>, filter by sample, and render one or many XRD patterns together.</p>
      </div>
    </div>

    <div class="workspace">
      <aside class="sidebar">
        <section class="panel">
          <h2>Workspace</h2>
          <div id="rootPath" class="path"></div>
          <div id="browserStatus" class="status">Loading files...</div>
          <div class="selection-summary">
            <span id="selectionCount">0 selected</span>
            <span id="fileCount">0 files</span>
          </div>
        </section>

        <section class="panel">
          <div class="toolbar">
            <button id="reloadFiles" class="button secondary" type="button">Reload Files</button>
            <button id="clearSelection" class="button secondary" type="button">Clear Selection</button>
            <button id="plotSelection" class="button" type="button">Plot Selected</button>
          </div>
          <div class="filter-row">
            <div>
              <label for="sampleFilter" class="filter-label">Sample Filter</label>
              <select id="sampleFilter" class="select">
                <option value="__all__">All Samples</option>
              </select>
            </div>
          </div>
          <div class="overlay-panel">
            <div>
              <label for="cifSelect" class="filter-label">CIF Overlay</label>
              <select id="cifSelect" class="select">
                <option value="">No CIF Selected</option>
              </select>
            </div>
            <div>
              <label for="wavelengthSelect" class="filter-label">Wavelength</label>
              <select id="wavelengthSelect" class="select">
                <option value="CuKa1">CuKa1</option>
                <option value="CuKa">CuKa</option>
                <option value="MoKa">MoKa</option>
              </select>
            </div>
            <div>
              <label for="hklInput" class="filter-label">HKL List</label>
              <textarea id="hklInput" class="textarea" placeholder="Examples: 0 0 2&#10;0 0 4&#10;1 1 1"></textarea>
            </div>
            <div class="toolbar">
              <button id="overlayPeaks" class="button secondary" type="button">Overlay HKL Peaks</button>
              <button id="clearOverlay" class="button secondary" type="button">Clear Overlay</button>
            </div>
          </div>
        </section>

        <section class="panel" style="min-height: 0;">
          <h2>BRML Files</h2>
          <div id="fileList" class="file-list"></div>
        </section>
      </aside>

      <main class="main">
        <section class="panel">
          <div class="plot-summary">
            <div class="plot-meta">
              <h2>Plot View</h2>
              <div id="plotStatus" class="status">Select one or more BRML files to render.</div>
              <div id="selectedPaths" class="path"></div>
            </div>
            <div class="plot-stats">
              <div id="plotMetrics" class="metrics"></div>
              <div id="plotLegend" class="legend"></div>
            </div>
          </div>
        </section>

        <section class="panel">
          <div id="plotContainer" class="plot-wrap">
            <svg id="plotSvg" viewBox="0 0 1100 620" preserveAspectRatio="none"></svg>
          </div>
          <div class="hint">Multiple selections are overlaid with separate colors. Dense scans are downsampled on the server for responsive rendering.</div>
        </section>
      </main>
    </div>
  </div>

  <script>
    const state = {
      files: [],
      cifFiles: [],
      selectedPaths: [],
      datasets: [],
      sampleFilter: "__all__",
      overlayPeaks: [],
    };

    const palette = ["#a53f2b", "#1d6f8c", "#7f8f1f", "#6f42c1", "#c05621", "#2f855a", "#805ad5", "#b83280"];

    const elements = {
      rootPath: document.getElementById("rootPath"),
      browserStatus: document.getElementById("browserStatus"),
      fileList: document.getElementById("fileList"),
      selectionCount: document.getElementById("selectionCount"),
      fileCount: document.getElementById("fileCount"),
      selectedPaths: document.getElementById("selectedPaths"),
      plotStatus: document.getElementById("plotStatus"),
      plotMetrics: document.getElementById("plotMetrics"),
      plotLegend: document.getElementById("plotLegend"),
      plotContainer: document.getElementById("plotContainer"),
      plotSvg: document.getElementById("plotSvg"),
      reloadFiles: document.getElementById("reloadFiles"),
      clearSelection: document.getElementById("clearSelection"),
      plotSelection: document.getElementById("plotSelection"),
      sampleFilter: document.getElementById("sampleFilter"),
      cifSelect: document.getElementById("cifSelect"),
      wavelengthSelect: document.getElementById("wavelengthSelect"),
      hklInput: document.getElementById("hklInput"),
      overlayPeaks: document.getElementById("overlayPeaks"),
      clearOverlay: document.getElementById("clearOverlay"),
    };

    function formatNumber(value, digits = 3) {
      return Number(value).toLocaleString(undefined, {
        maximumFractionDigits: digits,
      });
    }

    function visibleFiles() {
      if (state.sampleFilter === "__all__") {
        return state.files;
      }
      return state.files.filter((file) => file.sample === state.sampleFilter);
    }

    function updateSelectionSummary() {
      elements.selectionCount.textContent = `${state.selectedPaths.length} selected`;
      elements.fileCount.textContent = `${visibleFiles().length} visible / ${state.files.length} files`;
      elements.selectedPaths.textContent = state.selectedPaths.length
        ? state.selectedPaths.join(" | ")
        : "No files selected.";
    }

    function populateSampleFilter(samples = []) {
      elements.sampleFilter.innerHTML = '<option value="__all__">All Samples</option>';
      for (const sample of samples) {
        const option = document.createElement("option");
        option.value = sample;
        option.textContent = sample;
        elements.sampleFilter.appendChild(option);
      }
      if (![...elements.sampleFilter.options].some((option) => option.value === state.sampleFilter)) {
        state.sampleFilter = "__all__";
      }
      elements.sampleFilter.value = state.sampleFilter;
    }

    function populateCifSelect(cifFiles = []) {
      elements.cifSelect.innerHTML = '<option value="">No CIF Selected</option>';
      for (const cifFile of cifFiles) {
        const option = document.createElement("option");
        option.value = cifFile.relative_path;
        option.textContent = cifFile.relative_path;
        elements.cifSelect.appendChild(option);
      }
    }

    function parseHklInput() {
      const lines = elements.hklInput.value
        .split(/\\r?\\n|;/)
        .map((line) => line.trim())
        .filter(Boolean);

      return lines.map((line) => {
        const parts = line.split(/[\\s,]+/).filter(Boolean);
        if (parts.length !== 3) {
          throw new Error(`Invalid hkl entry: ${line}`);
        }
        const values = parts.map((part) => Number.parseInt(part, 10));
        if (values.some((value) => Number.isNaN(value))) {
          throw new Error(`Invalid hkl entry: ${line}`);
        }
        return values.join(",");
      });
    }

    function toggleSelection(path) {
      if (state.selectedPaths.includes(path)) {
        state.selectedPaths = state.selectedPaths.filter((item) => item !== path);
      } else {
        state.selectedPaths = [...state.selectedPaths, path];
      }
      renderFiles();
      updateSelectionSummary();
      if (state.selectedPaths.length) {
        loadPlots().catch(showPlotError);
      } else {
        resetPlotView();
      }
    }

    function renderFiles() {
      const files = visibleFiles();
      elements.fileList.innerHTML = "";

      if (!files.length) {
        elements.fileList.innerHTML = '<div class="empty">No <code>.brml</code> files match the current sample filter.</div>';
        return;
      }

      for (const file of files) {
        const card = document.createElement("div");
        card.className = "file-card";
        card.setAttribute("role", "button");
        card.tabIndex = 0;
        if (state.selectedPaths.includes(file.relative_path)) {
          card.classList.add("selected");
        }

        const sampleChip = file.sample ? `<span class="record-chip">Sample: ${file.sample}</span>` : "";
        const expChip = file.exp_id ? `<span class="record-chip">Exp ID: ${file.exp_id}</span>` : "";
        const comment = file.comment ? `<div class="comment">${file.comment}</div>` : "";

        card.innerHTML = `
          <div class="record-chip-row">${expChip}${sampleChip}</div>
          <strong>${file.name}</strong>
          <div class="file-meta">${file.relative_path}</div>
          <div class="file-meta">${formatNumber(file.size_bytes, 0)} bytes • ${new Date(file.modified_at * 1000).toLocaleString()}</div>
          ${comment}
        `;
        card.addEventListener("click", () => toggleSelection(file.relative_path));
        card.addEventListener("keydown", (event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            toggleSelection(file.relative_path);
          }
        });
        elements.fileList.appendChild(card);
      }
    }

    async function loadFiles() {
      elements.browserStatus.textContent = "Scanning for BRML files...";
      const response = await fetch("/api/files");
      let payload = null;
      try {
        payload = await response.json();
      } catch {
        throw new Error("The server did not return valid JSON for /api/files");
      }
      if (!response.ok) {
        throw new Error(payload.detail || "Failed to load file list");
      }
      state.files = payload.files || [];
      state.cifFiles = payload.cif_files || [];
      elements.rootPath.textContent = payload.root_directory;
      elements.browserStatus.textContent = payload.record_file_found
        ? `${state.files.length} BRML file(s) found • metadata loaded from experiment_record.csv`
        : `${state.files.length} BRML file(s) found • no experiment_record.csv detected`;
      state.selectedPaths = state.selectedPaths.filter((path) => state.files.some((file) => file.relative_path === path));
      populateSampleFilter(payload.samples || []);
      populateCifSelect(state.cifFiles);
      renderFiles();
      updateSelectionSummary();
    }

    function renderMetrics(items) {
      elements.plotMetrics.innerHTML = "";
      for (const item of items) {
        const metric = document.createElement("div");
        metric.className = "metric";
        metric.innerHTML = `<span>${item.label}</span><strong>${item.value}</strong>`;
        elements.plotMetrics.appendChild(metric);
      }
    }

    function renderLegend(datasets) {
      elements.plotLegend.innerHTML = "";
      for (const dataset of datasets) {
        const item = document.createElement("div");
        item.className = "legend-item";
        item.innerHTML = `<span class="swatch" style="background:${dataset.color}"></span><span>${dataset.file_name}</span>`;
        elements.plotLegend.appendChild(item);
      }
    }

    function buildScales(datasets) {
      const xMin = Math.min(...datasets.map((dataset) => dataset.two_theta_min));
      const xMax = Math.max(...datasets.map((dataset) => dataset.two_theta_max));
      const yMax = Math.max(...datasets.flatMap((dataset) => dataset.intensity));
      return { xMin, xMax, yMax };
    }

    function renderPlot(datasets, overlayPeaks = []) {
      elements.plotContainer.innerHTML = '<svg id="plotSvg" viewBox="0 0 1100 620" preserveAspectRatio="none"></svg>';
      elements.plotSvg = document.getElementById("plotSvg");

      const width = 1100;
      const height = 620;
      const left = 78;
      const right = 24;
      const top = 18;
      const bottom = 52;
      const plotWidth = width - left - right;
      const plotHeight = height - top - bottom;
      const { xMin, xMax, yMax } = buildScales(datasets);

      const mapX = (value) => left + ((value - xMin) / Math.max(xMax - xMin, 1e-9)) * plotWidth;
      const mapY = (value) => height - bottom - (value / Math.max(yMax, 1e-9)) * plotHeight;

      const xTicks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => ({
        value: xMin + ratio * (xMax - xMin),
        x: left + ratio * plotWidth,
      }));
      const yTicks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => ({
        value: ratio * yMax,
        y: height - bottom - ratio * plotHeight,
      }));

      const polyLines = datasets.map((dataset) => {
        const points = dataset.two_theta.map((x, index) => `${mapX(x)},${mapY(dataset.intensity[index])}`).join(" ");
        return `<polyline fill="none" stroke="${dataset.color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" points="${points}"></polyline>`;
      }).join("");

      const overlayLines = overlayPeaks.map((peak, index) => {
        const x = mapX(peak.two_theta);
        const labelY = top + 18 + (index % 3) * 16;
        return `
          <line x1="${x}" y1="${top}" x2="${x}" y2="${height - bottom}" stroke="rgba(31,41,51,0.45)" stroke-dasharray="4 4" stroke-width="1.1"></line>
          <text x="${x + 2}" y="${labelY}" font-size="11" fill="#1f2933" transform="rotate(-90, ${x + 2}, ${labelY})">${peak.label}</text>
        `;
      }).join("");

      elements.plotSvg.innerHTML = `
        <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
        <line x1="${left}" y1="${top}" x2="${left}" y2="${height - bottom}" stroke="rgba(31,41,51,0.7)" stroke-width="1.4"></line>
        <line x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}" stroke="rgba(31,41,51,0.7)" stroke-width="1.4"></line>
        ${xTicks.map((tick) => `
          <line x1="${tick.x}" y1="${height - bottom}" x2="${tick.x}" y2="${height - bottom + 8}" stroke="rgba(31,41,51,0.55)" stroke-width="1"></line>
          <text x="${tick.x}" y="${height - bottom + 24}" font-size="12" text-anchor="middle" fill="#5d6b78">${formatNumber(tick.value, 2)}</text>
        `).join("")}
        ${yTicks.map((tick) => `
          <line x1="${left - 8}" y1="${tick.y}" x2="${left}" y2="${tick.y}" stroke="rgba(31,41,51,0.55)" stroke-width="1"></line>
          <text x="${left - 12}" y="${tick.y + 4}" font-size="12" text-anchor="end" fill="#5d6b78">${formatNumber(tick.value, 0)}</text>
          <line x1="${left}" y1="${tick.y}" x2="${width - right}" y2="${tick.y}" stroke="rgba(165,63,43,0.08)" stroke-width="1"></line>
        `).join("")}
        ${overlayLines}
        ${polyLines}
        <text x="${(left + width - right) / 2}" y="${height - 12}" font-size="14" text-anchor="middle" fill="#1f2933">2θ (degrees)</text>
        <text x="22" y="${height / 2}" font-size="14" text-anchor="middle" fill="#1f2933" transform="rotate(-90, 22, ${height / 2})">Intensity</text>
      `;
    }

    async function maybeLoadCifOverlay(rangeMin, rangeMax) {
      const cifPath = elements.cifSelect.value;
      if (!cifPath) {
        state.overlayPeaks = [];
        return;
      }

      const hkls = parseHklInput();
      if (!hkls.length) {
        state.overlayPeaks = [];
        return;
      }

      const params = new URLSearchParams({
        cif_path: cifPath,
        wavelength: elements.wavelengthSelect.value,
        two_theta_min: String(rangeMin),
        two_theta_max: String(rangeMax),
      });
      for (const hkl of hkls) {
        params.append("hkl", hkl);
      }

      const response = await fetch(`/api/cif-peaks?${params.toString()}`);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Failed to load CIF peaks");
      }
      state.overlayPeaks = payload.peaks;
    }

    async function loadPlots() {
      if (!state.selectedPaths.length) {
        resetPlotView();
        return;
      }

      elements.plotStatus.textContent = "Loading BRML pattern(s)...";
      const params = new URLSearchParams();
      for (const path of state.selectedPaths) {
        params.append("path", path);
      }

      const response = await fetch(`/api/plots?${params.toString()}`);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Failed to load plots");
      }

      state.datasets = payload.datasets.map((dataset, index) => ({
        ...dataset,
        color: palette[index % palette.length],
      }));

      await maybeLoadCifOverlay(payload.global_two_theta_min, payload.global_two_theta_max);
      renderPlot(state.datasets, state.overlayPeaks);
      renderLegend(state.datasets);
      renderMetrics([
        { label: "Selected Files", value: formatNumber(state.datasets.length, 0) },
        { label: "Rendered Points", value: formatNumber(payload.total_rendered_points, 0) },
        { label: "Original Points", value: formatNumber(payload.total_original_points, 0) },
        { label: "2θ Range", value: `${formatNumber(payload.global_two_theta_min, 2)} - ${formatNumber(payload.global_two_theta_max, 2)}` },
      ]);
      elements.plotStatus.textContent = `Rendered ${state.datasets.length} pattern(s).`;
    }

    function resetPlotView() {
      state.datasets = [];
      state.overlayPeaks = [];
      elements.plotStatus.textContent = "Select one or more BRML files to render.";
      elements.selectedPaths.textContent = "No files selected.";
      elements.plotMetrics.innerHTML = "";
      elements.plotLegend.innerHTML = "";
      elements.plotContainer.innerHTML = '<div class="empty">Choose one or more BRML files from the left panel to draw them here.</div>';
    }

    function showPlotError(error) {
      elements.plotStatus.textContent = error.message;
      elements.plotMetrics.innerHTML = "";
      elements.plotLegend.innerHTML = "";
      elements.plotContainer.innerHTML = '<div class="empty">Could not render the selected BRML file set.</div>';
    }

    async function bootstrap() {
      elements.reloadFiles.addEventListener("click", () => loadFiles().catch(showPlotError));
      elements.clearSelection.addEventListener("click", () => {
        state.selectedPaths = [];
        renderFiles();
        updateSelectionSummary();
        resetPlotView();
      });
      elements.plotSelection.addEventListener("click", () => loadPlots().catch(showPlotError));
      elements.overlayPeaks.addEventListener("click", () => loadPlots().catch(showPlotError));
      elements.clearOverlay.addEventListener("click", () => {
        elements.cifSelect.value = "";
        elements.hklInput.value = "";
        state.overlayPeaks = [];
        if (state.datasets.length) {
          renderPlot(state.datasets, []);
        }
      });
      elements.sampleFilter.addEventListener("change", (event) => {
        state.sampleFilter = event.target.value;
        renderFiles();
        updateSelectionSummary();
      });

      try {
        await loadFiles();
        resetPlotView();
      } catch (error) {
        elements.browserStatus.textContent = error.message;
        showPlotError(error);
      }
    }

    bootstrap();
  </script>
</body>
</html>
"""


def _normalize_header(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "")


def _normalize_id(value: str) -> str:
    return value.strip().lower()


def _load_experiment_records(root_dir: Path) -> tuple[dict[str, dict[str, str]], list[str], bool]:
    csv_path = root_dir / "experiment_record.csv"
    if not csv_path.is_file():
        return {}, [], False

    records: dict[str, dict[str, str]] = {}
    sample_names: set[str] = set()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    if not rows:
        return {}, [], True

    first_row = [cell.strip() for cell in rows[0]]
    header_like = len(first_row) >= 3 and _normalize_header(first_row[0]) in {"exp-id", "expid"}
    data_rows = rows[1:] if header_like else rows

    for row in data_rows:
        if len(row) < 3:
            continue
        exp_id, sample, comment = row[0].strip(), row[1].strip(), row[2].strip()
        if not exp_id:
            continue
        normalized = _normalize_id(exp_id)
        records[normalized] = {
            "exp_id": exp_id,
            "sample": sample,
            "comment": comment,
        }
        if sample:
            sample_names.add(sample)

    return records, sorted(sample_names), True


def _match_record(relative_path: Path, records: dict[str, dict[str, str]]) -> dict[str, str] | None:
    if not records:
        return None

    stem = relative_path.stem.lower()
    full_without_suffix = relative_path.with_suffix("").as_posix().lower()

    if stem in records:
        return records[stem]
    if full_without_suffix in records:
        return records[full_without_suffix]

    for exp_id, record in records.items():
        if exp_id and (exp_id in stem or exp_id in full_without_suffix):
            return record

    return None


def _walk_matching_files(root_dir: Path, suffix: str, *, limit_to: Path | None = None) -> list[Path]:
    search_root = (limit_to or root_dir).resolve()
    matched: list[Path] = []

    for current_root, dir_names, file_names in os.walk(search_root):
        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if dir_name not in SKIP_DIR_NAMES and not dir_name.endswith(".egg-info")
        ]
        current_path = Path(current_root)
        for file_name in file_names:
            if not file_name.lower().endswith(suffix):
                continue
            matched.append(current_path / file_name)

    return sorted(matched)


def _iter_brml_files(root_dir: Path) -> tuple[list[dict[str, object]], list[str], bool]:
    records, _samples, record_file_found = _load_experiment_records(root_dir)
    files = []
    matched_samples: set[str] = set()

    for path in _walk_matching_files(root_dir, ".brml"):
        stat = path.stat()
        relative_path = path.relative_to(root_dir)
        record = _match_record(relative_path, records) or {}
        sample = record.get("sample", "")
        if sample:
            matched_samples.add(sample)
        files.append(
            {
                "name": path.name,
                "relative_path": relative_path.as_posix(),
                "size_bytes": stat.st_size,
                "modified_at": stat.st_mtime,
                "exp_id": record.get("exp_id", ""),
                "sample": sample,
                "comment": record.get("comment", ""),
            }
        )

    return files, sorted(matched_samples), record_file_found


def _iter_cif_files(root_dir: Path) -> list[dict[str, str]]:
    cif_root = root_dir / "cifs"
    if not cif_root.is_dir():
        return []

    files = []
    for path in _walk_matching_files(root_dir, ".cif", limit_to=cif_root):
        files.append(
            {
                "name": path.name,
                "relative_path": path.relative_to(root_dir).as_posix(),
            }
        )
    return files


def _resolve_brml_path(root_dir: Path, relative_path: str) -> Path:
    candidate = (root_dir / relative_path).resolve()
    root_resolved = root_dir.resolve()

    if not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {relative_path}")
    if candidate.suffix.lower() != ".brml":
        raise HTTPException(status_code=400, detail="Only .brml files are supported")
    if root_resolved not in candidate.parents:
        raise HTTPException(status_code=403, detail="File is outside the workspace root")
    return candidate


def _downsample(values_x, values_y, max_points: int = 4000) -> tuple[list[float], list[float]]:
    if len(values_x) <= max_points:
        return values_x.tolist(), values_y.tolist()

    stride = max(len(values_x) // max_points, 1)
    return values_x[::stride].tolist(), values_y[::stride].tolist()


def _serialize_dataset(workspace_root: Path, relative_path: str) -> dict[str, object]:
    brml_path = _resolve_brml_path(workspace_root, relative_path)
    try:
        two_theta, intensity = read_brml(brml_path)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to parse BRML {relative_path}: {exc}") from exc

    sampled_two_theta, sampled_intensity = _downsample(two_theta, intensity)
    return {
        "file_name": brml_path.name,
        "relative_path": brml_path.relative_to(workspace_root).as_posix(),
        "two_theta": sampled_two_theta,
        "intensity": sampled_intensity,
        "point_count": len(sampled_two_theta),
        "original_point_count": int(len(two_theta)),
        "two_theta_min": float(two_theta.min()),
        "two_theta_max": float(two_theta.max()),
        "intensity_max": float(intensity.max()),
    }


def _resolve_cif_path(root_dir: Path, relative_path: str) -> Path:
    candidate = (root_dir / relative_path).resolve()
    root_resolved = root_dir.resolve()

    if not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"CIF file not found: {relative_path}")
    if candidate.suffix.lower() != ".cif":
        raise HTTPException(status_code=400, detail="Only .cif files are supported")
    if root_resolved not in candidate.parents:
        raise HTTPException(status_code=403, detail="CIF file is outside the workspace root")
    return candidate


def _serialize_cif_peaks(
    workspace_root: Path,
    cif_relative_path: str,
    hkl_values: list[str],
    wavelength: str,
    two_theta_range: tuple[float, float] | None,
) -> dict[str, object]:
    cif_path = _resolve_cif_path(workspace_root, cif_relative_path)
    structure = read_cif(cif_path)
    pattern = calculate_powder_pattern(structure, wavelength=wavelength, two_theta_range=two_theta_range)

    requested_hkls = {tuple(int(part) for part in value.split(",")) for value in hkl_values}
    peaks = []

    for two_theta, intensity, hkl_options in zip(pattern.x, pattern.y, pattern.hkls):
        matched_hkls = []
        for hkl_info in hkl_options:
            hkl_tuple = tuple(hkl_info["hkl"])
            if hkl_tuple in requested_hkls:
                matched_hkls.append(hkl_tuple)
        if matched_hkls:
            label = " / ".join(f"({h},{k},{l})" for h, k, l in matched_hkls)
            peaks.append(
                {
                    "two_theta": float(two_theta),
                    "intensity": float(intensity),
                    "label": label,
                }
            )

    return {
        "cif_path": cif_path.relative_to(workspace_root).as_posix(),
        "peak_count": len(peaks),
        "peaks": peaks,
    }


def create_app(root_dir: str | Path | None = None) -> FastAPI:
    app = FastAPI(title="Powder XRD Analyzer WebApp")
    configured_root = root_dir or os.environ.get("POWDER_XRD_ANALYZER_WEBAPP_ROOT") or Path.cwd()
    workspace_root = Path(configured_root).resolve()

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return HTML_APP

    @app.get("/api/files")
    async def list_files() -> dict[str, object]:
        files, samples, record_file_found = _iter_brml_files(workspace_root)
        return {
            "root_directory": workspace_root.as_posix(),
            "files": files,
            "samples": samples,
            "record_file_found": record_file_found,
            "cif_files": _iter_cif_files(workspace_root),
        }

    @app.get("/api/plots")
    async def plot_files(path: list[str] = Query(..., description="One or more relative BRML paths")) -> dict[str, object]:
        datasets = [_serialize_dataset(workspace_root, item) for item in path]
        return {
            "datasets": datasets,
            "total_rendered_points": sum(dataset["point_count"] for dataset in datasets),
            "total_original_points": sum(dataset["original_point_count"] for dataset in datasets),
            "global_two_theta_min": min(dataset["two_theta_min"] for dataset in datasets),
            "global_two_theta_max": max(dataset["two_theta_max"] for dataset in datasets),
        }

    @app.get("/api/cif-peaks")
    async def cif_peaks(
        cif_path: str = Query(..., description="Relative path to the CIF file"),
        hkl: list[str] = Query(..., description="Requested hkl triplets, e.g. 0,0,2"),
        wavelength: str = Query("CuKa1", description="Wavelength passed to calculate_powder_pattern"),
        two_theta_min: float | None = Query(None),
        two_theta_max: float | None = Query(None),
    ) -> dict[str, object]:
        two_theta_range = None
        if two_theta_min is not None and two_theta_max is not None:
            two_theta_range = (two_theta_min, two_theta_max)

        return _serialize_cif_peaks(workspace_root, cif_path, hkl, wavelength, two_theta_range)

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Powder XRD Analyzer BRML web application.")
    parser.add_argument(
        "--root",
        default=".",
        help="Workspace root to scan recursively for .brml files. Defaults to the current directory.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn auto-reload during development.")
    args = parser.parse_args()

    os.environ["POWDER_XRD_ANALYZER_WEBAPP_ROOT"] = str(Path(args.root).resolve())
    uvicorn.run(
        "powder_xrd_analyzer.webapp:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
