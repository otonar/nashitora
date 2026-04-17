import requests
import gradio as gr
import os
import requests
# 必要なAPI情報
ACCESS_TOKEN = "EAAdrMCbdr1YBO7v2DHH835r8nL1AhSEttMvd5zPoGrBEGvgjtuMLR4axpQ4nShF0wh8Nf4ctxwIpuedvoWAe2dhOVOpDRp41z1FhlGDciod5cJZCDrq52dEgUyx4eZCCAPUTxrBv08fjFOXO0jucr9TlPiaBb0NiYYN1X0cdFUgULuREIpEA6HLCm0fVgQi9wjYZCoA2f3JkmlDLfZAEJBGS2wkZD"
# USER_ID = "17841471021863236"  # 実際のInstagramユーザーID
GRAPH_API_URL = "https://graph.facebook.com/v21.0"
# USER_ID = requests.get(
#     f"{GRAPH_API_URL}/me/accounts?access_token={ACCESS_TOKEN}").json()["data"][0]["id"]


# print(f"USER_ID: {USER_ID}")


def get_instagram_user_id(access_token):
    """
    FacebookページにリンクされたInstagramビジネスアカウントのユーザーIDを取得
    """
    print("get_instagram_user_id: アクセストークンを使用してユーザーIDを取得しようとしています。")
    url = f"{GRAPH_API_URL}/me/accounts?access_token={access_token}"
    response = requests.get(url)
    print(f"get_instagram_user_id: accounts APIレスポンス: {response.status_code}")
    data = response.json()
    print(f"get_instagram_user_id: レスポンスデータ: {data}")
    if "data" in data:
        for page in data["data"]:
            page_id = page.get("id")
            print(f"get_instagram_user_id: ページID: {page_id}")
            instagram_url = f"{GRAPH_API_URL}/{page_id}?fields=instagram_business_account&access_token={access_token}"
            insta_response = requests.get(instagram_url)
            print(
                f"get_instagram_user_id: Instagram APIレスポンスステータス: {insta_response.status_code}")
            insta_data = insta_response.json()
            print(f"get_instagram_user_id: Instagramデータ: {insta_data}")
            if "instagram_business_account" in insta_data:
                instagram_id = insta_data["instagram_business_account"].get(
                    "id")
                print(
                    f"get_instagram_user_id: 取得したInstagramビジネスアカウントID: {instagram_id}")
                return instagram_id
    print("get_instagram_user_id: 有効なInstagramビジネスアカウントのユーザーIDが見つかりませんでした。")
    return None


USER_ID = get_instagram_user_id(ACCESS_TOKEN)
print(f"USER_ID: {USER_ID}")
if not USER_ID:
    raise ValueError("有効なInstagramビジネスアカウントのユーザーIDが取得できませんでした。")


