import React from "react";

export const ErrorState = ({ message, onRetry }) => (
  <div className="mx-auto max-w-md rounded-2xl border border-red-500/20 bg-red-500/5 p-6 text-center">
    <p className="text-red-300">{message}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="mt-4 rounded-lg bg-white/10 px-4 py-2 text-sm font-medium hover:bg-white/20"
      >
        Réessayer
      </button>
    )}
  </div>
);

export const CardSkeleton = ({ count = 8 }) => (
  <>
    {Array.from({ length: count }, (_, i) => (
      <div key={i} className="animate-pulse overflow-hidden rounded-2xl bg-slate-900">
        <div className="aspect-[3/4] bg-slate-800" />
        <div className="space-y-2 p-4">
          <div className="h-4 w-3/4 rounded bg-slate-800" />
          <div className="h-3 w-1/2 rounded bg-slate-800" />
        </div>
      </div>
    ))}
  </>
);
