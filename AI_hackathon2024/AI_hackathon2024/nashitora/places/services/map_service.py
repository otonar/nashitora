import csv
import openai
import requests
import json


def load_locations(csv_file):
    """CSVファイルから全ロケーション情報を読み込む"""
    locations = {}
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            locations[int(row['No.'])] = {
                "name": row['スポット名'],
                "latitude": float(row['緯度']),
                "longitude": float(row['経度'])
            }
    return locations


def load_destination_numbers(csv_file):
    """destination_no.csvから目的地の番号を読み込む"""
    with open(csv_file, 'r') as file:
        numbers = [int(num) for num in file.read().strip().split(',')]
    return numbers


def get_selected_waypoints(locations, destination_numbers):
    """選択された目的地の情報を取得"""
    waypoints = []
    for num in destination_numbers:
        if num in locations:
            waypoints.append(locations[num])
    return waypoints


def search_nearby_hotels(api_key, location, radius=5000):
    """指定された場所の周辺のホテルを検索"""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{location['latitude']},{location['longitude']}",
        "radius": radius,
        "type": "lodging",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get('results', [])

        hotels = []
        for result in results[:5]:  # 上位5件のみ取得
            hotels.append({
                "name": result.get('name'),
                "rating": result.get('rating', 'N/A'),
                "address": result.get('vicinity'),
                "location": {
                    "lat": result['geometry']['location']['lat'],
                    "lng": result['geometry']['location']['lng']
                }
            })
        return hotels
    except Exception as e:
        print(f"ホテル検索エラー: {e}")
        return []


def generate_travel_plans(route_info, hotels):
    """旅行プランを生成"""
    prompt = f"""
    以下の観光スポットを巡る3つの旅行プランを作成してください：
    
    訪問スポット: {', '.join(route_info['spots'])}
    総距離: {route_info['total_distance']}km
    予想所要時間: {route_info['total_duration']}
    
    利用可能なホテル:
    {', '.join([f"{h['name']}（評価: {h['rating']}）" for h in hotels])}
    
    以下の3つのプランを作成してください：
    1. 日帰りプラン
    2. 1泊2日プラン
    3. 2泊3日プラン
    
    各プランには以下を含めてください：
    - 具体的な時間配分
    - 食事場所の提案
    - 効率的な観光順序
    - 宿泊プランの場合は具体的な宿泊場所の提案
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                    "content": "あなたは山梨県の旅行プランナーです。現地の観光スポットやグルメに詳しく、効率的な旅程を提案できます。"},
                {"role": "user", "content": prompt}
            ]
        )

        return {
            "success": True,
            "plans": response.choices[0].message['content']
        }
    except Exception as e:
        print(f"プラン生成エラー: {e}")
        return {
            "success": False,
            "plans": "申し訳ありません。プランの生成中にエラーが発生しました。"
        }


def generate_multiple_points_route_html_with_labels(api_key, waypoints, travel_plans=None, initial_travel_mode="DRIVING", optimize_waypoints=True):
    """HTMLコンテンツを生成して文字列で返す関数"""
    origin = waypoints[0]
    destination = waypoints[-1]
    waypoint_locations = waypoints[1:-1]

    formatted_waypoints = ", ".join([
        f"{{ location: {{ lat: {point['latitude']}, lng: {point['longitude']} }}, stopover: true }}"
        for point in waypoint_locations
    ])

    markers_with_labels = "\n".join([
        f"""
        const marker{index} = new google.maps.Marker({{
            position: {{ lat: {point['latitude']}, lng: {point['longitude']} }},
            map: map,
            title: '{point['name']}',
            label: {{ text: '{index + 1}', color: 'white' }},
            animation: google.maps.Animation.DROP
        }});
        const infoWindow{index} = new google.maps.InfoWindow({{
            content: '<div style="padding: 10px;"><strong>{point['name']}</strong></div>'
        }});
        marker{index}.addListener('click', () => {{
            infoWindow{index}.open(map, marker{index});
        }});
        """
        for index, point in enumerate(waypoints)
    ])

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>観光ルート案内</title>
    <!-- API key: {api_key} -->
    <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=places"></script>
    <style>
        #map {{
            height: 600px;
            width: 100%;
            margin-bottom: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .controls {{
            margin-bottom: 20px;
        }}
        .info-panel {{
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }}
        .info-item {{
            margin: 5px 0;
        }}
        .travel-plans {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>観光スポット ルート案内</h1>
        
        <div class="controls">
            <label for="mode">移動手段: </label>
            <select id="mode" onchange="calculateAndDisplayRoute()">
                <option value="DRIVING">🚗 車</option>
                <option value="WALKING">🚶 徒歩</option>
            </select>
        </div>

        <div id="map"></div>
        
        <div class="info-panel">
            <div id="total-distance" class="info-item">📍 総距離: 計算中...</div>
            <div id="total-duration" class="info-item">⏱ 予想所要時間: 計算中...</div>
        </div>

        <div class="travel-plans">
            <h2>おすすめ旅行プラン</h2>
            <div id="travel-plans-content">
                <pre>{travel_plans['plans'] if travel_plans and travel_plans.get('success') else '旅行プランを生成中...'}</pre>
            </div>
        </div>
    </div>

    <script>
        let map;
        let currentDirectionsRenderer;
        let directionsService;

        function initMap() {{
            directionsService = new google.maps.DirectionsService();
            map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 12,
                center: {{ lat: {origin['latitude']}, lng: {origin['longitude']} }}
            }});

            calculateAndDisplayRoute();
            
            {markers_with_labels}
        }}

        function calculateAndDisplayRoute() {{
            if (currentDirectionsRenderer) {{
                currentDirectionsRenderer.setMap(null);
            }}
            
            currentDirectionsRenderer = new google.maps.DirectionsRenderer({{
                map: map,
                suppressMarkers: true
            }});

            const selectedMode = document.getElementById('mode').value;

            const request = {{
                origin: {{ lat: {origin['latitude']}, lng: {origin['longitude']} }},
                destination: {{ lat: {destination['latitude']}, lng: {destination['longitude']} }},
                waypoints: [{formatted_waypoints}],
                optimizeWaypoints: {str(optimize_waypoints).lower()},
                travelMode: google.maps.TravelMode[selectedMode]
            }};

            directionsService.route(request, (response, status) => {{
                if (status === 'OK') {{
                    currentDirectionsRenderer.setDirections(response);
                    
                    let totalDistance = 0;
                    let totalDuration = 0;
                    
                    response.routes[0].legs.forEach(leg => {{
                        totalDistance += leg.distance.value;
                        totalDuration += leg.duration.value;
                    }});
                    
                    const distanceKm = (totalDistance / 1000).toFixed(1);
                    const hours = Math.floor(totalDuration / 3600);
                    const minutes = Math.floor((totalDuration % 3600) / 60);
                    
                    document.getElementById('total-distance').textContent = `📍 総距離: ${{distanceKm}} km`;
                    document.getElementById('total-duration').textContent = 
                        `⏱ 予想所要時間: ${{hours}}時間${{minutes}}分`;
                }} else {{
                    window.alert('ルートの取得に失敗しました: ' + status);
                }}
            }});
        }}

        window.onload = initMap;
    </script>
</body>
</html>
"""
    return html_content
