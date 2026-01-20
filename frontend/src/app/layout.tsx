import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CLI-Mate - AI Error Analysis',
  description: 'AI-Powered Error Knowledge Base',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className="bg-background text-foreground">{children}</body>
    </html>
  )
}
