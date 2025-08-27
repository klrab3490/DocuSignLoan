import { render, screen } from "@testing-library/react";
import Home from "../app/page"; // adjust path if needed

describe("Home Page", () => {
  beforeEach(() => {
    render(<Home />);
  });

  it("renders main heading", () => {
    // h1 -> "PDF Document Processor"
    expect(
      screen.getByRole("heading", { name: /PDF Document Processor/i })
    ).toBeInTheDocument();
  });

  it("renders upload tab trigger", () => {
    expect(
      screen.getByRole("tab", { name: /Upload Document/i })
    ).toBeInTheDocument();
  });

  it("renders retrieve tab trigger", () => {
    expect(
      screen.getByRole("tab", { name: /Retrieve Data/i })
    ).toBeInTheDocument();
  });
});
