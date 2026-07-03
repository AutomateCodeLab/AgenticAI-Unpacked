// Shows which persisted facts were retrieved and injected for one turn —
// makes semantic recall visible instead of invisible.
export default function MemoryChips({ items }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="memory-chips">
      {items.map((text, i) => (
        <span className="memory-chip" key={i} title={text}>
          🧩 {text}
        </span>
      ))}
    </div>
  );
}
