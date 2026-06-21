import { cn } from "@/lib/utils";

export function Panel({ className, children }: { className?: string; children: React.ReactNode }) {
  return <section className={cn("border border-slate-700/70 bg-card/95 shadow-glow", className)}>{children}</section>;
}

export function PanelHeader({ title, action }: { title: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-700/70 px-4 py-3">
      <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">{title}</h2>
      {action}
    </div>
  );
}
