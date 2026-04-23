import asyncio
import os
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

STATE_FILE = "instagram_state.json"


async def scrape_instagram(profile_name: str, max_posts=10):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = None
        if os.path.exists(STATE_FILE):
            context = await browser.new_context(storage_state=STATE_FILE)
            print("📂 Sesión cargada")
        else:
            context = await browser.new_context()

        page = await context.new_page()

        stealth = Stealth()
        await stealth.apply_stealth_async(page)

        posts_data = []
        comments_buffer = {}
        seen_ids = set()

        # =========================
        # 📡 INTERCEPTOR GRAPHQL
        # =========================
        async def handle_response(response):
            if "graphql/query" not in response.url:
                return

            try:
                data = await response.json()
            except:
                return

            if not data or "data" not in data:
                return

            # =========================
            # 📌 POSTS (nuevo formato IG)
            # =========================
            try:
                media = data["data"].get("xdt_api__v1__feed__user_timeline_graphql_connection")

                if media:
                    edges = media.get("edges", [])

                    for edge in edges:
                        node = edge.get("node", {})

                        post_id = node.get("id")
                        if not post_id or post_id in seen_ids:
                            continue

                        seen_ids.add(post_id)

                        post = {
                            "id": post_id,
                            "shortcode": node.get("code") or node.get("shortcode"),
                            "caption": "",
                            "likes": node.get("like_count", 0),
                            "comments": []
                        }

                        # caption
                        caption = node.get("caption")
                        if isinstance(caption, dict):
                            post["caption"] = caption.get("text", "")

                        posts_data.append(post)

            except:
                pass

            # =========================
            # 💬 COMENTARIOS (preview)
            # =========================
            try:
                comments = data["data"].get("xdt_api__v1__media__comments__connection")

                if comments:
                    edges = comments.get("edges", [])

                    temp = []
                    for c in edges[:3]:
                        node = c.get("node", {})
                        text = node.get("text")
                        if text:
                            temp.append(text)

                    if temp:
                        comments_buffer["last"] = temp

            except:
                pass

        page.on("response", handle_response)

        # =========================
        # 🔐 LOGIN
        # =========================
        if not os.path.exists(STATE_FILE):
            await page.goto("https://www.instagram.com/accounts/login/")
            print("👉 Inicia sesión manualmente...")

            await page.wait_for_url(lambda url: "login" not in url, timeout=120000)

            await context.storage_state(path=STATE_FILE)
            print("💾 Sesión guardada")

        # =========================
        # 🚀 PERFIL
        # =========================
        await page.goto(f"https://www.instagram.com/{profile_name}/")
        await asyncio.sleep(5)

        # =========================
        # 🔽 SCROLL CONTROLADO
        # =========================
        scroll_attempts = 0
        MAX_SCROLLS = 10

        while len(posts_data) < max_posts and scroll_attempts < MAX_SCROLLS:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            scroll_attempts += 1

        posts_data = posts_data[:max_posts]

        print(f"✅ Posts capturados: {len(posts_data)}")

        # =========================
        # 🔗 LINKS POSTS
        # =========================
        links = await page.eval_on_selector_all(
            'article a[href*="/p/"]',
            'els => els.map(e => e.href)'
        )

        links = list(dict.fromkeys(links))[:max_posts]

        # =========================
        # 💬 ABRIR POSTS
        # =========================
        for i, link in enumerate(links):
            print(f"🔎 Post {i+1}")

            await page.goto(link)
            await asyncio.sleep(4)

            if "last" in comments_buffer and i < len(posts_data):
                posts_data[i]["comments"] = comments_buffer["last"]

        await browser.close()

        return posts_data


# =========================
# 🚀 MAIN
# =========================
async def main():
    user = input("Usuario: ")

    data = await scrape_instagram(user, max_posts=10)

    print("\n📦 RESULTADO FINAL:\n")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n💾 Guardado en resultado.json")


if __name__ == "__main__":
    asyncio.run(main())