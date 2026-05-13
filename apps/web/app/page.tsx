import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 py-24">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
          Interview Copilot
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Personalized mock interviews from your resume and target role. Practice,
          get scored, improve.
        </p>
        <div className="mt-8 flex gap-4 justify-center">
          <Link
            href="/login"
            className="rounded-md bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground"
          >
            Get started
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-border px-6 py-2.5 text-sm font-medium"
          >
            View on GitHub
          </a>
        </div>
        <p className="mt-12 text-xs text-muted-foreground">
          v0.1.0 — scaffolding stage. Real flows ship by May 28, 2026.
        </p>
      </div>
    </main>
  );
}
