#!/usr/bin/env python3
"""Create the frens.earth pack-01 products in a Printful store via the v1 API.

v2 plan (2026-09-15, the Admiral's law): bitcoin logo FRONT · the type on the BACK ·
the brand on the SLEEVE. A tee/hoodie product carries three files; caps/beanies one
embroidery file; totes/stickers one print file.

Reads the token from ~/.config/pacsarcade/printful.env — PRINTFUL_KEY_<STORE>=<token>,
or Lumen's account-level PRINTFUL_KEY_LUMEN + PRINTFUL_STORE_ID_<STORE> (never from
argv, never echoed). Creating sync products orders nothing and charges nothing.

Usage:
  create-products.py --whoami  [--store frens]      # which stores the token sees
  create-products.py --list    [--store frens]      # products in that store
  create-products.py --dry-run [--only 'Tick Tock'] # print the payloads, no writes
  create-products.py           [--only 'Tick Tock'] # create products
Printful fetches files by URL: plan.json file_base_url must be public (GitHub raw).
"""
import json, math, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
ENV = os.path.expanduser("~/.config/pacsarcade/printful.env")
ENV_LEGACY = os.path.expanduser("~/.config/pacsarcade/printful-lumen.env")
API = "https://api.printful.com"
DEFAULT_STORE = "frens"
THREAD_WHITE, THREAD_ORANGE = "#FFFFFF", "#E25C27"


def read_env_file(path):
    env = {}
    try:
        for ln in open(path):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def load_env(store):
    env = {**read_env_file(ENV_LEGACY), **read_env_file(ENV)}
    key = env.get(f"PRINTFUL_KEY_{store.upper()}") or (env.get("PRINTFUL_API_KEY") if store == DEFAULT_STORE else None)
    if not key and env.get("PRINTFUL_KEY_LUMEN") and env.get(f"PRINTFUL_STORE_ID_{store.upper()}"):
        key = env["PRINTFUL_KEY_LUMEN"]
    if not key:
        have = sorted(k for k in env if k.startswith("PRINTFUL_KEY_"))
        sys.exit(f"no token for store '{store}' — add PRINTFUL_KEY_{store.upper()}=... to {ENV} (have: {', '.join(have) or 'none'})")
    out = {"PRINTFUL_API_KEY": key}
    sid = env.get(f"PRINTFUL_STORE_ID_{store.upper()}") or env.get("PRINTFUL_STORE_ID")
    if sid:
        out["PRINTFUL_STORE_ID"] = sid
    return out


def call(env, method, path, body=None):
    hdr = {"Authorization": "Bearer " + env["PRINTFUL_API_KEY"], "Content-Type": "application/json"}
    if env.get("PRINTFUL_STORE_ID"):
        hdr["X-PF-Store-Id"] = env["PRINTFUL_STORE_ID"]
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers=hdr)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")
        raise SystemExit(f"{method} {path} -> HTTP {e.code}: {txt[:700]}")


def catalog(pid):
    return json.load(open(f"{HERE}/catalog-{pid}.json"))["result"]


def pick_variants(spec):
    vs = catalog(spec["product_id"])["variants"]
    if spec.get("sizes"):
        return [v for v in vs if v["size"] in spec["sizes"]]
    return [v for v in vs if v["color"] in spec["colors"]]


def price_for(v, retail):
    if retail:
        return f"{float(retail):.2f}"
    return f"{math.ceil(float(v['price']) * 2):.2f}"  # PLACEHOLDER rule, 2× cost


def file_url(plan, rel):
    return plan["file_base_url"].rstrip("/") + "/" + rel.lstrip("/")


def files_for(plan, item):
    kind = item["kind"]
    spec = plan["eco_catalog"][kind]
    if kind in ("tee", "hoodie"):
        base = plan["tee_files"] if kind == "tee" else plan["hoodie_files"]
        return [
            {"type": "front", "url": file_url(plan, base["front"])},
            {"type": "back", "url": file_url(plan, item["back"])},
            {"type": "sleeve_left", "url": file_url(plan, base["sleeve_left"])},
        ]
    f = {"type": spec.get("placement", "default"), "url": file_url(plan, item["file"])}
    if spec.get("embroidery"):
        f["options"] = [{"id": "embroidery_type", "value": "flat"},
                        {"id": spec.get("thread_option", "thread_colors"), "value": [THREAD_WHITE, THREAD_ORANGE]}]
    return [f]


def build_payload(plan, item):
    spec = plan["eco_catalog"][item["kind"]]
    variants = pick_variants(spec)
    if not variants:
        raise SystemExit(f"no variants for {item}")
    files = files_for(plan, item)
    placeholder = item.get("retail_price") in (None, "", 0)
    thumb = next((f["url"] for f in files if f["type"] == "back"), files[0]["url"])
    sync_variants = [{"variant_id": v["id"], "retail_price": price_for(v, item.get("retail_price")), "files": files} for v in variants]
    return {"sync_product": {"name": item["title"], "thumbnail": thumb}, "sync_variants": sync_variants}, placeholder


def main(argv):
    plan = json.load(open(f"{HERE}/plan.json"))
    only = argv[argv.index("--only") + 1].lower() if "--only" in argv else None
    store = argv[argv.index("--store") + 1] if "--store" in argv else DEFAULT_STORE
    env = load_env(store)
    print(f"store token: {store}")

    if "--whoami" in argv:
        print(json.dumps(call(env, "GET", "/stores")["result"], indent=2)); return
    if "--list" in argv:
        for p in call(env, "GET", "/store/products?limit=100")["result"]:
            print(p["id"], "|", p["name"], "| variants", p.get("variants"), "| synced", p.get("synced"))
        return
    if plan["file_base_url"].startswith("SET-ME"):
        sys.exit("plan.json file_base_url is not set")

    dry = "--dry-run" in argv
    made = []
    for item in plan["products"]:
        if only and only not in item["title"].lower():
            continue
        payload, placeholder = build_payload(plan, item)
        tag = " [PLACEHOLDER PRICE 2× cost]" if placeholder else ""
        v0 = payload["sync_variants"][0]
        print(f"→ {item['title']}{tag}: {len(payload['sync_variants'])} variants @ {v0['retail_price']} | files: " + ", ".join(f"{f['type']}={f['url'].rsplit('/',1)[-1]}" for f in v0["files"]))
        if dry:
            continue
        res = call(env, "POST", "/store/products", payload)["result"]
        made.append({"id": res["id"], "title": item["title"], "store": store})
        print("   created sync product", res["id"])
        time.sleep(1.5)
    if made:
        json.dump(made, open(f"{HERE}/created-{int(time.time())}.json", "w"), indent=2)
        print(f"\n{len(made)} products created in the {store} store — verify with --list, then set real prices.")


if __name__ == "__main__":
    main(sys.argv[1:])
