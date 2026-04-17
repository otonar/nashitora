
import os
import openai
import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from .services.map_service import (
    load_locations,
    load_destination_numbers,
    get_selected_waypoints,
    search_nearby_hotels,
    generate_travel_plans,
    generate_multiple_points_route_html_with_labels
)
from .models import Hashtag
import csv
from io import TextIOWrapper, StringIO
from django.http import JsonResponse
from urllib.parse import quote
from urllib.parse import unquote
from .models import Hashtag
from django.views.decorators.csrf import csrf_exempt

INSTAGRAM_ACCESS_TOKEN = settings.INSTAGRAM_ACCESS_TOKEN
GRAPH_API_URL = "https://graph.facebook.com/v21.0"


file_path = os.path.join(settings.BASE_DIR, 'places', 'tourlist.csv')

# CSVファイルを辞書形式で読み込む
with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # print(row['スポット名'])  # 各行を辞書形式で出力

        try:
            if Hashtag.objects.filter(number=row['No.']).exists():
                print("duplicated")

            else:
                new_hashtag = Hashtag(
                    number=row["No."],
                    category=row['カテゴリ'],
                    spot=row['スポット名'],
                    address=row['住所'],
                    latitude=row['緯度'],
                    longitude=row['経度']
                )
                new_hashtag.save()
        except Exception as e:
            print(f"Error: {e}")


def route_view(request):
    if request.method == 'POST':
        # APIキーをsettingsから取得
        api_key = settings.GOOGLE_MAPS_API_KEY
        openai.api_key = settings.OPENAI_API_KEY

        # 選択された投稿番号を取得
        selected_posts = request.POST.getlist('selected_posts')
        print(f"受信した選択された投稿: {selected_posts}")

        # 空の値をフィルタリング
        selected_posts = [post for post in selected_posts if post]
        print(f"フィルタリング後の選択された投稿: {selected_posts}")

        if not selected_posts:
            return render(request, 'places/error.html', {'message': '選択された投稿がありません。'})

        try:
            # selected_posts を整数に変換
            selected_posts_int = [int(post) for post in selected_posts]
        except ValueError:
            return render(request, 'places/error.html', {'message': '選択された投稿の形式が無効です。'})

        print(f"選択された投稿番号（整数）: {selected_posts_int}")

        # 選択されたハッシュタグを取得
        hashtags = Hashtag.objects.filter(number__in=selected_posts_int)
        print(f"取得したハッシュタグ情報: {hashtags}")

        if not hashtags.exists():
            return render(request, 'places/error.html', {'message': '選択された投稿が見つかりません。'})

        # ルート生成のためのウェイポイントを構築
        waypoints = []
        for hashtag in hashtags:
            waypoint = {
                "name": hashtag.spot,
                "latitude": hashtag.latitude,
                "longitude": hashtag.longitude
            }
            waypoints.append(waypoint)
        print(f"生成されたウェイポイント: {waypoints}")

        # ホテル検索
        hotels = []
        for point in waypoints:
            nearby_hotels = search_nearby_hotels(api_key, point)
            hotels.extend(nearby_hotels)
        print(f"検索された近隣ホテル: {hotels}")

        # ルート情報（仮の値を使用）
        route_info = {
            "spots": [point["name"] for point in waypoints],
            "total_distance": "計算中...",
            "total_duration": "計算中..."
        }

        # 旅行プラン生成
        travel_plans = generate_travel_plans(route_info, hotels)
        print(f"生成された旅行プラン: {travel_plans}")

        # Google Maps用のHTMLコンテンツを生成
        html_content = generate_multiple_points_route_html_with_labels(
            api_key, waypoints, travel_plans=travel_plans
        )

        return HttpResponse(html_content)

    else:
        return render(request, 'places/error.html', {'message': '無効なリクエストです。'})


def home_view(request):
    hashtags = Hashtag.objects.all()  # Hashtagオブジェクトのクエリセットを取得
    posts = fetch_hashtag_posts(hashtags)

    if isinstance(posts, str):  # エラーメッセージの場合
        return render(request, 'places/error.html', {'message': posts})
    else:
        return render(request, 'places/home.html', {'posts': posts})


