import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'StoreForge AI - AI-Powered Shopify Store Builder',
  description: 'Build complete Shopify stores in minutes using AI. Generate product descriptions, enhance images, and create ready-to-launch stores from any product URL.',
  keywords: 'Shopify, AI, store builder, ecommerce, dropshipping, product descriptions, image enhancement',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}