import { render, screen } from '@testing-library/react';
import Home from '../app/page';

describe('Home Page', () => {
  it('renders Market Pulse heading', () => {
    render(<Home />);
    // Matches "Market Pulse" or "Market-Pulse", even with text before it
    expect(screen.getByText(/Market[\s-]?Pulse/i)).toBeInTheDocument();
  });
});