'use client'

import { useState, useEffect } from 'react'
import { ComposableMap, Geographies, Geography } from 'react-simple-maps'

const DEPT_URL = '/assets/peru_dept.geojson'
const PROV_URL = '/assets/peru_prov.geojson'
const DIST_URL = '/assets/peru_dist.geojson'

type Level = 'department' | 'province' | 'district'

function toTitle(s: string = ''): string {
  return s.toLowerCase().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

// Compute center + scale from a GeoJSON feature geometry
function bboxConfig(geo: GeoFeature): { center: [number, number]; scale: number } {
  try {
    let coords: number[][] = []
    const g = geo.geometry
    if (g.type === 'Polygon') {
      coords = g.coordinates[0] as number[][]
    } else if (g.type === 'MultiPolygon') {
      for (const poly of g.coordinates as number[][][][]) coords.push(...poly[0])
    }
    if (!coords.length) throw new Error('empty')

    const lngs = coords.map(c => c[0])
    const lats  = coords.map(c => c[1])
    const minLng = Math.min(...lngs), maxLng = Math.max(...lngs)
    const minLat = Math.min(...lats),  maxLat = Math.max(...lats)
    const span   = Math.max(maxLng - minLng, maxLat - minLat)
    // scale ~ 480 px / span_rad
    const scale  = Math.round(Math.min(90000, Math.max(2000, 480 / (span * Math.PI / 180))))
    return {
      center: [(minLng + maxLng) / 2, (minLat + maxLat) / 2],
      scale,
    }
  } catch {
    return { center: [-75.5, -9.5], scale: 1750 }
  }
}

interface GeoFeature {
  rsmKey: string
  properties: Record<string, string>
  geometry: {
    type: string
    coordinates: unknown
  }
}

interface Props {
  onSelectRegion: (region: string) => void
}

export default function PeruMap({ onSelectRegion }: Props) {
  const [level, setLevel]               = useState<Level>('department')
  const [selectedDept, setSelectedDept] = useState('')
  const [selectedProv, setSelectedProv] = useState('')
  const [geoData, setGeoData]           = useState<object | null>(null)
  const [loading, setLoading]           = useState(true)
  const [error, setError]               = useState(false)
  // Stack of projections — push when drilling in, pop when going back
  const [projStack, setProjStack] = useState<Array<{ center: [number, number]; scale: number }>>([
    { center: [-75.5, -9.5], scale: 1750 },
  ])
  const projCfg = projStack[projStack.length - 1]
  const [tooltip, setTooltip] = useState<{ name: string; x: number; y: number } | null>(null)

  const geoUrl =
    level === 'department' ? DEPT_URL :
    level === 'province'   ? PROV_URL :
                             DIST_URL

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(false)
    setGeoData(null)
    fetch(geoUrl)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then(data => { if (!cancelled) { setGeoData(data); setLoading(false) } })
      .catch(() => { if (!cancelled) { setError(true); setLoading(false) } })
    return () => { cancelled = true }
  }, [geoUrl])

  function shouldShow(p: Record<string, string>): boolean {
    if (level === 'department') return true
    if (level === 'province')
      return (p.FIRST_NOMB ?? '').toUpperCase().trim() === selectedDept
    return (
      (p.NOMBDEP  ?? '').toUpperCase().trim() === selectedDept &&
      (p.NOMBPROV ?? '').toUpperCase().trim() === selectedProv
    )
  }

  function getLabel(p: Record<string, string>): string {
    if (level === 'department') return toTitle(p.NOMBDEP)
    if (level === 'province')   return toTitle(p.NOMBPROV)
    return toTitle(p.NOMBDIST)
  }

  function handleClick(geo: GeoFeature) {
    const p = geo.properties
    if (level === 'department') {
      const dept = (p.NOMBDEP ?? '').toUpperCase().trim()
      setSelectedDept(dept)
      setLevel('province')
      setProjStack(s => [...s, bboxConfig(geo)])
      onSelectRegion(toTitle(p.NOMBDEP))
    } else if (level === 'province') {
      const prov = (p.NOMBPROV ?? '').toUpperCase().trim()
      setSelectedProv(prov)
      setLevel('district')
      setProjStack(s => [...s, bboxConfig(geo)])
    }
    // district: no further drill
  }

  function goBack() {
    setTooltip(null)
    // Pop the current projection to restore the previous one
    setProjStack(s => s.length > 1 ? s.slice(0, -1) : s)
    if (level === 'district') {
      setLevel('province')
      setSelectedProv('')
    } else {
      setLevel('department')
      setSelectedDept('')
      onSelectRegion('')
    }
  }

  const breadcrumb = [
    level !== 'department' ? toTitle(selectedDept) : null,
    level === 'district'   ? toTitle(selectedProv) : null,
  ].filter(Boolean).join(' › ')

  return (
    <div className="relative w-full h-full bg-white" onMouseLeave={() => setTooltip(null)}>

      {level !== 'department' && (
        <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
          <button
            onClick={goBack}
            className="text-[11px] font-semibold bg-white border border-gray-200 rounded-lg px-3 py-1.5 text-navy-800 hover:bg-gray-50 shadow-sm transition-colors"
          >
            ← Volver
          </button>
          {breadcrumb && (
            <span className="text-[11px] font-semibold text-navy-800 bg-white/90 px-2.5 py-1 rounded-lg shadow-sm border border-gray-100">
              {breadcrumb}
            </span>
          )}
        </div>
      )}

      <div className="absolute bottom-3 right-3 z-10 text-[10px] font-light text-gray-400">
        {level === 'department' && 'Clic para ver provincias'}
        {level === 'province'   && 'Clic para ver distritos'}
        {level === 'district'   && 'Distritos'}
      </div>

      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 z-20 text-sm font-light text-gray-400">
          Cargando…
        </div>
      )}
      {error && !loading && (
        <div className="absolute inset-0 flex items-center justify-center text-sm font-light text-red-400">
          Error cargando el mapa
        </div>
      )}

      {geoData && (
        <ComposableMap
          projection="geoMercator"
          projectionConfig={projCfg}
          style={{ width: '100%', height: '100%' }}
        >
          <Geographies geography={geoData}>
            {({ geographies }) =>
              geographies
                .filter(geo => shouldShow(geo.properties as Record<string, string>))
                .map(geo => {
                  const p     = geo.properties as Record<string, string>
                  const label = getLabel(p)
                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      onClick={() => handleClick(geo as unknown as GeoFeature)}
                      onMouseEnter={(e: React.MouseEvent) =>
                        setTooltip({ name: label, x: e.clientX, y: e.clientY })
                      }
                      onMouseMove={(e: React.MouseEvent) =>
                        setTooltip({ name: label, x: e.clientX, y: e.clientY })
                      }
                      onMouseLeave={() => setTooltip(null)}
                      style={{
                        default: {
                          fill: '#bfdbfe',
                          stroke: '#ffffff',
                          strokeWidth: level === 'district' ? 0.2 : 0.6,
                          outline: 'none',
                          cursor: 'pointer',
                        },
                        hover: {
                          fill: '#1d4ed8',
                          stroke: '#ffffff',
                          strokeWidth: level === 'district' ? 0.3 : 0.9,
                          outline: 'none',
                          cursor: 'pointer',
                        },
                        pressed: {
                          fill: '#1e3a8a',
                          stroke: '#ffffff',
                          strokeWidth: 0.9,
                          outline: 'none',
                        },
                      }}
                    />
                  )
                })
            }
          </Geographies>
        </ComposableMap>
      )}

      {tooltip && (
        <div
          className="fixed z-[9999] text-white text-[11px] font-semibold px-3 py-1.5 rounded-lg shadow-xl pointer-events-none whitespace-nowrap"
          style={{ left: tooltip.x + 14, top: tooltip.y - 38, background: '#1b2547' }}
        >
          {tooltip.name}
        </div>
      )}
    </div>
  )
}
