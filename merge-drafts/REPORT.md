# angorabbits.com recovery: merges, redirects, generic-post plan

Status as of 2026-09-28. Nothing on the live site has been changed.

## 1. Credential check: FAILED

`GET /wp-json/wp/v2/users/me` returns **401 `rest_not_logged_in`**. The session proxy reports
`X-Proxy-Error: upstream auth failed: connection "Wordpress Angorarabbits"`, so the credential is
being sent but WordPress rejects it. Likely causes, most likely first:

1. The Application Password for user **Friend** was revoked or regenerated, or the user's
   password or role changed. To fix: in WP Admin, go to Users → Friend → Application Passwords,
   create a new one, then update the connector.
2. Hostinger or a security plugin is blocking REST Basic Auth or stripping the `Authorization`
   header on LiteSpeed. To fix: allowlist REST authentication in that plugin, or add
   `SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1` to `.htaccess`.

Because of this, **no drafts were created in WordPress.** The merged content was built from the
public REST API and is ready in this folder. After the credential is fixed, run
`python3 push_drafts.py` (dry run), then `python3 push_drafts.py --go`. The script only creates
**new** items with `status=draft`, titled `[MERGE DRAFT] …`. It never edits, publishes or deletes
existing content.

## 2. Merged drafts (in this folder)

| Draft file | Replaces (keep URL) | Merged in | Words (before → after) |
|---|---|---|---|
| `german-angora-rabbit__MERGED.html` | `/german-angora-rabbit/` (post 943) | `/german-angora-rabbits/` (page 1608) | 3,584 → 4,090 |
| `giant-angora-rabbits__MERGED.html` | `/giant-angora-rabbits/` (page 115) | `/huge-angora-rabbit/` (post 1031), `/how-big-do-angora-rabbits-get/` (post 908) | 1,968 → 3,478 |
| `lifespan-of-angora-rabbits__MERGED.html` | `/lifespan-of-angora-rabbits/` (post 693) | `/english-angora-rabbit-lifespan/` (post 864) | 2,936 → 3,935 |
| `breeds__MERGED.html` | `/breeds/` (page 638) | `/types-of-angora-rabbits/` (post 883) | 984 → 2,248 |
| `wool-rabbit-breeds__LINKED.html` | `/wool-rabbit-breeds/` (post 856) | (kept separate; link to `/breeds/` added) | |
| `fluffy-rabbit-breeds__LINKED.html` | `/fluffy-rabbit-breeds/` (post 689) | (kept separate; link to `/breeds/` added) | |

**What each merge does**

- **German.** Keeps the post's structure, which matches IAGARB (see §3). From the page it adds only
  what the post lacked: everyday health checks (6–8 hour no-eating rule, hocks, dental schedule),
  a "What German Angora Fiber Is Worth" section that links to the price page, a temperament
  paragraph, and three FAQs (colors, lifespan, fiber value). It does **not** bring in the page's
  wrong claims (see §3).
- **Giant.** The keep page gets the stronger sourced history from `/huge-angora-rabbit/`
  (Louise Walsh, 1988), the three-component coat section, the buck/doe minimums and the 6-class
  show format. From the size guide it gets a new **"How Big Do Giant Angora Rabbits Get?"**
  section (anchor `#how-big`) with the all-breed weight table, the coat-size illusion and the
  growth timeline. The FAQs now cover size, full-grown age, Angora weight in general and
  enclosure size, so the size queries still have an answer on this page.
- **Lifespan.** Adds an **"English Angora Rabbit Lifespan: 7 to 10 Years"** section (anchor
  `#english-angora-lifespan`): why the coat matters, why the smallest breed doesn't live longest,
  and a longevity checklist. Adds two English FAQs and fixes the page's contradictory German
  lifespan (the FAQ said 7–10 while the table said 7–11).
- **Breeds.** Adds history, a side-by-side comparison table, care across all breeds, how to find a
  breeder, a "More Breed Guides" block (wool, fluffy, Lionhead mix, dwarf, colors) and 7 FAQs.
  Links to `/wool-rabbit-breeds/` and `/fluffy-rabbit-breeds/` from the intro.
