# Lushah Digital Inc. — brand & website plan

Decisions agreed with Shahzad on 2026-09-28. This is the handoff for any session that makes live changes.

## Structure

| Site | Role |
|---|---|
| lushah.com | **Lushah Digital Inc.**: agency site. Lead offers: Shopify builds, WordPress builds, SEO. Everything else (branding, design, video, podcast, YouTube, social) is an add-on. |
| shahzadsadiq.com | Founder site for **future clients checking out the founder**, plus a personal blog with affiliate income. Sends hiring intent to lushah.com. |
| shihtzupedia.com, scaleblog.com, angorabbits.com | Lushah Digital Inc. publications. Footer: "© 2026 <Site>, a Lushah Digital Inc. publication", linked to lushah.com. |
| pawsometips.com | Built by Lushah and **sold**. Show as "built & sold" (check the sale terms allow it). |
| linkedin.com/in/lushahz | Personal profile. Create a separate Lushah Digital Inc. company page. |

## Facts and dates (use these consistently)

- The Lushah brand has operated since **2019**. Incorporated as **Lushah Digital Inc. in June 2026**. Toronto.
- Drop "210+ projects". Use real, provable numbers only.
- Founder: Shahzad Sadiq. Did jewelry design for about 20 years before web work (years still to be confirmed).
- Clients in six countries: Canada, USA, UK, Germany, Australia, Pakistan.

## Portfolio

**Lushah clients (can be featured on lushah.com)**

| Client | Country | Work | URL |
|---|---|---|---|
| SellEton Scales & Liberty Scales | USA | Shopify, SEO, product video; since 2020 (contract) | selletonscales.com, libertyscales.com |
| Sohhas International | Canada | WordPress catalog, 249+ dental products | sohhasinternational.com |
| R.A. Mirza CPA | Mississauga, ON | WordPress | ramirza.com |
| Sadiq Builders | Pakistan | WordPress | sadiqbuilders.org |
| Adjuster University | USA | Course video editing, since 2020 | adjuster-university.com |
| The Balanced Practice Inc. | Ottawa, ON | Podcast editing (The Balanced Dietitian Podcast) | thebalancedpractice.com |
| Blue Crane Capital | Sydney, Australia | Social media content, about 2–3 yrs (resume says 2019–2023; confirm) | bluecranecapital.com |
| Naomi Peris | Australia | YouTube video editing & channel management, 2019– | youtube.com/@NaomiPeris |
| GRUMA | Germany | About 12 videos edited | gruma.de |

**HueBlue partner work (outsourced to Shahzad by HueBlue, Lahore).** Don't present these as Lushah's own clients. Get HueBlue's written OK before naming them. Otherwise say "outsourced developer for HueBlue".
HueBlue (hueblue.com), HAWX Gear, Octane Moto Sport, Surgimax (UK), Millennia (Shopify, PK), plus more to come.

**Volunteer / community:** Al-Hidayah Camp (website, flyers, social media; Hamilton, ON). MQI Canada (flyers; website in progress).

**Own brands:** ShihTzuPedia, ScaleBlog, AngoRabbits. Built & sold: PawsomeTips.

## Compliance to-dos
- ScaleBlog: disclose the Liberty Scales / SellEton relationship next to the Liberty banner and on the About page.
- shahzadsadiq.com: affiliate disclosure page, plus a note on posts with affiliate links (e.g. the Hostinger banner).
- lushah.com: add Privacy Policy and Terms pages (none exist).

## Resume (shahzadsadiq.com), in order
1. Founder & CEO, Lushah Digital Inc.: 2019–present (incorporated 2026), Toronto
2. Ecommerce & Digital Manager (contract), SellEton Scales | Liberty Scales: 2020–present
3. WordPress Developer (outsourced), HueBlue: [year]–present
4. Video Editor, Adjuster University: 2020–present
5. Video Editor & YouTube Channel Manager, Naomi Peris (Australia): 2019–[?]
6. Social Media Content Creator, Blue Crane Capital (Sydney): [confirm dates]
7. Podcast Editor, The Balanced Practice Inc. (Ottawa): [dates]
8. Video Editor (freelance), GRUMA (Germany): [year]
9. Jewelry Designer: [years]
- Volunteer: Al-Hidayah Camp, MQI Canada
- Also: built & sold PawsomeTips; publisher of three content sites
- Education: MS & BS Business Administration, Virtual University of Pakistan (2016 / 2014); DigiSkills certificates (2019)

## lushah.com sitemap
Home · Services (Shopify / WordPress / SEO) · Work · Our Brands · About · Blog · Contact · Privacy · Terms
- The Home page copy is drafted in `lushah-home.md`.
- Blog: aimed at people ready to hire (e.g. costs, Shopify vs WooCommerce). No affiliate links.

## shahzadsadiq.com sitemap
Home · About · Resume · Blog · Work with me (links to lushah.com)
- Drop "digital maestro and creative genius". New headline: "Founder & CEO, Lushah Digital Inc."
- Blog categories: Tools I use (affiliate), Building in public, Founder lessons, Freelancing (the 3 existing posts).

## Technical notes (from the 2026-09-28 check)
- Hosting: Hostinger, account `u661793786` (lushah.com, shahzadsadiq.com, shihtzupedia.com, scaleblog.com, angorabbits.com, sadiqbuilders.org, al-hidayah.camp).
- **lushah.com**: Arolax theme + **Elementor** (plus Animation Addons for Elementor, AIOSEO, Omnisend). Page IDs: home 34, about 3304, services 3331, work 4307, blog 6236, contact 2474. Page content lives in Elementor's `_elementor_data` meta, which the REST API doesn't expose by default.
- **shahzadsadiq.com**: Leven theme (lmpixels framework = Unyson page builder). The frontend renders from the builder JSON in post meta (`fw_get_db_post_option($id,'page-builder')`), NOT from post_content, so editing post_content through REST has no visible effect. Builder pages need a helper that writes the builder option, or edits in wp-admin. Non-builder pages (e.g. Privacy Policy, id 3) can be edited through REST normally. Page IDs: about-me 157, resume 171, portfolio 25, blog 86, contact 187.
- Live edits need a WordPress Application Password per site, added in the environment settings as an API credential (as done for angorabbits.com).

## Still needed from Shahzad
- Case-study numbers for SellEton / Liberty (traffic, sales, rankings)
- Start year with HueBlue, jewelry design years, Blue Crane / Balanced Practice / Naomi Peris dates and counts
- 8–12 design, logo and animation samples; founder headshot
- Testimonials (ideally Rizwan Mirza, Sohhas, SellEton / Liberty)
- HueBlue's permission to name their clients

## Done log
- 2026-09-29 shahzadsadiq.com: tagline → "Founder & CEO, Lushah Digital Inc."; Privacy Policy (id 3) rewritten with an affiliate disclosure and published.
- Home (157) and Resume (171) text is prepared (see chat), not yet applied: it needs a builder-aware write.
