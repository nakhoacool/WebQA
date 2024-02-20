import { withAuth, NextRequestWithAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'
export default withAuth(
  // `withAuth` augments your `Request` with the user's token.
  function middleware(request: NextRequestWithAuth) {
    if (
      request.nextUrl.pathname.startsWith('/admin') &&
      request.nextauth.token?.role !== 'admin'
    ) {
      return NextResponse.rewrite(new URL('/unauthorized', request.url))
    }
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
)

export const config = { matcher: ['/admin'] }