- **Every draft:** links to merged URLs are repointed; the broken `/satin-angora-rabbits/` link
  now goes to `/satin-angora-rabbit/`; empty image `alt` text is filled in.

**Editor notes before publishing**
- The content is block-editor HTML. It will open as blocks or a Classic block, so use "Convert to
  blocks" if needed.
- **FAQ sections will show correctly but won't output FAQ schema** until you rebuild them as Rank
  Math FAQ blocks. The keep pages use Rank Math FAQ, so paste the Q&As into the existing block.
- When approved, copy the draft content **into the existing live post/page** (same ID, same URL),
  then trash the `[MERGE DRAFT]` item. Don't publish the draft as a new URL.

## 3. Fact corrections (the competing pages contradicted each other)

Checked against IAGARB's published breed standard and registration rules (iagarb.com):

| Claim | Old page(s) | Correct / used in drafts |
|---|---|---|
| IAGARB registration minimum | 1,000 g (`/german-angora-rabbits/`, `/breeds/`) | **1,300 g/yr** (a 325 g 90-day clip × 4) and ≥80 points |
| German Angora face | "clean face, no facial wool" (page) | **Furnished on head, ears and feet** (IAGARB standard) |
| German grooming between shearings | "2–3 sessions/week" (page) | **Generally none needed** if the conditions are met (IAGARB "Grooming the German") |
| German colors | "white only; colored = hybrids, not registrable" (page) | **Colored animals may be exhibited if not bi-colored**; IAGARB publishes a color guide |
| German weight | 5.5–11.5 lb (page) | **5.5–12 lb** (2.5–5.5 kg standard) |
| German yield | 24–48 / 32–48 / 32–70+ oz | **32–70+ oz; registered lines ≥45 oz** |
| Giant yield | 32–80 oz (keep page, `/breeds/`) | **28–40 oz typical**, exceptional higher. This keeps "German out-produces Giant" true sitewide |
| Giant minimum weight | 9.5 lb (keep page) | **Bucks 9.5 lb, does 10 lb**, no maximum |
| English / French / Satin yield | 10–16, 16–20, 10–16 (types, huge, German post) | **12–16 / 12–16 / 6–12 oz**, matching the breed profile pages |
| Lifespan | Giant/German shown as 7–12 in breed pages | **Giant 7–10, German 7–11**, matching the lifespan page |

**Please verify (I could not confirm these):**
- **Giant Angora colors.** `/huge-angora-rabbit/` says ARBA accepted **Chestnut** in 2023; the
  keep page says REW only. The draft says "REW has long been standard; Chestnut reported accepted
  in 2023; check the current Standard of Perfection." Tighten this once confirmed.
- **Fiber prices** ($8–12/oz raw, $11–16/oz washed/carded). These come from the old page and are
  not sourced.
- I softened the papaya-enzyme advice in the lifespan FAQ ("evidence is limited"). The same claim
  still appears as a recommendation on other pages; worth a sitewide review since it's pet-health
  advice.

## 4. Proposed 301 redirects (apply only after the merged content is live)

| From | To | Note |
|---|---|---|
| `/german-angora-rabbits/` | `/german-angora-rabbit/` | |
| `/huge-angora-rabbit/` | `/giant-angora-rabbits/` | |
| `/how-big-do-angora-rabbits-get/` | `/giant-angora-rabbits/` | Per your plan. Alternative: `/breeds/`, since "how big do angora rabbits get" covers all breeds; the Giant draft covers all breeds to compensate |
| `/english-angora-rabbit-lifespan/` | `/lifespan-of-angora-rabbits/` | |
| `/types-of-angora-rabbits/` | `/breeds/` | |
| **`/satin-angora-rabbits/`** | **`/satin-angora-rabbit/`** | **Existing bug:** it currently 301s to the **homepage**, and 5 pages link to it |

Set these up in Rank Math → Redirections (the site already uses Rank Math). After redirecting, move
the source posts/page to Draft or Trash; that part needs your approval.

