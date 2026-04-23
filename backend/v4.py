import asyncio
import os
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

STATE_FILE = "instagram_state.json"

def extract_media_from_node(node):
    """Devuelve lista de {'type': 'image'/'video', 'url': '...'} desde un nodo de la API interna."""
    media_list = []
    media_type = node.get("media_type")  # 1=imagen, 2=video, 8=carrusel

    # Imagen simple
    if media_type == 1:
        image_versions = node.get("image_versions2", {})
        candidates = image_versions.get("candidates", [])
        if candidates:
            url = candidates[0]["url"]  # mejor calidad
            media_list.append({"type": "image", "url": url})

    # Video simple
    elif media_type == 2:
        video_versions = node.get("video_versions", [])
        if video_versions:
            url = video_versions[0]["url"]
            media_list.append({"type": "video", "url": url})

    # Carrusel (álbum)
    elif media_type == 8:
        carousel_media = node.get("carousel_media", [])
        for media in carousel_media:
            # Cada elemento puede ser imagen o video
            if media.get("media_type") == 1:  # imagen
                img_versions = media.get("image_versions2", {})
                candidates = img_versions.get("candidates", [])
                if candidates:
                    media_list.append({"type": "image", "url": candidates[0]["url"]})
            elif media.get("media_type") == 2:  # video
                vid_versions = media.get("video_versions", [])
                if vid_versions:
                    media_list.append({"type": "video", "url": vid_versions[0]["url"]})
    return media_list

async def get_user_info_api(page, username):
    try:
        # Ejecutamos fetch dentro del navegador (aprovecha las cookies de la sesión)
        result = await page.evaluate(f"""
            async () => {{
                const url = 'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}';
                const resp = await fetch(url, {{
                    headers: {{
                        'User-Agent': navigator.userAgent,
                        'x-ig-app-id': '936619743392459',
                        'Accept': 'application/json'
                    }}
                }});
                if (!resp.ok) return null;
                return await resp.json();
            }}
        """)
        
        if not result:
            print("⚠️ No se pudo obtener info del usuario (respuesta vacía o error)")
            return {}
        
        user_data = result.get("data", {}).get("user", {})
        if not user_data:
            print("⚠️ Usuario no encontrado en la respuesta")
            return {}
        
        return {
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name"),
            "biography": user_data.get("biography"),
            "profile_pic": user_data.get("profile_pic_url_hd") or user_data.get("profile_pic_url"),
            "posts": user_data.get("edge_owner_to_timeline_media", {}).get("count", 0),
            "followers": user_data.get("edge_followed_by", {}).get("count", 0),
            "following": user_data.get("edge_follow", {}).get("count", 0),
            "is_private": user_data.get("is_private", False),
            "is_verified": user_data.get("is_verified", False),
            "external_url": user_data.get("external_url", "")
        }
    except Exception as e:
        print("⚠️ Error en API de usuario:", e)
        return {}


# =========================
# 💬 COMMENTS (API INTERNA)
# =========================
async def get_comments_graphql(page, shortcode, max_comments=20):
    url = "https://www.instagram.com/graphql/query"
    params = {
        "query_hash": "bc3296d1ce80a24b1b6e40b1e72903f5",  # hash para comentarios
        "variables": json.dumps({
            "shortcode": shortcode,
            "first": max_comments
        })
    }
    response = await page.request.get(url, params=params)
    data = await response.json()
    #print("#####################################################")
    #print(data.get("data", {}).get("shortcode_media", {}).get("edge_media_to_parent_comment", {}).get("edges", []))
    #print("#####################################################")

    return data.get("data", {}).get("shortcode_media", {}).get("edge_media_to_parent_comment", {}).get("edges", [])


# =========================
# 🚀 SCRAPER PRINCIPAL
# =========================
async def scrape_instagram(profile_name: str, max_posts=5):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
            storage_state=STATE_FILE if os.path.exists(STATE_FILE) else None
        )

        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        posts = []
        seen_posts = set()

        # =========================
        # 📡 GRAPHQL POSTS
        # =========================
        async def handle_response(response):
            if "graphql/query" not in response.url:
                return

            try:
                data = await response.json()
            except:
                return

            try:
                data_block = data.get("data")
                if not isinstance(data_block, dict):
                    return

                feed = data_block.get(
                    "xdt_api__v1__feed__user_timeline_graphql_connection"
                )

                if not isinstance(feed, dict):
                    return

                edges = feed.get("edges", [])
                if not edges:
                    return

                for edge in edges:
                    node = edge.get("node", {})
                    if not node:
                        continue

                    post_id = node.get("id")
                    if not post_id or post_id in seen_posts:
                        continue

                    #print("DEBUG node keys:", node.keys())

                    seen_posts.add(post_id)

                    media_list = extract_media_from_node(node)

                    posts.append({
                        "id": post_id,
                        "shortcode": node.get("code"),
                        "caption": (
                            node.get("caption", {}).get("text", "")
                            if isinstance(node.get("caption"), dict)
                            else ""
                        ),
                        "likes": node.get("like_count", 0),
                        "comments": [],
                        "media": media_list
                    })

            except Exception as e:
                print("⚠️ Post parse error:", e)

        page.on("response", handle_response)

        # =========================
        # 🔐 LOGIN
        # =========================
        if not os.path.exists(STATE_FILE):
            await page.goto("https://www.instagram.com/accounts/login/")
            print("👉 Login manual (60s)...")
            await page.wait_for_timeout(60000)
            await context.storage_state(path=STATE_FILE)

            # 👇 AÑADE ESTO
        

        # =========================
        # 🚀 PERFIL
        # =========================
        await page.goto(f"https://www.instagram.com/{profile_name}/")
        await page.wait_for_timeout(5000)

        user_info = await get_user_info_api(page, profile_name)
        #print("\n👤 USER INFO:")
        #print(user_info)

        # =========================
        # 🔽 SCROLL CONTROLADO
        # =========================
        scroll_attempts = 0
        MAX_SCROLLS = 10

        while len(posts) < max_posts and scroll_attempts < MAX_SCROLLS:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            scroll_attempts += 1

        posts = posts[:max_posts]

        print(f"✅ Posts capturados: {len(posts)}")

        # =========================
        # 💬 LINKS
        # =========================
        links = [
            f"https://www.instagram.com/p/{p['shortcode']}/"
            for p in posts if p.get("shortcode")
        ]

        print("\nLINKS:")
        print(links)

        # =========================
        # 💬 COMENTARIOS
        # =========================
        for i, post in enumerate(posts):

            media_id = post["id"]

            print(f"\n🔎 Post {i+1}")
            comments = await get_comments_graphql(page, post["shortcode"], max_comments=5)
            post["comments"] = comments
            print(f"   💬 {len(comments)} comentarios")

        await browser.close()

        return posts, user_info


# =========================
# 🚀 MAIN
# =========================
async def main(username: str):
    user = username

    data = await scrape_instagram(user, max_posts=2)

    #print("\n📦 RESULTADO FINAL:\n")
    #print(json.dumps(data[0], indent=2, ensure_ascii=False))

    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump(data[0], f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())