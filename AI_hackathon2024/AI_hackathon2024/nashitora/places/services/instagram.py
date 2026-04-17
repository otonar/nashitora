# places/services/instagram.py
import requests
from django.conf import settings

FB_GRAPH_API_BASE = "https://graph.facebook.com"


def get_instagram_media():
    user_access_token = settings.INSTAGRAM_ACCESS_TOKEN
    if not user_access_token:
        raise ValueError(
            "INSTAGRAM_ACCESS_TOKEN.pyで定義してください。")

    # 1. ユーザーが管理するFacebookページ取得
    pages_url = f"{FB_GRAPH_API_BASE}/me/accounts"
    pages_params = {
        "access_token": user_access_token
    }
    pages_response = requests.get(pages_url, params=pages_params)
    pages_response.raise_for_status()
    pages_data = pages_response.json()

    if not pages_data.get('data'):
        print("管理しているFacebookページが見つかりません。")
        return []

    # とりあえず最初のページを利用
    page = pages_data['data'][0]
    page_id = page['id']
    page_access_token = page['access_token']

    # 2. Facebookページに紐づくInstagramビジネスアカウント取得
    insta_account_url = f"{FB_GRAPH_API_BASE}/{page_id}"
    insta_account_params = {
        "fields": "instagram_business_account",
        "access_token": page_access_token
    }
    insta_account_response = requests.get(
        insta_account_url, params=insta_account_params)
    insta_account_response.raise_for_status()
    insta_account_data = insta_account_response.json()

    if "instagram_business_account" not in insta_account_data:
        print("このFacebookページにはInstagramビジネスアカウントが紐づいていません。")
        return []

    instagram_account_id = insta_account_data["instagram_business_account"]["id"]

    # 3. Instagramビジネスアカウントからメディア取得
    media_url = f"{FB_GRAPH_API_BASE}/{instagram_account_id}/media"
    media_params = {
        "fields": "id,caption,media_url,permalink",
        "access_token": page_access_token
    }
    media_response = requests.get(media_url, params=media_params)
    media_response.raise_for_status()
    media_data = media_response.json().get('data', [])

    return media_data


def get_instagram_media_by_hashtag(hashtag):
    """
    指定されたハッシュタグを持つInstagramメディアを取得します。
    """
    user_access_token = settings.INSTAGRAM_ACCESS_TOKEN
    if not user_access_token:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN.pyで定義してく��さい。")

    # ハッシュタグIDを取得
    hashtag_search_url = f"{FB_GRAPH_API_BASE}/ig_hashtag_search"
    hashtag_params = {
        "user_id": settings.IG_USER_ID,
        "q": hashtag,
        "access_token": user_access_token
    }
    hashtag_response = requests.get(hashtag_search_url, params=hashtag_params)
    if hashtag_response.status_code != 200:
        print(f"Error fetching hashtag ID: {hashtag_response.text}")
    hashtag_response.raise_for_status()
    hashtag_data = hashtag_response.json()

    if not hashtag_data.get('data'):
        print(f"ハッシュタグ '{hashtag}' が見つかりません。")
        return []

    hashtag_id = hashtag_data['data'][0]['id']

    # ハッシュタグに関連するメディアを取得
    media_url = f"{FB_GRAPH_API_BASE}/{hashtag_id}/recent_media"
    media_params = {
        "user_id": settings.IG_USER_ID,
        "fields": "id,caption,media_url,permalink",
        "access_token": user_access_token
    }
    media_response = requests.get(media_url, params=media_params)
    if media_response.status_code != 200:
        print(f"Error fetching media: {media_response.text}")
    media_response.raise_for_status()
    media_data = media_response.json().get('data', [])

    return media_data
