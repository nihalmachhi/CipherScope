import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Faq } from "./Faq";

describe("FAQ", () => {
  it("uses native disclosures and explains the payload boundary", () => {
    render(<Faq />);
    const question = screen.getByText("Does CipherScope decrypt traffic?");
    expect(question.closest("details")).not.toHaveAttribute("open");
    fireEvent.click(question);
    expect(question.closest("details")).toHaveAttribute("open");
    expect(screen.getByText(/Payload bytes are not inspected or stored/)).toBeInTheDocument();
  });
});
