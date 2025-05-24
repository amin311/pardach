import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../stores/auth';
import { api } from '../api';
import { HomeSkeleton } from './HomeSkeleton';
import { LandingLockScreen } from './LandingLockScreen';
import { Footer } from './Footer';

function BlockRenderer({ block }: { block: any }) {
  switch (block.type) {
    case "catalog_link":
      return <CatalogHero key={block.id} {...block.config} />;
    case "order_form":
      return <OrderFormEmbed key={block.id} />;
    case "business_grid":
      return <BusinessGrid key={block.id} />;
    case "profile_short":
      return <ProfileShortcut key={block.id} />;
    default:
      return null;
  }
}

export default function PublicHome() {
  const { data, isLoading } = useQuery(['home-config'], () => 
    api.get('/public/home').then(res => res.data)
  );
  const { user } = useAuthStore();

  if (isLoading) return <HomeSkeleton />;

  if (data.require_signup && !user) {
    return <LandingLockScreen />;
  }

  return (
    <div className="container mx-auto px-4">
      {data.blocks.map(block => (
        <BlockRenderer key={block.id} block={block} />
      ))}
      <Footer />
    </div>
  );
} 