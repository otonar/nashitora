FROM python:3.10-slim

WORKDIR /app

# requirements.txt をコピーして依存関係をインストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# すべてのファイルを/app下にコピー
COPY . /app/

EXPOSE 8000

# Django開発サーバ起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

