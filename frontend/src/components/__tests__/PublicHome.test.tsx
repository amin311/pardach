import { render, screen } from '@testing-library/react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../../stores/auth';
import PublicHome from '../PublicHome';
import { LandingLockScreen } from '../LandingLockScreen';

// Mock hooks
jest.mock('@tanstack/react-query');
jest.mock('../../stores/auth');
jest.mock('../LandingLockScreen');

describe('PublicHome', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useQuery as jest.Mock).mockReturnValue({
      data: {
        require_signup: false,
        blocks: [
          {
            id: '1',
            title: 'Catalog',
            type: 'catalog_link',
            config: {},
            order: 1
          }
        ]
      },
      isLoading: false
    });
  });

  it('renders CatalogHero when require_signup is false', () => {
    (useAuthStore as jest.Mock).mockReturnValue({ user: null });
    render(<PublicHome />);
    expect(screen.getByTestId('catalog-hero')).toBeInTheDocument();
  });

  it('renders LandingLockScreen when require_signup is true and user is null', () => {
    (useQuery as jest.Mock).mockReturnValue({
      data: {
        require_signup: true,
        blocks: []
      },
      isLoading: false
    });
    (useAuthStore as jest.Mock).mockReturnValue({ user: null });
    render(<PublicHome />);
    expect(LandingLockScreen).toHaveBeenCalled();
  });
}); 