**Internal links to repoint** (so they don't rely on redirects):
- `/types-of-angora-rabbits/` is linked from **19** pages: home, about, faq, resources, contact,
  breeds, german-angora-rabbit, huge-angora-rabbit, dwarf-angora-rabbit, raising-angora-rabbits,
  how-big-do-angora-rabbits-get, wool-rabbit-breeds, short-haired-bunnies, fluffy-rabbit-breeds,
  angora-lionhead-rabbit, lifespan-of-angora-rabbits, blue-eyed-white-bunny,
  angora-rabbits-for-wool, angora-rabbit-care. Also check the menu and footer.
- `/huge-angora-rabbit/` ← how-big-do-angora-rabbits-get, wool-rabbit-breeds
- `/how-big-do-angora-rabbits-get/` ← faq
- `/english-angora-rabbit-lifespan/` ← angora-rabbit-eyes (a top page, so point this link to
  `/lifespan-of-angora-rabbits/#english-angora-lifespan`)
- `/satin-angora-rabbits/` ← how-big-do-angora-rabbits-get, wool-rabbit-breeds,
  types-of-angora-rabbits, glossary, breeds

The merged drafts and the two `__LINKED` files already carry the corrected links. The remaining
live pages need a find-and-replace once auth works; I can do that as drafts too.

**Rollout order:** (1) you approve the drafts → (2) copy them into the live IDs → (3) add the 301s
in the same session → (4) repoint internal links → (5) unpublish the sources → (6) resubmit the
sitemap and inspect the 4 keep URLs in Search Console. Then give it 4–8 weeks before judging.

## 5. Plan for the generic "can rabbits eat / are rabbits" posts

**Pattern:** there are 16 generic posts. Six of them, plus the two "why do rabbits…" posts, were
published **2026-04-18 to 04-22**, after the July 2025 drop. The pages that recovered are
Angora-specific (Lionhead mix, eyes, ears, German price, colors). Generic "can rabbits eat X"
queries are dominated by large pet sites, and a batch of off-topic posts dilutes the site's
Angora focus. That focus is exactly what core and helpful-content evaluation reward.

**Decision rule (needs 16 months of Search Console data per URL, which I don't have access to):**
keep a post as-is only if it has **≥ ~50 clicks in the last 12 months or ranks in the top 20** for
its main query. Otherwise apply the default action below.

| Group | Posts | Default action |
|---|---|---|
| **Angora-relevant: keep and rewrite around Angoras** | `are-rabbits-hypoallergenic` (Angora wool and allergies), `can-rabbits-swim` (wet Angora coat, hypothermia and felting; already Angora-heavy) | Retitle and angle, e.g. "Are Angora Rabbits Hypoallergenic?" and "Can Angora Rabbits Swim? Why Getting Wet Is Dangerous". Keep the URLs. Link from `/angora-rabbit-care/` |
| **Vision: consolidate** | `are-rabbits-blind` → `can-rabbits-see-in-the-dark` | Merge into one vision post, 301 the other, and link to `/angora-rabbit-eyes/`. Do **not** merge into the eyes page, which is a top performer |
| **Behavior: fold into the existing Angora post** | `why-do-rabbits-binky`, `why-do-rabbits-flop`, `are-rabbits-friendly` | Add as sections to `/angora-rabbit-behavior/`, then 301 |
| **Pet suitability: consolidate** | `are-rabbits-good-pets` | Rewrite as "Are Angora Rabbits Good Pets?" (a real Angora query), keep the URL or 301 into `/angora-rabbit-care/` |
| **Diet: one hub** | `can-rabbits-eat-apples`, `-carrots`, `-cauliflower`, `-cucumber`, `-grapes`, plus `are-rabbits-omnivores` | Build one "Fruits, Vegetables and Treats for Angora Rabbits" guide (the Angora angle is wool-growth protein needs and wool-block-safe diets), with a section per food, and 301 each post into it |
| **Taxonomy trivia: retire** | `are-rabbits-mammals`, `are-rabbits-farm-animals` | Noindex, or 410 if there's no traffic. `farm-animals` could instead fold into `/raising-angora-rabbits/` as "Angoras as fiber livestock" |

**Going forward:** pause new generic posts. Put the effort into Angora-specific depth next to what
already ranks: German Angora price, colors by breed, eyes and ears problems, Lionhead-mix care, and
wool harvesting how-tos. Add real photos, and author and breeder experience, to the top pages.

Once the credential works, the next steps are: create the six drafts, then the diet hub and
behavior merges as drafts.
