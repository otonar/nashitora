# import os
# import requests
# from dotenv import load_dotenv
# load_dotenv()


# def test_instagram_api():
#     # アクセストークンを環境変数から取得
#     access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
#     if not access_token:
#         raise ValueError(
#             "INSTAGRAM_ACCESS_TOKENが設定されていません。環境変数または設定ファイルで指定してください。")

#     # 1. 管理しているFacebookページの一覧を取得
#     pages_url = "https://graph.facebook.com/me/accounts"
#     pages_params = {
#         "access_token": access_token
#     }

#     pages_response = requests.get(pages_url, params=pages_params)
#     pages_response.raise_for_status()
#     pages_data = pages_response.json()

#     if "data" not in pages_data or len(pages_data["data"]) == 0:
#         print("管理しているFacebookページが見つかりませんでした。Instagramビジネスアカウントが紐付いているか確認してください。")
#         return

#     # 最初のページを利用（必要に応じて特定のページを選ぶロジックを追加）
#     first_page = pages_data["data"][0]
#     page_id = first_page["id"]
#     page_access_token = first_page["access_token"]

#     print(f"取得したFacebookページID: {page_id}")

#     # 2. ページに紐づくInstagramビジネスアカウントIDを取得
#     insta_account_url = f"https://graph.facebook.com/{page_id}"
#     insta_account_params = {
#         "fields": "instagram_business_account",
#         "access_token": page_access_token
#     }

#     insta_account_response = requests.get(
#         insta_account_url, params=insta_account_params)
#     insta_account_response.raise_for_status()
#     insta_account_data = insta_account_response.json()

#     if "instagram_business_account" not in insta_account_data:
#         print("このFacebookページにはInstagramビジネスアカウントが紐付いていません。設定を確認してください。")
#         return

#     instagram_account_id = insta_account_data["instagram_business_account"]["id"]
#     print(f"取得したInstagramビジネスアカウントID: {instagram_account_id}")

#     # 3. Instagramビジネスアカウントのメディア一覧を取得
#     media_url = f"https://graph.facebook.com/{instagram_account_id}/media"
#     media_params = {
#         "fields": "id,caption,media_url,permalink",
#         "access_token": page_access_token
#     }

#     media_response = requests.get(media_url, params=media_params)
#     media_response.raise_for_status()
#     media_data = media_response.json()

#     if "data" in media_data:
#         print("メディア一覧を取得しました:")
#         for item in media_data["data"]:
#             print(
#                 f"- ID: {item['id']}, URL: {item.get('media_url')}, Permalink: {item.get('permalink')}")
#     else:
#         print("メディアが存在しないか、取得できませんでした。")


# if __name__ == "__main__":
#     test_instagram_api()


import requests


import requests


def test_instagram_api():
    access_token = 'EAAdrMCbdr1YBO4PMuGRsCEwdb94hKmQ4QPdhwy9ENKb73bKutgid7tpqU4RF1XKd0Xs4LfIUSBfnKJixybHGCUuubVTkPrbh8U0vjqZC8Xq9Kxd8CIq12ZCT8KZCWtMvCySD9fvklMCBIla8SGR8ZBRdWTGuUlDMpvzAB7gNxJlQytpCpn8IvVHZCo5q6jq8xkFFhpB2QFQ9ZBsESguAZDZD'
    url = f'https://graph.facebook.com/me/accounts?access_token={access_token}'
    response = requests.get(url)
    try:
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.HTTPError as e:
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス内容: {response.text}")
        raise e


if __name__ == "__main__":
    test_instagram_api()
