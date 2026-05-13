export default function InterviewPage({ params }: { params: { id: string } }) {
  return (
    <main className="flex min-h-screen flex-col px-6 py-12 max-w-3xl mx-auto">
      <h1 className="text-2xl font-semibold">Interview session</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Session ID: <code className="text-xs">{params.id}</code>
      </p>
      <p className="mt-1 text-sm text-muted-foreground">
        Streaming chat UI lands on Day 6.
      </p>
      {/* Day 6: streaming chat, message list, input box, evaluation sidebar */}
    </main>
  );
}
