# House of Spells Marketplace - Storefront

Modern Next.js storefront for the House of Spells marketplace, built with TypeScript, Tailwind CSS, and Apollo Client.

## Features

- 🚀 Next.js 16 with App Router
- 📱 Fully responsive design
- 🔍 SEO optimized with next-seo and next-sitemap
- 🎨 Tailwind CSS for styling
- 🔌 Apollo Client for GraphQL
- 🛒 Multi-seller marketplace support
- 🏪 B2B/B2C seller differentiation
- 📦 Product approval status display
- 🎯 TypeScript for type safety

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```bash
cp .env.local.example .env.local
```

3. Update `.env.local` with your Saleor API URL:
```
NEXT_PUBLIC_SALEOR_API_URL=https://hos-saleor-production.up.railway.app/graphql/
NEXT_PUBLIC_SITE_URL=https://hos-marketplaceweb-production.up.railway.app
NEXT_PUBLIC_SITE_NAME=House of Spells Marketplace
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
hos-storefront/
├── app/                    # Next.js App Router
│   ├── (shop)/            # Shop routes
│   ├── (account)/         # Account routes
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Homepage
├── components/            # React components
│   ├── common/           # Shared components
│   ├── product/          # Product components
│   ├── seller/           # Seller components
│   ├── cart/            # Cart components
│   └── layout/          # Layout components
├── lib/                  # Utilities
│   ├── apollo-client.ts  # GraphQL client
│   ├── graphql/          # GraphQL queries/mutations
│   └── utils.ts          # Helper functions
├── types/                # TypeScript types
└── public/               # Static assets
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production (includes sitemap generation)
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

See `.env.local.example` for required environment variables.

## GraphQL API

The storefront connects to the Saleor GraphQL API. Make sure your `NEXT_PUBLIC_SALEOR_API_URL` is correctly configured.

## SEO

- Dynamic meta tags using next-seo
- Automatic sitemap generation with next-sitemap
- JSON-LD structured data (to be implemented)
- Open Graph and Twitter Card support

## Deployment

The project is ready for deployment on Railway, Vercel, or any Node.js hosting platform.

For Railway:
1. Connect your GitHub repository
2. Set environment variables
3. Deploy!

## Next Steps

- [ ] Implement product detail pages
- [ ] Add shopping cart functionality
- [ ] Create checkout flow
- [ ] Add seller storefront pages
- [ ] Implement search functionality
- [ ] Add user authentication
- [ ] Create account pages
