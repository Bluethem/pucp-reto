import type { Metadata } from 'next'
import { Poppins } from 'next/font/google'
import './globals.css'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-poppins',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'glass — Transparencia en Obras Públicas',
  description:
    'Sistema de detección de sobreprecios y transparencia en obras públicas del Estado Peruano. Datos de INFOBRAS, SEACE, INEI y JNE.',
  icons: { icon: '/assets/icono cuadrado.png' },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es" className={poppins.variable}>
      <body className="min-h-screen flex flex-col bg-gray-50 font-sans antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
