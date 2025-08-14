import { render, screen } from '@testing-library/react';
import Home from '../app/page';

describe('Home Page', () => {
  it('renders starter text', () => {
    render(<Home />);
    expect(
      screen.getByText(/Get started by editing/i)
    ).toBeInTheDocument();
  });
});
