'use client'

import { useState, useEffect, useCallback } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const BANNERS = [
  '/assets/banner 1.png',
  '/assets/banner 2.png',
  '/assets/banner 3.png',
]
const INTERVAL = 4500

export default function BannerCarousel() {
  const [current, setCurrent] = useState(0)
  const [paused, setPaused] = useState(false)

  const prev = useCallback(() =>
    setCurrent(c => (c - 1 + BANNERS.length) % BANNERS.length), [])

  const next = useCallback(() =>
    setCurrent(c => (c + 1) % BANNERS.length), [])

  useEffect(() => {
    if (paused) return
    const id = setInterval(next, INTERVAL)
    return () => clearInterval(id)
  }, [paused, next])

  return (
    <div
      className="relative w-full rounded-2xl shadow-lg overflow-hidden"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      {/* Imagen activa: determina la altura natural del contenedor */}
      {BANNERS.map((src, i) => (
        <img
          key={i}
          src={src}
          alt={`Banner ${i + 1}`}
          className="w-full block transition-opacity duration-700"
          style={{
            display:  'block',
            position: i === current ? 'relative' : 'absolute',
            top: 0, left: 0,
            width:   '100%',
            height:  i === current ? 'auto' : '100%',
            objectFit: 'cover',
            opacity: i === current ? 1 : 0,
          }}
        />
      ))}

      {/* Arrows */}
      <button onClick={prev} aria-label="Anterior"
        className="absolute left-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-white/70 hover:bg-white flex items-center justify-center shadow transition-colors backdrop-blur-sm">
        <ChevronLeft className="w-5 h-5 text-navy-800" />
      </button>
      <button onClick={next} aria-label="Siguiente"
        className="absolute right-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-white/70 hover:bg-white flex items-center justify-center shadow transition-colors backdrop-blur-sm">
        <ChevronRight className="w-5 h-5 text-navy-800" />
      </button>

      {/* Dots */}
      <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10 flex gap-2">
        {BANNERS.map((_, i) => (
          <button key={i} onClick={() => setCurrent(i)} aria-label={`Banner ${i + 1}`}
            className="transition-all duration-300 rounded-full"
            style={{
              width:           i === current ? 20 : 8,
              height:          8,
              backgroundColor: i === current ? '#0d9488' : 'rgba(255,255,255,0.6)',
            }}
          />
        ))}
      </div>
    </div>
  )
}
