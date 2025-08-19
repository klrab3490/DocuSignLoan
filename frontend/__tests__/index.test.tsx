import { render, screen } from "@testing-library/react";
import Home from "../app/page"; // adjust the path if different

describe("Home Page", () => {
  it("renders main heading", () => {
    render(<Home />);
    expect(screen.getByText(/Document Processing Hub/i)).toBeInTheDocument();
  });

  it("renders upload tab trigger", () => {
    render(<Home />);
    expect(screen.getByText(/Upload Document/i)).toBeInTheDocument();
  });

  it("renders fetch tab trigger", () => {
    render(<Home />);
    // match "Fetch Data" or "Retrieve Data"
    expect(
      screen.getByText(/(Fetch Data|Retrieve Data)/i)
    ).toBeInTheDocument();
  });
});