def fetch_hashtag_posts(hashtag, type_of_posts="top"):
    """
    ハッシュタグに関連する投稿を取得
    type_of_posts: "top" -> 人気投稿, "recent" -> 最新投稿
    """
    # ハッシュタグから '#' を削除
    clean_hashtag = hashtag.lstrip('#')
    print(f"fetch_hashtag_posts: クリーンなハッシュタグ「{clean_hashtag}」を使用します。")

    print(
        f"fetch_hashtag_posts: ハッシュタグ「{clean_hashtag}」の{type_of_posts}投稿を取得します。")
    posts = []
    # ハッシュタグIDを取得
    search_url = f"{GRAPH_API_URL}/ig_hashtag_search?user_id={USER_ID}&q={clean_hashtag}&access_token={ACCESS_TOKEN}"
    print(f"fetch_hashtag_posts: ハッシュタグ検索URL: {search_url}")
    response = requests.get(search_url)
    print(
        f"fetch_hashtag_posts: ハッシュタグ検索APIレスポンスステータス: {response.status_code}")
    print(f"fetch_hashtag_posts: APIレスポンス: {response.json()}")

    hashtag_data = response.json()
    if "data" not in hashtag_data or not hashtag_data["data"]:
        print("fetch_hashtag_posts: ハッシュタグが見つかりませんでした。")
        return "Error: ハッシュタグが見つかりませんでした。"

    hashtag_id = hashtag_data["data"][0].get("id")
    print(f"fetch_hashtag_posts: 取得したハッシュタグID: {hashtag_id}")

    # 人気投稿 or 最新投稿を取得
    if type_of_posts == "top":
        posts_url = f"{GRAPH_API_URL}/{hashtag_id}/top_media?user_id={USER_ID}&fields=id,caption,media_type,media_url,timestamp&access_token={ACCESS_TOKEN}"
    else:
        posts_url = f"{GRAPH_API_URL}/{hashtag_id}/recent_media?user_id={USER_ID}&fields=id,caption,media_type,media_url,timestamp&access_token={ACCESS_TOKEN}"

    print(f"fetch_hashtag_posts: 投稿取得URL: {posts_url}")
    posts_response = requests.get(posts_url)
    print(
        f"fetch_hashtag_posts: 投稿取得APIレスポンスステータス: {posts_response.status_code}")
    posts_data = posts_response.json()
    print(f"fetch_hashtag_posts: 投稿データ: {posts_data}")

    if "data" not in posts_data or not posts_data["data"]:
        print("fetch_hashtag_posts: 投稿が見つかりませんでした。")
        return "Error: 投稿が見つかりませんでした。"

    # Gradioで表示するためのデータ整形
    posts = []
    for post in posts_data["data"]:
        print(f"fetch_hashtag_posts: 処理中の投稿ID: {post.get('id')}")
        media_type = post.get("media_type")
        media_url = post.get("media_url")
        caption = post.get('caption', 'キャプションなし')
        timestamp = post.get('timestamp')

        if media_type == "IMAGE":
            if media_url:
                posts.append(
                    (media_url, f"{caption} ({timestamp})"))
                print(f"fetch_hashtag_posts: 画像投稿を追加しました。URL: {media_url}")
            else:
                print(
                    f"fetch_hashtag_posts: 画像投稿に'media_url'がありません。投稿ID: {post.get('id')} をスキップします。")
        elif media_type == "VIDEO":
            if media_url:
                posts.append(
                    (media_url, f"Video: {caption} ({timestamp})"))
                print(f"fetch_hashtag_posts: 動画投稿を追加しました。URL: {media_url}")
            else:
                print(
                    f"fetch_hashtag_posts: 動画投稿に'media_url'がありません。投稿ID: {post.get('id')} をスキップします。")
        elif media_type == "CAROUSEL_ALBUM":
            # キャロセルアルバムの場合、各メディアアイテムを処理
            children = post.get('children', {}).get('data', [])
            for child in children:
                child_media_url = child.get('media_url')
                child_media_type = child.get('media_type')
                if child_media_type in ["IMAGE", "VIDEO"] and child_media_url:
                    prefix = "Video: " if child_media_type == "VIDEO" else ""
                    posts.append(
                        (child_media_url, f"{prefix}{caption} ({timestamp})"))
                    print(
                        f"fetch_hashtag_posts: キャロセルの投稿を追加しました。URL: {child_media_url}")
                else:
                    print(
                        f"fetch_hashtag_posts: キャロセルの投稿に'media_url'がありません。子投稿ID: {child.get('id')} をスキップします。")
        else:
            print(
                f"fetch_hashtag_posts: 未対応のmedia_type '{media_type}' の投稿ID: {post.get('id')} をスキップします。")

    print(f"fetch_hashtag_posts: 取得した総投稿数: {len(posts)}")
    return posts


def display_posts(hashtag, post_type):
    # ハッシュタグから '#' を削除
    clean_hashtag = hashtag.lstrip('#')
    print(
        f"display_posts: ユーザー入力ハッシュタグ「{hashtag}」からクリーンなハッシュタグ「{clean_hashtag}」を生成しました。")

    # 日本語の投稿タイプをAPIのパラメータにマッピング
    post_type_map = {
        "人気投稿": "top",
        "最新投稿": "recent"
    }
    api_post_type = post_type_map.get(post_type, "top")

    posts = fetch_hashtag_posts(clean_hashtag, api_post_type)
    if isinstance(posts, str):  # エラーメッセージの場合
        return posts

    # Gradioのギャラリーが画像URLを最初に受け取るように順序を変更
    formatted_posts = [[post[0], f"Caption: {post[1]}"] for post in posts]
    return formatted_posts


# Gradioインターフェース
interface = gr.Interface(
    fn=display_posts,
    inputs=[
        gr.Textbox(label="ハッシュタグ", placeholder="例: #nature"),
        gr.Radio(["人気投稿", "最新投稿"], label="投稿の種類")
    ],
    outputs="gallery",
    title="Instagram 投稿ビューワー",
    description="指定されたハッシュタグに関連する人気投稿または最新投稿を表示します。",
)

interface.launch()
