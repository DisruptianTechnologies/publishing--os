import type { Metadata, Viewport } from 'next';
import { ClerkProvider } from '@clerk/nextjs';
import './globals.css';

export const metadata: Metadata = {
  title: { default: 'Kindlepreneur 2.0 — Publishing OS', template: '%s | Kindlepreneur 2.0' },
  description: 'The intelligent publishing command center for modern authors. Research, write, edit, publish, and grow with AI-powered agents.',
  keywords: ['kindle publishing', 'KDP', 'book writing AI', 'self publishing', 'Amazon KDP'],
  openGraph: {
    title: 'Kindlepreneur 2.0 — Publishing OS',
    description: 'AI-powered publishing platform from idea to bestseller.',
    type: 'website',
  },
};

export const viewport: Viewport = {
  themeColor: '#020617',
  colorScheme: 'dark',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || 'pk_test_Y2xlcmsua2luZGxlcHJlbmV1ci5kZXYk';

  return (
    <ClerkProvider publishableKey={publishableKey}>
      <html lang="en" className="dark">
        <body className="min-h-screen antialiased">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
