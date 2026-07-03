import { useEffect, useState } from "react";

/** A brief, self-dismissing confirmation — fires on New Session / Forget All. */
export default function Toast({ toast }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!toast) return;
    setVisible(true);
    const t = setTimeout(() => setVisible(false), 2400);
    return () => clearTimeout(t);
  }, [toast]);

  if (!toast) return null;
  return (
    <div className={`toast${visible ? " show" : ""}`} key={toast.id}>
      {toast.msg}
    </div>
  );
}
