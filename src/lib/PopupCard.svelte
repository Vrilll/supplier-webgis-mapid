<script>
  import { PLOT_PERCENTILES, PLOT_MEDIAN_HA, PLOT_COUNT } from './plotStats.js';

  export let props = {};
  export let lngLat = [0, 0];
  export let overlap = 1;
  export let onClose = () => {};

  let copied = false;

  $: area = Number.isFinite(Number(props.plotareaha)) && props.plotareaha !== null
    ? Number(props.plotareaha)
    : null;
  // Rank of this plot among all plots: index of the highest percentile it reaches.
  $: rank = area === null ? null : Math.max(0, PLOT_PERCENTILES.findLastIndex((v) => v <= area));
  $: comparison = rank === null
    ? 'No plot area recorded'
    : area > PLOT_MEDIAN_HA
      ? `Larger than ${rank}% of plots`
      : area < PLOT_MEDIAN_HA
        ? `Smaller than ${100 - rank}% of plots`
        : 'Exactly the median plot size';
  $: [lng, lat] = lngLat;
  $: coordText = `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  $: regionParts = String(props.regionlabel ?? '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  const fmtHa = (v) => v.toLocaleString('en-US', { maximumFractionDigits: 2 });
  const fmtM2 = (v) => Math.round(v * 10000).toLocaleString('en-US');

  async function copyCoords() {
    try {
      await navigator.clipboard.writeText(coordText);
      copied = true;
      setTimeout(() => (copied = false), 1600);
    } catch {
      copied = false;
    }
  }
</script>

<article class="card" aria-label="Supplier plot details">
  <header>
    <div>
      <p class="fid">Plot #{props.FID ?? '—'}</p>
      <h2>{props.entityname ?? 'Unnamed supplier'}</h2>
    </div>
    <button class="close" type="button" on:click={onClose} aria-label="Close details">
      <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">
        <path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      </svg>
    </button>
  </header>

  <section class="area">
    <p class="figure">
      {#if area !== null}
        <span class="num">{fmtHa(area)}</span><span class="unit">ha</span>
      {:else}
        <span class="num muted">—</span>
      {/if}
    </p>
    {#if area !== null}
      <p class="m2">{fmtM2(area)} m²</p>
    {/if}

    {#if rank !== null}
      <div class="rank" role="img" aria-label="{comparison}, among {PLOT_COUNT.toLocaleString('en-US')} plots">
        <div class="track">
          <span class="median" style="left: 50%"></span>
          <span class="marker" style="left: {rank}%"></span>
        </div>
        <div class="scale">
          <span>smallest</span>
          <span>median {fmtHa(PLOT_MEDIAN_HA)} ha</span>
          <span>largest</span>
        </div>
      </div>
    {/if}
    <p class="comparison">{comparison}</p>
  </section>

  <dl>
    <div>
      <dt>Region</dt>
      <dd>
        {#if regionParts.length}
          {regionParts.join(', ')}
        {:else}
          —
        {/if}
      </dd>
    </div>
    <div>
      <dt>Country</dt>
      <dd>{props.countryname ?? '—'}</dd>
    </div>
    <div>
      <dt>Location</dt>
      <dd class="coords">
        <span>{coordText}</span>
        <button type="button" on:click={copyCoords}>{copied ? 'Copied' : 'Copy'}</button>
      </dd>
    </div>
  </dl>

  {#if overlap > 1}
    <p class="overlap">{overlap - 1} more {overlap - 1 === 1 ? 'plot sits' : 'plots sit'} at this spot. Zoom in to pick one.</p>
  {/if}
</article>

<style>
  .card {
    width: 300px;
    max-width: calc(100vw - 40px);
    font-family: var(--font-body);
    color: var(--ink);
  }

  header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 14px 14px 10px 16px;
  }

  .fid {
    margin: 0 0 2px;
    font-size: 12.5px;
    color: var(--muted);
    font-variant-numeric: tabular-nums;
  }

  h2 {
    margin: 0;
    font-family: var(--font-display);
    font-size: 19px;
    font-weight: 650;
    line-height: 1.15;
    letter-spacing: -0.01em;
    overflow-wrap: anywhere;
  }

  .close {
    flex-shrink: 0;
    display: grid;
    place-items: center;
    width: 28px;
    height: 28px;
    border: 0;
    border-radius: 50%;
    background: transparent;
    color: var(--muted);
    cursor: pointer;
  }

  .close:hover {
    background: var(--line-soft);
    color: var(--ink);
  }

  .area {
    margin: 0 10px;
    padding: 12px 12px 12px;
    background: var(--forest-tint);
    border-radius: 10px;
  }

  .figure {
    margin: 0;
    display: flex;
    align-items: baseline;
    gap: 5px;
    color: var(--forest-deep);
  }

  .num {
    font-family: var(--font-display);
    font-size: 34px;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
  }

  .num.muted {
    color: var(--muted);
  }

  .unit {
    font-size: 16px;
    font-weight: 600;
  }

  .m2 {
    margin: 3px 0 0;
    font-size: 13px;
    color: var(--forest-deep);
    opacity: 0.75;
    font-variant-numeric: tabular-nums;
  }

  .rank {
    margin-top: 12px;
  }

  .track {
    position: relative;
    height: 8px;
    border-radius: 4px;
    background: linear-gradient(90deg, #cfe3d6, #7fb495 50%, #0f6f4a);
  }

  .median {
    position: absolute;
    top: -3px;
    width: 1.5px;
    height: 14px;
    background: var(--forest-deep);
    opacity: 0.45;
    transform: translateX(-50%);
  }

  .marker {
    position: absolute;
    top: 50%;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--amber);
    border: 2.5px solid #fff;
    box-shadow: 0 0 0 1px rgba(24, 36, 29, 0.25);
    transform: translate(-50%, -50%);
  }

  .scale {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    font-size: 11.5px;
    color: var(--forest-deep);
    opacity: 0.75;
  }

  .comparison {
    margin: 8px 0 0;
    font-size: 13.5px;
    font-weight: 600;
    color: var(--forest-deep);
  }

  dl {
    margin: 0;
    padding: 10px 16px 14px;
  }

  dl div {
    display: grid;
    grid-template-columns: 72px 1fr;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid var(--line-soft);
  }

  dl div:last-child {
    border-bottom: 0;
  }

  dt {
    font-size: 13px;
    color: var(--muted);
  }

  dd {
    margin: 0;
    font-size: 13.5px;
    line-height: 1.35;
  }

  .coords {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }

  .coords button {
    padding: 2px 9px;
    font: inherit;
    font-size: 12px;
    font-weight: 600;
    color: var(--forest);
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 999px;
    cursor: pointer;
  }

  .coords button:hover {
    border-color: var(--forest);
  }

  .overlap {
    margin: 0;
    padding: 9px 16px 12px;
    font-size: 12.5px;
    color: var(--muted);
    border-top: 1px solid var(--line-soft);
  }

  button:focus-visible {
    outline: 2px solid var(--forest);
    outline-offset: 2px;
  }
</style>