def get_user_id(INSTAGRAM_ACCESS_TOKEN):
    """
    FacebookページにリンクされたInstagramビジネスアカウントのユーザーIDを取得
    """
    print("get_user_id: アクセストークンを使用してユーザーIDを取得しようとしています。")
    # url = f"{GRAPH_API_URL}/me/accounts?access_token={INSTAGRAM_ACCESS_TOKEN}"
    base_url1 = "/me/accounts?access_token="
    enurl = quote(GRAPH_API_URL)+base_url1+quote(INSTAGRAM_ACCESS_TOKEN)
    url = unquote(enurl)

    try:
        # APIリクエスト
        print(f"get_user_id: リクエストURL: {url}")
        response = requests.get(url)

        # ステータスコードが200でない場合
        if response.status_code != 200:
            print(f"Error: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            raise ValueError(f"APIリクエストに失敗しました: {response.text}")

        print(f"get_user_id: accounts APIレスポンス: {response.status_code}")
        data = response.json()
        print(f"get_user_id: レスポンスデータ: {data}")

        # Instagramビジネスアカウント情報を取得
        if "data" in data:
            for page in data["data"]:
                page_id = page.get("id")
                print(f"get_user_id: ページID: {page_id}")

                # Instagramビジネスアカウント情報を取得するためのURL
                # instagram_url = f"{GRAPH_API_URL}/{page_id}?fields=instagram_business_account&access_token={INSTAGRAM_ACCESS_TOKEN}"
                base_url2 = "?fields=instagram_business_account&access_token="
                eninstagram_url = quote(
                    GRAPH_API_URL)+"/"+quote(page_id)+base_url2+quote(INSTAGRAM_ACCESS_TOKEN)
                instagram_url = unquote(eninstagram_url)
                print(
                    f"get_user_id: InstagramビジネスアカウントリクエストURL: {instagram_url}")

                insta_response = requests.get(instagram_url)

                print(
                    f"get_user_id: Instagram APIレスポンスステータス: {insta_response.status_code}")

                if insta_response.status_code != 200:
                    print(
                        f"Error: Instagram API request failed with status {insta_response.status_code}")
                    print(f"Response: {insta_response.text}")
                    raise ValueError(
                        f"Instagram APIリクエストに失敗しました: {insta_response.text}")

                insta_data = insta_response.json()
                print(f"get_user_id: Instagramデータ: {insta_data}")

                # InstagramビジネスアカウントIDを取得
                if "instagram_business_account" in insta_data:
                    instagram_id = insta_data["instagram_business_account"].get(
                        "id")
                    print(
                        f"get_user_id: 取得したInstagramビジネスアカウントID: {instagram_id}")
                    return instagram_id

        print("get_user_id: 有効なInstagramビジネスアカウントのユーザーIDが見つかりませんでした。")
        return None

    except requests.exceptions.RequestException as e:
        # リクエストエラーが発生した場合
        print(f"Error: RequestException occurred: {e}")
        raise ValueError(f"APIリクエストに失敗しました: {e}")


def fetch_hashtag_posts(hashtags):
    USER_ID = get_user_id(INSTAGRAM_ACCESS_TOKEN)
    print(f"USER_ID: {USER_ID}")
    if not USER_ID:
        raise ValueError("有効なInstagramビジネスアカウントのユーザーIDが取得できませんでした。")

    results = {}
    for hashtag in hashtags:
        clean_hashtag = hashtag.spot.lstrip('#')  # Hashtagオブジェクトのspotフィールドを使用
        print(f"fetch_hashtag_posts: クリーンなハッシュタグ「{clean_hashtag}」を使用します。")
        # ハッシュタグIDを取得
        search_url = f"{GRAPH_API_URL}/ig_hashtag_search?user_id={USER_ID}&q={clean_hashtag}&access_token={INSTAGRAM_ACCESS_TOKEN}"
        print(f"fetch_hashtag_posts: ハッシュタグ検索URL: {search_url}")
        response = requests.get(search_url)
        if response.status_code != 200:
            print(
                f"Error: ハッシュタグ検索APIリクエストに失敗しました。ステータスコード: {response.status_code}")
            continue

        hashtag_data = response.json()
        print(
            f"fetch_hashtag_posts: ハッシュタグ検索APIレスポンスステータス: {response.status_code}")
        print(f"fetch_hashtag_posts: APIレスポンス: {hashtag_data}")

        if ("data" not in hashtag_data) or (not hashtag_data["data"]):
            print("fetch_hashtag_posts: ハッシュタグが見つかりませんでした。")
            continue

        hashtag_id = hashtag_data["data"][0].get("id")
        print(f"fetch_hashtag_posts: 取得したハッシュタグID: {hashtag_id}")

        # 投稿取得URL
        posts_url = f"{GRAPH_API_URL}/{hashtag_id}/top_media?user_id={USER_ID}&fields=id,caption,media_type,media_url,timestamp&limit=3&access_token={INSTAGRAM_ACCESS_TOKEN}"
        print(f"fetch_hashtag_posts: 投稿取得URL: {posts_url}")

        posts_response = requests.get(posts_url)
        if posts_response.status_code != 200:
            print(
                f"Error: 投稿取得APIのリクエストに失敗しました。ステータスコード: {posts_response.status_code}")
            continue
        print(
            f"fetch_hashtag_posts: 投稿取得APIレスポンスステータス: {posts_response.status_code}")

        posts_data = posts_response.json()
        if ("data" not in posts_data) or (not posts_data["data"]):
            print("fetch_hashtag_posts: 投稿が見つかりませんでした。")
            continue
        print(f"fetch_hashtag_posts: 投稿データ: {posts_data}")

        posts = []
        for post in posts_data["data"]:
            print(f"fetch_hashtag_posts: 処理中の投稿ID: {post.get('id')}")
            post_data = {
                'media_type': post.get("media_type"),
                'media_url': post.get("media_url"),
                'caption': post.get("caption", "キャプションなし"),
                'timestamp': post.get("timestamp"),
                'number': hashtag.number,  # Hashtagのnumberを追加
            }
            posts.append(post_data)

        results[hashtag.spot] = posts
        print(
            f"fetch_hashtag_posts: ハッシュタグ「{hashtag.spot}」の投稿を取得しました。総数: {len(posts)}")

    return results


def display_posts(request):
    if request.method == "GET":
        hashtags = Hashtag.objects.values_list('spot', flat=True)
        posts = fetch_hashtag_posts(hashtags)

        if isinstance(posts, str):  # エラーメッセージの場合
            return render(request, 'places/error.html', {'message': posts})
        else:
            return render(request, 'places/graph.html', {'posts': posts})

    else:
        return render(request, 'places/error.html', {'message': '無効なリクエスト'})


def next_page(request):
    if request.method == 'POST':
        selected_posts = request.POST.getlist('selected_posts')
        print(f"Received selected_posts: {selected_posts}")

        if not selected_posts:
            return render(request, 'places/error.html', {'message': 'No posts selected'})
        # 選択した投稿の情報を取得
        numbers = Hashtag.objects.filter(
            spot__in=selected_posts).values_list('number', flat=True)
        print(f"Retrieved numbers: {list(numbers)}")
        return render(request, 'places/graph.html', {'numbers': numbers, 'selected_posts': selected_posts})

    else:
        return render(request, 'places/error.html', {'message': '無効なリクエスト'})
