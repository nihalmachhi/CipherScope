import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QuickStart } from "./QuickStart";

describe("quick-start shell tabs", () => {
  it("switches command examples between PowerShell and Bash", () => {
    render(<QuickStart />);
    fireEvent.click(screen.getByRole("tab", { name: "Bash" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("export CIPHERSCOPE_HASH_SALT");
    fireEvent.click(screen.getByRole("tab", { name: "PowerShell" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("$env:CIPHERSCOPE_HASH_SALT");
  });
});
