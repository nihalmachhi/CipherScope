import { useEffect, useRef, useState } from "react";

export function useInView(threshold = 0.25, once = false) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (typeof IntersectionObserver === "undefined") {
      setInView(true);
      return;
    }
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) setInView(true);
      else if (!once) setInView(false);
      if (once && entry.isIntersecting) observer.disconnect();
    }, { threshold });
    observer.observe(node);
    return () => observer.disconnect();
  }, [threshold, once]);
  return { ref, inView };
}
