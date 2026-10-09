# INVENTORY: Ultro occurrences for the text-and-links pass

Nothing in this file was edited in pass 1. Format: `file:line | kind | exact value | location`, one row per occurrence.
Edits made in pass 1 (logo alt/title/aria-label set to "GEMINII", brand files, Arvo, palette) are not listed.
Rows for CSS selectors and variables that still carry an Ultro identifier are listed because a rename must follow them
(`src/styles/global.css` holds the palette override rules added in pass 1; they use the original names).

Kinds with no occurrence in the site: analytics-id, manifest-name, legal-page (no pages; README copyright line is listed as text).

Counts: canonical-or-og-url 1, email 1, form-endpoint 2, json-ld 3, link 14, meta-description 6, sitemap-or-robots-entry 5, social-handle 7, ultro-name-in-attribute 3, ultro-name-in-identifier 32, ultro-name-in-text 21; total 95.

```text
.github/workflows/deploy.yml:49 | ultro-name-in-identifier | ~/ultro.browning.edu/public | deploy workflow
README.md:1 | ultro-name-in-text | # Ultro Robotics Website | README
README.md:3 | link | /public/old/ | README link
README.md:3 | link | /src/pages/old/ | README link
README.md:3 | link | https://ultro.browning.edu/old | README
README.md:3 | ultro-name-in-text | This repository houses the in-development redesigned website for Ultro Robotics! Our legacy codebase is preserved character-for-character but is divided into two places: CSS and assets [here](/public/old/) and HTML [here](/src/pages/old/). This makes it publicly accessible at <https://ultro.browning.edu/old>. | README
README.md:13 | ultro-name-in-text | │   │   └── { old Ultro website assets } | README
README.md:24 | ultro-name-in-text | │   │   │   └── { old Ultro website HTML } | README
README.md:40 | ultro-name-in-text | Copyright © Ultro Robotics | README
astro.config.ts:13 | canonical-or-og-url | https://ultro.browning.edu | Astro `site`, base of canonical, sitemap and JSON-LD URLs
astro.config.ts:25 | sitemap-or-robots-entry | sitemap(), | sitemap integration
src/assets/ultro_dark.svg:1 | ultro-name-in-identifier | ultro_dark.svg | file name (logo file, unreferenced after the logo swap)
src/assets/ultro_small_dark.svg:1 | ultro-name-in-identifier | ultro_small_dark.svg | file name (logo file, unreferenced after the logo swap)
src/assets/ultro_small_dark.svg:11 | ultro-name-in-identifier | ultro_small_dark_v2.svg | src/assets/ultro_small_dark.svg
src/assets/ultroblack.png:1 | ultro-name-in-identifier | ultroblack.png | file name (logo file, unreferenced after the logo swap)
src/assets/ultrosmall.png:1 | ultro-name-in-identifier | ultrosmall.png | file name (logo file, unreferenced after the logo swap)
src/components/Button.astro:15 | ultro-name-in-identifier | bg-ultro-red-600 | button component
src/components/Button.astro:15 | ultro-name-in-identifier | border-ultro-red-600 | button component
src/components/Button.astro:15 | ultro-name-in-identifier | shadow-ultro-red-600/25 | button component
src/components/Footer.astro:12 | link | / | site footer
src/components/Footer.astro:19 | social-handle | https://youtube.com/@UltroRobotics | site footer
src/components/Footer.astro:28 | social-handle | https://www.instagram.com/ultro_robotics10539/ | site footer
src/components/Footer.astro:37 | social-handle | https://github.com/BrowningUltro-10539 | site footer
src/components/Footer.astro:46 | email | mailto:ultro@browning.edu | site footer
src/components/Footer.astro:58 | link | https://browning.edu | site footer
src/components/Footer.astro:66 | ultro-name-in-text | Ultro Robotics is the Browning School's premier FTC robotics team. | site footer
src/components/Footer.astro:70 | link | https://github.com/BrowningUltro-10539/ultro.browning.edu | site footer
src/components/Link.astro:10 | ultro-name-in-identifier | hover:text-ultro-red-800 | inline link component
src/components/Link.astro:10 | ultro-name-in-identifier | text-ultro-red-500 | inline link component
src/components/NavigationBar.astro:23 | link | /about/ | header navigation
src/components/NavigationBar.astro:24 | link | /robots/ | header navigation
src/components/NavigationBar.astro:28 | link | /outreach/ | header navigation
src/components/NavigationBar.astro:29 | link | /resources/ | header navigation
src/components/NavigationBar.astro:57 | link | / | header navigation
src/components/NavigationBar.astro:57 | ultro-name-in-attribute | aria-label="Ultro logo" | header navigation
src/components/Socials.astro:18 | social-handle | https://youtube.com/@UltroRobotics | floating social links
src/components/Socials.astro:27 | social-handle | https://www.instagram.com/ultro_robotics10539/ | floating social links
src/components/Socials.astro:36 | social-handle | https://github.com/BrowningUltro-10539 | floating social links
src/layouts/MainLayout.astro:15 | ultro-name-in-text | <BaseLayout title={title + " | Ultro Robotics"} description={description}> | page title template
src/pages/about.astro:23 | ultro-name-in-text | headline: "Ultro Robotics", | about page (/about/)
src/pages/about.astro:25 | ultro-name-in-text | "Browning Robotics gets renamed to Ultro - a testament to our student-driven, autonomous designs.", | about page (/about/)
src/pages/about.astro:31 | ultro-name-in-text | "Ultro makes it to NYC Championships for the first time in our sophomore season, Velocity Vortex.", | about page (/about/)
src/pages/about.astro:37 | ultro-name-in-text | "Ultro makes it through NYC Championships undefeated, winning Inspire 2<sup>nd</sup> and the Control Award. The FTC World Championship was unfortunately cancelled due to COVID-19.", | about page (/about/)
src/pages/about.astro:43 | link | /ex-nihilo/ | about page (/about/)
src/pages/about.astro:43 | ultro-name-in-identifier | hover:text-ultro-red-800 | about page (/about/)
src/pages/about.astro:43 | ultro-name-in-identifier | text-ultro-red-500 | about page (/about/)
src/pages/about.astro:43 | ultro-name-in-text | "To commemorate our 10-year anniversary, Ultro unveils a refreshed website and identity, and launches community team <a href=\"/ex-nihilo/\" class=\"text-ultro-red-500 hover:text-ultro-red-800 transition-colors underline\">Ex Nihilo.</a>", | about page (/about/)
src/pages/about.astro:48 | meta-description | We began as Browning Robotics in 2015 when our founders won a robotics competition at Johns Hopkins. Learn more about Ultro Robotics, our history, and our sponsors. | about page (/about/), title
src/pages/about.astro:50 | ultro-name-in-text | Ultro began as Browning Robotics in 2015 when the founders, Robert, Ben, | about page (/about/)
src/pages/about.astro:71 | ultro-name-in-text | <strong>Ultro is entirely self-funded.</strong> Our finances are | about page (/about/)
src/pages/ex-nihilo.astro:15 | meta-description | Ex Nihilo is our brand-new, open community FIRST Tech Challenge robotics team hosted at Browning's 64th St campus. Join us! | ex nihilo page (/ex-nihilo/)
src/pages/ex-nihilo.astro:40 | form-endpoint | https://docs.google.com/forms/d/e/1FAIpQLScDP07p6hY8JLLDER6yYc0aYAKBmeJmnxOW10It-Iu0EI2hZQ/viewform?usp=dialog | ex nihilo page (/ex-nihilo/)
src/pages/ex-nihilo.astro:44 | ultro-name-in-identifier | from-ultro-red-900 | ex nihilo page (/ex-nihilo/)
src/pages/ex-nihilo.astro:44 | ultro-name-in-identifier | to-ultro-red-950 | ex nihilo page (/ex-nihilo/)
src/pages/ex-nihilo.astro:52 | ultro-name-in-text | Ex Nihilo is an open community robotics team being launched by Ultro | ex nihilo page (/ex-nihilo/)
src/pages/ex-nihilo.astro:56 | ultro-name-in-text | mentorship of Ultro. | ex nihilo page (/ex-nihilo/)
src/pages/ex-nihilo.astro:97 | form-endpoint | https://docs.google.com/forms/d/e/1FAIpQLScDP07p6hY8JLLDER6yYc0aYAKBmeJmnxOW10It-Iu0EI2hZQ/viewform?usp=dialog | ex nihilo page (/ex-nihilo/)
src/pages/index.astro:14 | json-ld | name: "Ultro Robotics 10539" | JSON-LD WebSite block on the home page
src/pages/index.astro:15 | json-ld | alternateName: ["Ultro Robotics", "Ultro 10539", "Ultro"] | JSON-LD WebSite block on the home page
src/pages/index.astro:16 | json-ld | url: Astro.site | JSON-LD WebSite block on the home page
src/pages/index.astro:21 | ultro-name-in-attribute | title="Ultro Robotics | FTC Team 10539" | home page (/), title
src/pages/index.astro:23 | meta-description | Ultro Robotics is The Browning School's premier FIRST Tech Challenge robotics team. We are a student-led team that aims to engineer for humanity. | home page (/)
src/pages/index.astro:28 | ultro-name-in-identifier | to-ultro-red-950 | home page (/)
src/pages/index.astro:36 | ultro-name-in-identifier | from-ultro-red-900 | home page (/)
src/pages/index.astro:36 | ultro-name-in-identifier | to-ultro-red-950 | home page (/)
src/pages/index.astro:43 | ultro-name-in-text | What is Ultro? | home page (/)
src/pages/index.astro:46 | ultro-name-in-text | Team Ultro (meaning "of its own mind") is a <strong | home page (/)
src/pages/index.astro:49 | link | https://browning.edu | home page (/)
src/pages/index.astro:60 | link | /about/ | home page (/)
src/pages/outreach.astro:12 | meta-description | From mentorship to collaboration with the community, Ultro Robotics is committed to more than just building robots. | outreach page (/outreach/), title
src/pages/outreach.astro:14 | ultro-name-in-text | Ultro is committed to more than just building robots. Our holistic | outreach page (/outreach/)
src/pages/outreach.astro:46 | ultro-name-in-text | For the 2024-25 season, Ultro team members mentored the | outreach page (/outreach/)
src/pages/outreach.astro:51 | ultro-name-in-attribute | title="Ultro Robotics YouTube" | outreach page (/outreach/), card title
src/pages/outreach.astro:56 | social-handle | https://www.youtube.com/@UltroRobotics | outreach page (/outreach/)
src/pages/outreach.astro:63 | ultro-name-in-text | Our ENGINEERING FOR HUMANITY speaker series connects Ultro | outreach page (/outreach/)
src/pages/resources.astro:9 | meta-description | Get resources from a veteran FTC team to help you build your robot. | resources page (/resources/), title
src/pages/robots.astro:9 | meta-description | Explore our robots from past seasons of FTC. | robots page (/robots/), title
src/pages/robots.txt.ts:4 | sitemap-or-robots-entry | # Hey, I'm not the one that has to worry about DDoS attacks. -AC | robots.txt template
src/pages/robots.txt.ts:6 | sitemap-or-robots-entry | User-agent: * | robots.txt template
src/pages/robots.txt.ts:7 | sitemap-or-robots-entry | Allow: / | robots.txt template
src/pages/robots.txt.ts:9 | sitemap-or-robots-entry | Sitemap: ${sitemapURL.href} | robots.txt template
src/styles/global.css:37 | ultro-name-in-identifier | --color-ultro | global stylesheet
src/styles/global.css:37 | ultro-name-in-identifier | --color-ultro-red-600 | global stylesheet
src/styles/global.css:38 | ultro-name-in-identifier | --color-ultro-red-50 | global stylesheet
src/styles/global.css:39 | ultro-name-in-identifier | --color-ultro-red-100 | global stylesheet
src/styles/global.css:40 | ultro-name-in-identifier | --color-ultro-red-200 | global stylesheet
src/styles/global.css:41 | ultro-name-in-identifier | --color-ultro-red-300 | global stylesheet
src/styles/global.css:42 | ultro-name-in-identifier | --color-ultro-red-400 | global stylesheet
src/styles/global.css:43 | ultro-name-in-identifier | --color-ultro-red-500 | global stylesheet
src/styles/global.css:44 | ultro-name-in-identifier | --color-ultro-red-600 | global stylesheet
src/styles/global.css:45 | ultro-name-in-identifier | --color-ultro-red-700 | global stylesheet
src/styles/global.css:46 | ultro-name-in-identifier | --color-ultro-red-800 | global stylesheet
src/styles/global.css:47 | ultro-name-in-identifier | --color-ultro-red-900 | global stylesheet
src/styles/global.css:48 | ultro-name-in-identifier | --color-ultro-red-950 | global stylesheet
src/styles/global.css:159 | ultro-name-in-identifier | .shadow-ultro-red-600\/25 | global stylesheet
```
