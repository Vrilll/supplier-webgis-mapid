<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import PopupCard from './PopupCard.svelte';
  import { basemaps, MVT_TILES, MVT_SOURCE_LAYER, MAP_CENTER, MAP_ZOOM } from './config.js';

  export let basemap = 'street';
  // Toggle on/off for the supplier point layer (HomeTask 3).
  export let showPoints = false;

  const dispatch = createEventDispatcher();

  let container;
  let map;
  let popup;
  let appliedBasemap = basemap;
  let styleReady = false;
  // Becomes true the first time points are switched on. From then on the
  // source stays in the style and the toggle only flips visibility, so
  // turning points back on does not request the tiles again.
  let pointsLoaded = false;
  let tilesLoaded = false;

  const SOURCE_ID = 'suppliers';
  const LAYER_ID = 'suppliers-circles';
  const SELECTED_ID = 'suppliers-selected';
  const NONE = -1;

  const circlePaint = {
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 3, 12, 6, 16, 9],
    'circle-color': '#0f6f4a',
    'circle-stroke-width': 1,
    'circle-stroke-color': '#ffffff'
  };

  const selectedPaint = {
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 6, 7, 12, 11, 16, 15],
    'circle-color': 'rgba(0,0,0,0)',
    'circle-stroke-width': 3,
    'circle-stroke-color': '#e0a526'
  };

  function onSupplierClick(event) {
    const features = event.features ?? [];
    if (!features.length) return;
    const feature = features[0];
    // A point near a tile edge can be returned twice, so count unique FIDs.
    const overlap = new Set(features.map((f) => f.properties?.FID)).size;
    const lngLat = feature.geometry?.type === 'Point'
      ? feature.geometry.coordinates
      : [event.lngLat.lng, event.lngLat.lat];
    openCard(feature.properties, lngLat, overlap);
  }

  // A fresh popup per click. Reusing one popup with closeOnClick makes the
  // same click that opens it also close it, because MapLibre runs the old
  // close listener after the layer click handler.
  function openCard(props, lngLat, overlap) {
    popup?.remove();
    const node = document.createElement('div');
    let thisPopup;
    const thisCard = new PopupCard({
      target: node,
      props: { props, lngLat, overlap, onClose: () => thisPopup.remove() }
    });
    thisPopup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: true,
      maxWidth: 'none',
      offset: 14,
      className: 'plot-popup'
    })
      .setLngLat(lngLat)
      .setDOMContent(node);
    thisPopup.on('close', () => {
      thisCard.$destroy();
      if (popup === thisPopup) {
        popup = null;
        setSelected(NONE);
      }
    });
    popup = thisPopup;
    setSelected(props.FID);
    thisPopup.addTo(map);
  }

  function setSelected(fid) {
    if (map?.getLayer(SELECTED_ID)) {
      map.setFilter(SELECTED_ID, ['==', ['get', 'FID'], fid ?? NONE]);
    }
  }

  function onPointer() {
    map.getCanvas().style.cursor = 'pointer';
  }

  function onPointerOut() {
    map.getCanvas().style.cursor = '';
  }

  function bindClicks() {
    map.on('click', LAYER_ID, onSupplierClick);
    map.on('mouseenter', LAYER_ID, onPointer);
    map.on('mouseleave', LAYER_ID, onPointerOut);
  }

  function unbindClicks() {
    map.off('click', LAYER_ID, onSupplierClick);
    map.off('mouseenter', LAYER_ID, onPointer);
    map.off('mouseleave', LAYER_ID, onPointerOut);
  }

  function visibility() {
    return showPoints ? 'visible' : 'none';
  }

  // setStyle drops custom layers. style.load calls this again after each basemap switch.
  function addSupplierLayer() {
    if (!map.getStyle()) return;
    unbindClicks();
    if (map.getLayer(SELECTED_ID)) map.removeLayer(SELECTED_ID);
    if (map.getLayer(LAYER_ID)) map.removeLayer(LAYER_ID);
    if (map.getSource(SOURCE_ID)) map.removeSource(SOURCE_ID);

    map.addSource(SOURCE_ID, {
      type: 'vector',
      tiles: [MVT_TILES],
      minzoom: 0,
      maxzoom: 14
    });
    map.addLayer({
      id: LAYER_ID,
      type: 'circle',
      source: SOURCE_ID,
      'source-layer': MVT_SOURCE_LAYER,
      layout: { visibility: visibility() },
      paint: circlePaint
    });
    map.addLayer({
      id: SELECTED_ID,
      type: 'circle',
      source: SOURCE_ID,
      'source-layer': MVT_SOURCE_LAYER,
      layout: { visibility: visibility() },
      filter: ['==', ['get', 'FID'], NONE],
      paint: selectedPaint
    });
    bindClicks();
  }

  function onStyleLoad() {
    styleReady = true;
    if (pointsLoaded) addSupplierLayer();
    dispatch('basemap', { ok: true });
  }

  function syncPoints(on) {
    if (!map || !styleReady) return;
    if (on && !pointsLoaded) {
      pointsLoaded = true;
      addSupplierLayer();
      return;
    }
    if (!map.getLayer(LAYER_ID)) return;
    map.setLayoutProperty(LAYER_ID, 'visibility', visibility());
    map.setLayoutProperty(SELECTED_ID, 'visibility', visibility());
    if (!on) popup?.remove();
  }

  $: syncPoints(showPoints, styleReady);

  onMount(() => {
    map = new maplibregl.Map({
      container,
      style: basemaps[basemap],
      center: MAP_CENTER,
      zoom: MAP_ZOOM
    });
    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');
    map.on('style.load', onStyleLoad);
    map.on('error', (e) => {
      // Static hosting answers empty squares with 404. That just means no points there.
      if (e.sourceId === SOURCE_ID) {
        const msg = e.error?.message ?? '';
        // Empty squares come back as 404 (static host) or an HTML fallback page
        // (some dev/preview servers). Both just mean no points there. Panning
        // also cancels tiles that left the screen. None of these are failures.
        if (e.error?.status === 404 || e.error?.name === 'AbortError' || /abort|parse/i.test(msg)) return;
        // A real failure: the tile server is down or the URL is wrong.
        if (!tilesLoaded) dispatch('tiles', { ok: false });
        return;
      }
      if (!styleReady) dispatch('basemap', { ok: false });
    });
    map.on('sourcedata', (e) => {
      if (e.sourceId === SOURCE_ID && e.tile) {
        tilesLoaded = true;
        dispatch('tiles', { ok: true });
      }
    });
  });

  // diff:false makes style.load fire again. The default diff drops custom layers quietly.
  $: if (map && basemap !== appliedBasemap) {
    appliedBasemap = basemap;
    styleReady = false;
    popup?.remove();
    map.setStyle(basemaps[basemap], { diff: false });
  }

  onDestroy(() => {
    popup?.remove();
    map?.remove();
  });
</script>

<div class="map" bind:this={container}></div>

<style>
  .map {
    position: absolute;
    inset: 0;
  }
</style>
