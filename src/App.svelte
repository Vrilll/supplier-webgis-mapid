<script>
  import MapView from './lib/MapView.svelte';
  import { SUPPLIER_COUNT } from './lib/plotStats.js';

  let basemap = 'street';
  let showPoints = false;
  let everLoaded = false;
  let tilesOk = true;
  let basemapOk = true;
  // Phones start with the panel folded so the map is visible first.
  let panelOpen = typeof window === 'undefined' || window.innerWidth > 640;

  const options = [
    { id: 'street', label: 'MAPID Street 2D', swatch: ['#f2efe9', '#f6c96b', '#a9cfe0'] },
    { id: 'light', label: 'MAPID Light', swatch: ['#f7f7f5', '#e3e3df', '#c9d6dc'] },
    { id: 'satellite', label: 'MAPID Satellite', swatch: ['#3f4f2c', '#6b7a45', '#2b3a3e'] },
    { id: 'demo', label: 'MapLibre Demo (fallback)', swatch: ['#d8e6f0', '#e8d9b8', '#ffffff'] }
  ];

  $: if (showPoints) everLoaded = true;
  $: status = !showPoints
    ? everLoaded
      ? 'Points are hidden. Tiles already downloaded stay cached.'
      : 'Basemap only. Points are not loaded yet.'
    : tilesOk
      ? 'MVT is on. Pan the map and watch the small vector tile requests in DevTools.'
      : 'Point tiles did not load. Check that the tile server is running.';

  function togglePoints() {
    showPoints = !showPoints;
  }
</script>

