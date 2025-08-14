import { render, screen } from "@testing-library/react";
import Home from "../app/page"; // adjust if path is different

describe("Home Page", () => {
  it("renders upload PDF heading", () => {
    render(<Home />);
    expect(screen.getByText(/Upload Your PDF/i)).toBeInTheDocument();
  });
});
