import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Window } from "./Window";

afterEach(() => vi.useRealTimers());

describe("pipeline tour tabs", () => {
  it("exposes a tablist and moves selection with arrow keys", () => {
    render(<Window />);
    const ingest = screen.getByRole("tab", { name: "Ingest" });
    expect(ingest.parentElement).toHaveAttribute("role", "tablist");
    fireEvent.keyDown(ingest, { key: "ArrowRight" });
    expect(screen.getByRole("tab", { name: "Hash" })).toHaveAttribute("aria-selected", "true");
  });

  it("shows metadata-only details for the selected stage", () => {
    render(<Window />);
    fireEvent.click(screen.getByRole("tab", { name: "Features" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("tabular statistics");
    expect(screen.getByRole("tabpanel")).toHaveTextContent("No packet payload features");
  });

  it("holds auto-advance while hovered and resumes after leaving", () => {
    vi.useFakeTimers();
    const { container } = render(<Window />);
    const frame = container.firstElementChild;
    if (!frame) throw new Error("Tour frame is missing");
    fireEvent.mouseEnter(frame);
    act(() => vi.advanceTimersByTime(7000));
    expect(screen.getByRole("tab", { name: "Ingest" })).toHaveAttribute("aria-selected", "true");
    fireEvent.mouseLeave(frame);
    act(() => vi.advanceTimersByTime(7000));
    expect(screen.getByRole("tab", { name: "Hash" })).toHaveAttribute("aria-selected", "true");
  });
});