<div class="app">
  <MapView
    {basemap}
    {showPoints}
    on:tiles={(e) => (tilesOk = e.detail.ok)}
    on:basemap={(e) => (basemapOk = e.detail.ok)}
  />

  <aside class:collapsed={!panelOpen}>
    <header>
      <div>
        <h1>Supplier WebGIS</h1>
        <p class="sub">{SUPPLIER_COUNT.toLocaleString('en-US')} supplier plots in Ivory Coast</p>
      </div>
      <button
        class="collapse"
        type="button"
        aria-expanded={panelOpen}
        aria-controls="panel-body"
        on:click={() => (panelOpen = !panelOpen)}
      >
        {panelOpen ? 'Hide' : 'Show'}
      </button>
    </header>

    <div id="panel-body" class="body" hidden={!panelOpen}>
      <section>
        <h2>Layers</h2>
        <div class="layer" class:on={showPoints}>
          <span class="dot" aria-hidden="true"></span>
          <span class="layer-name" id="points-label">Supplier points</span>
          <button
            class="switch"
            type="button"
            role="switch"
            aria-checked={showPoints}
            aria-labelledby="points-label"
            on:click={togglePoints}
          >
            <span class="thumb"></span>
          </button>
        </div>
        <p class="status" class:warn={showPoints && !tilesOk} aria-live="polite">{status}</p>
      </section>

      <section>
        <h2 id="basemap-label">Basemap</h2>
        <div class="basemaps" role="radiogroup" aria-labelledby="basemap-label">
          {#each options as option}
            <label class="basemap" class:active={basemap === option.id}>
              <input type="radio" name="basemap" value={option.id} bind:group={basemap} />
              <span class="swatch" aria-hidden="true">
                {#each option.swatch as color}
                  <span style="background: {color}"></span>
                {/each}
              </span>
              <span>{option.label}</span>
            </label>
          {/each}
        </div>
        {#if !basemapOk}
          <p class="status warn">
            This basemap did not load. Check VITE_MAPID_KEY in .env, or pick MapLibre Demo.
          </p>
        {/if}
      </section>

      <p class="note">Click a green point to read the supplier, plot area, and region.</p>
      <p class="credit">MAPID × BINUS mini certification. Basemap © MAPID.</p>
    </div>
  </aside>
</div>

<style>
  .app {
    position: relative;
    height: 100%;
    overflow: hidden;
  }

  aside {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 2;
    width: 296px;
    max-height: calc(100% - 24px);
    overflow-y: auto;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 14px;
    box-shadow: 0 10px 30px -12px rgba(16, 40, 28, 0.35);
  }

  header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 16px 16px 14px 18px;
  }

  h1 {
    margin: 0;
    font-family: var(--font-display);
    font-size: 23px;
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.015em;
  }

  .sub {
    margin: 4px 0 0;
    font-size: 13.5px;
    color: var(--muted);
  }

  .collapse {
    flex-shrink: 0;
    padding: 4px 10px;
    font: inherit;
    font-size: 13px;
    font-weight: 600;
    color: var(--forest);
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 999px;
    cursor: pointer;
  }

  .body {
    padding: 0 18px 16px;
  }

  section {
    padding: 14px 0;
    border-top: 1px solid var(--line-soft);
  }

  h2 {
    margin: 0 0 10px;
    font-size: 14px;
    font-weight: 700;
  }

  .layer {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border: 1px solid var(--line);
    border-radius: 10px;
    transition: background 0.15s, border-color 0.15s;
  }

  .layer.on {
    background: var(--forest-tint);
    border-color: #b7d6c3;
  }

  .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--forest);
    box-shadow: 0 0 0 2px #fff, 0 0 0 3px var(--line);
    opacity: 0.4;
    transition: opacity 0.15s;
  }

  .layer.on .dot {
    opacity: 1;
  }

  .layer-name {
    flex: 1;
    font-size: 14.5px;
    font-weight: 600;
  }

  .switch {
    position: relative;
    width: 42px;
    height: 24px;
    padding: 0;
    border: 0;
    border-radius: 999px;
    background: #c3ccc6;
    cursor: pointer;
    transition: background 0.15s;
  }

  .switch[aria-checked='true'] {
    background: var(--forest);
  }

  .thumb {
    position: absolute;
    top: 3px;
    left: 3px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
    transition: transform 0.15s;
  }

  .switch[aria-checked='true'] .thumb {
    transform: translateX(18px);
  }

  .status {
    margin: 10px 0 0;
    font-size: 13.5px;
    line-height: 1.45;
    color: var(--ink-soft);
  }

  .status.warn {
    color: #8a4b00;
  }

  .basemaps {
    display: grid;
    gap: 6px;
  }

  .basemap {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 10px;
    font-size: 14px;
    border: 1px solid transparent;
    border-radius: 9px;
    cursor: pointer;
  }

  .basemap:hover {
    background: var(--line-soft);
  }

  .basemap.active {
    border-color: var(--forest);
    background: #fff;
    font-weight: 600;
  }

  .basemap input {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .basemap:has(input:focus-visible) {
    outline: 2px solid var(--forest);
    outline-offset: 1px;
  }

  .swatch {
    display: flex;
    width: 30px;
    height: 20px;
    overflow: hidden;
    border-radius: 5px;
    box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.12);
  }

  .swatch span {
    flex: 1;
  }

  .note {
    margin: 0;
    padding-top: 14px;
    border-top: 1px solid var(--line-soft);
    font-size: 13.5px;
    line-height: 1.45;
    color: var(--ink-soft);
  }

  .credit {
    margin: 10px 0 0;
    font-size: 12px;
    color: var(--muted);
  }

  button:focus-visible {
    outline: 2px solid var(--forest);
    outline-offset: 2px;
  }

  @media (max-width: 640px) {
    aside {
      top: auto;
      bottom: calc(10px + env(safe-area-inset-bottom, 0px));
      left: 10px;
      right: 10px;
      width: auto;
      max-height: 60%;
    }

    header {
      padding: 12px 14px 10px 16px;
    }

    h1 {
      font-size: 20px;
    }

    .body {
      padding: 0 16px 14px;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .layer,
    .dot,
    .switch,
    .thumb {
      transition: none;
    }
  }
</style>
