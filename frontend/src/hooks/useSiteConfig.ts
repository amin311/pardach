import { useQuery } from '@tanstack/react-query';
import { api } from '../api';

interface SiteConfig {
  require_signup: boolean;
  blocks: Array<{
    id: string;
    title: string;
    type: string;
    config: Record<string, any>;
    order: number;
  }>;
}

export function useSiteConfig() {
  return useQuery<SiteConfig>({
    queryKey: ['site-config'],
    queryFn: () => api.get('/public/home').then(res => res.data),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
} 