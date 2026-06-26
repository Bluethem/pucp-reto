import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const pdfUrl = request.nextUrl.searchParams.get('url')
  if (!pdfUrl) return new NextResponse('Missing url', { status: 400 })

  try {
    const upstream = await fetch(pdfUrl, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
    })
    if (!upstream.ok) {
      return new NextResponse(`Upstream error ${upstream.status}`, { status: 502 })
    }

    const buffer = await upstream.arrayBuffer()

    return new NextResponse(buffer, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline',
        'Cache-Control': 'public, max-age=3600',
      },
    })
  } catch {
    return new NextResponse('Failed to fetch PDF', { status: 502 })
  }
}
