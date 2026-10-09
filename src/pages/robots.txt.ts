import type { APIRoute } from 'astro';

const getRobotsTxt = (sitemapURL: URL) => `
# Hey, I'm not the one that has to worry about DDoS attacks. -AC

User-agent: *
Allow: /

Sitemap: ${sitemapURL.href}
`;

export const GET: APIRoute = ({ site }) => {
  const sitemapURL = new URL('sitemap-index.xml', site);
  return new Response(getRobotsTxt(sitemapURL));
};