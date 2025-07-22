import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-storage')
  const isAuthPage = request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/register'
  const isMainPage = request.nextUrl.pathname === '/'
  const isQuotesPage = request.nextUrl.pathname === '/quotes' || request.nextUrl.pathname === '/quotes/'

  // Allow access to main page without authentication
  if (isMainPage) {
    return NextResponse.next()
  }

  // Redirect to login if not authenticated and trying to access protected routes
  if (!token && (isQuotesPage || request.nextUrl.pathname.startsWith('/quotes/'))) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Redirect to main page if authenticated and trying to access auth pages
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/quotes', '/quotes/:path*', '/login', '/register', '/'],
} 