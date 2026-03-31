export function Loader({ label = "Завантаження..." }: { label?: string }) {
  return (
    <div className="flex min-h-[30vh] flex-col items-center justify-center gap-3 text-slate-600">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-cyan-100 border-t-cyan-700" />
      <p className="text-sm font-medium">{label}</p>
    </div>
  );
}

