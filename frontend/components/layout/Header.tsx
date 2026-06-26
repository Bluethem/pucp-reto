'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useState } from 'react'
import { Search, Menu, X } from 'lucide-react'

const NAV_LINKS = [
  { label: 'Mapa de obras', href: '/' },
  { label: 'Empresas', href: '/empresa' },
  { label: 'Municipios', href: '/municipio' },
  { label: 'Acerca', href: '/acerca' },
]

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [search, setSearch] = useState('')

  return (
    <header className="sticky top-0 z-50">
      <div className="bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-0 h-[68px] flex items-center gap-8">

          {/* Logo — overflow allowed so the zoomed image fills the space */}
          <Link href="/" className="shrink-0 overflow-hidden flex items-center justify-start" style={{ width: 90, height: 68 }}>
            <Image
              src="/assets/glass.png"
              alt="glass"
              width={170}
              height={170}
              style={{ width: 170, height: 'auto', transform: 'scale(1.35)', transformOrigin: 'center' }}
              priority
            />
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-0.5 ml-2">
            {NAV_LINKS.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className="px-3.5 py-2 text-[13px] font-medium text-gray-500 hover:text-navy-800 hover:bg-gray-50 rounded-lg transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Search */}
          <div className="hidden md:flex items-center flex-1 max-w-xs ml-auto relative">
            <Search className="absolute left-3.5 w-3.5 h-3.5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar obra, empresa, municipio..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-[13px] font-light border border-gray-200 rounded-full bg-gray-50 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent placeholder:text-gray-400"
            />
          </div>

          {/* Mobile toggle */}
          <button
            className="md:hidden ml-auto p-2 rounded-lg text-gray-400 hover:bg-gray-100 transition-colors"
            onClick={() => setMobileOpen(v => !v)}
            aria-label="Menu"
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile nav */}
        {mobileOpen && (
          <div className="md:hidden border-t border-gray-100 bg-white px-5 py-4 space-y-1">
            <div className="relative mb-4">
              <Search className="absolute left-3.5 top-2.5 w-3.5 h-3.5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar..."
                className="w-full pl-9 pr-4 py-2 text-sm font-light border border-gray-200 rounded-full bg-gray-50 focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
            {NAV_LINKS.map(link => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="block px-3 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 rounded-lg"
              >
                {link.label}
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Accent line */}
      <div className="h-[3px] bg-gradient-to-r from-navy-800 via-teal-500 to-teal-400" />
    </header>
  )
}
