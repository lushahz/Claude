#!/usr/bin/env python3
"""Upload the merge drafts to angorabbits.com as NEW, separate drafts.

Safety: this only ever POSTs new items with status=draft. It never updates,
publishes, trashes or deletes an existing post/page. Live URLs are untouched.

Auth is injected by the session proxy, so no credentials live here.

  python3 push_drafts.py          # dry run: verify auth, show what would be created
  python3 push_drafts.py --go     # create the drafts
"""
import json, re, sys, urllib.request, pathlib

API = "https://angorabbits.com/wp-json/wp/v2"
HERE = pathlib.Path(__file__).parent

# file -> (endpoint matching the live URL being replaced, live ID it will eventually replace)
DRAFTS = {
    "german-angora-rabbit__MERGED.html":       ("posts", 943),
    "giant-angora-rabbits__MERGED.html":       ("pages", 115),
    "lifespan-of-angora-rabbits__MERGED.html": ("posts", 693),
    "breeds__MERGED.html":                     ("pages", 638),
    "wool-rabbit-breeds__LINKED.html":         ("posts", 856),
    "fluffy-rabbit-breeds__LINKED.html":       ("posts", 689),
}


def call(method, path, body=None):
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main():
    go = "--go" in sys.argv
    me = call("GET", "/users/me?context=edit")
    print(f"Authenticated as {me['name']} (id {me['id']}, roles {me.get('roles')})")
    created = {}
    for fname, (kind, live_id) in DRAFTS.items():
        html = (HERE / fname).read_text()
        title = re.match(r"<!-- TITLE: (.*?) -->", html).group(1)
        body = {
            "status": "draft",
            "title": f"[MERGE DRAFT] {title}",
            "content": re.sub(r"^<!-- TITLE: .*? -->\n", "", html),
        }
        print(f"{'CREATE' if go else 'would create'} {kind[:-1]} draft: {body['title']} (replaces live #{live_id})")
        if go:
            r = call("POST", f"/{kind}", body)
            assert r["status"] == "draft", r["status"]
            created[fname] = {"draft_id": r["id"], "live_id": live_id, "edit": f"https://angorabbits.com/wp-admin/post.php?post={r['id']}&action=edit"}
            print("   ->", created[fname]["edit"])
    if go:
        (HERE / "created_drafts.json").write_text(json.dumps(created, indent=2))


if __name__ == "__main__":
    main()
