import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import SessionProvider from '@/contexts/SessionProvider'
import { ChatProvider } from '@/contexts/ChatContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'WebQA',
  description: 'A web based Q&A platform admission consultation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang='en'>
      <body className={inter.className}>
        <ChatProvider>
          <SessionProvider>{children}</SessionProvider>
        </ChatProvider>
      </body>
    </html>
  )
}
