import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Interview Copilot',
  description: 'AI-powered interview preparation, personalized to your resume.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
