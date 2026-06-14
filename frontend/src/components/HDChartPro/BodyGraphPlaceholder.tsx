export default function BodyGraphPlaceholder() {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[400px] rounded-lg border border-dashed border-gray-300 bg-gray-50">
      {/* Decorative glyph */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-24 h-24 text-gray-300 mb-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1}
      >
        <circle cx="12" cy="5" r="2" />
        <circle cx="12" cy="12" r="2" />
        <circle cx="12" cy="19" r="2" />
        <circle cx="6" cy="8.5" r="2" />
        <circle cx="18" cy="8.5" r="2" />
        <circle cx="6" cy="15.5" r="2" />
        <circle cx="18" cy="15.5" r="2" />
        <line x1="12" y1="7" x2="12" y2="10" />
        <line x1="12" y1="14" x2="12" y2="17" />
        <line x1="7.5" y1="9.8" x2="10.5" y2="11" />
        <line x1="13.5" y1="11" x2="16.5" y2="9.8" />
      </svg>

      <p className="text-gray-400 font-semibold text-sm uppercase tracking-widest">
        BodyGraph SVG
      </p>
      <p className="text-gray-400 text-xs mt-1">
        Placeholder — connect your SVG renderer here
      </p>
    </div>
  );
}
