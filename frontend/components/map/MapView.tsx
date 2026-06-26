'use client'

import { useEffect, useRef } from 'react'
import type { Obra, RiskLevel } from '@/types'

interface MapViewProps {
  obras: Obra[]
  selectedId: string | null
  onSelect: (id: string) => void
}

function riskHex(score: RiskLevel): string {
  if (score <= 2) return '#16a34a'
  if (score === 3) return '#ca8a04'
  return '#dc2626'
}

export default function MapView({ obras, selectedId, onSelect }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<import('leaflet').Map | null>(null)
  const markersRef = useRef<Map<string, import('leaflet').CircleMarker>>(new Map())

  useEffect(() => {
    if (!containerRef.current) return
    // Guard against Leaflet double-init in React Strict Mode
    if ((containerRef.current as HTMLDivElement & { _leaflet_id?: number })._leaflet_id) return
    if (mapRef.current) return

    let destroyed = false

    import('leaflet').then(L => {
      if (destroyed || !containerRef.current) return
      if ((containerRef.current as HTMLDivElement & { _leaflet_id?: number })._leaflet_id) return

      const map = L.map(containerRef.current, {
        center: [-9.19, -75.0152],
        zoom: 5,
        zoomControl: true,
      })

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 18,
      }).addTo(map)

      if (!destroyed) {
        mapRef.current = map
      } else {
        map.remove()
      }
    })

    return () => {
      destroyed = true
      mapRef.current?.remove()
      mapRef.current = null
      markersRef.current.clear()
    }
  }, [])

  useEffect(() => {
    if (!mapRef.current) return
    import('leaflet').then(L => {
      const map = mapRef.current!

      markersRef.current.forEach((marker, id) => {
        if (!obras.find(o => o.id === id)) {
          marker.remove()
          markersRef.current.delete(id)
        }
      })

      obras.forEach(obra => {
        const color = riskHex(obra.score)
        const isSelected = obra.id === selectedId

        if (markersRef.current.has(obra.id)) {
          markersRef.current.get(obra.id)!.setStyle({
            color: isSelected ? '#0f172a' : color,
            fillColor: color,
            weight: isSelected ? 3 : 1.5,
            radius: isSelected ? 14 : 10,
          })
          return
        }

        const marker = L.circleMarker([obra.lat, obra.lng], {
          radius: isSelected ? 14 : 10,
          fillColor: color,
          color: isSelected ? '#0f172a' : color,
          weight: isSelected ? 3 : 1.5,
          opacity: 1,
          fillOpacity: 0.85,
        })

        marker.bindTooltip(
          `<div style="font-size:12px;max-width:200px;font-family:system-ui">
            <strong>${obra.titulo}</strong><br/>
            <span style="color:${color}">Riesgo ${obra.score}/5</span> · ${obra.tipo}<br/>
            <em style="color:#6b7280">${obra.municipioNombre}</em>
          </div>`,
          { direction: 'top', offset: [0, -10] }
        )

        marker.on('click', () => onSelect(obra.id))
        marker.addTo(map)
        markersRef.current.set(obra.id, marker)
      })
    })
  }, [obras, selectedId, onSelect])

  return (
    <div
      ref={containerRef}
      className="w-full h-full rounded-xl overflow-hidden"
      style={{ minHeight: 480 }}
    />
  )
}
