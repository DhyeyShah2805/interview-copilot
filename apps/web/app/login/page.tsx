export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Sign in</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Auth implementation lands on Day 2.
          </p>
        </div>
        {/* Day 2: build the form, wire to POST /auth/login */}
      </div>
    </main>
  );
}
