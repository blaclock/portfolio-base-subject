# SNS Camp API

## 概要

SNS Camp は、投稿・フォロー・いいね機能を備えたシンプルな SNS アプリケーションです。本リポジトリはそのバックエンド API サーバーで、Python (FastAPI) で実装されています。

- REST API（認証、投稿、フォロー、いいね機能）
- JWT 認証（HS256、有効期限24時間）
- データベースおよびテーブルはアプリケーション起動時に自動作成

| 技術 | 説明 |
|---|---|
| Python / FastAPI | Web フレームワーク |
| SQLAlchemy | ORM |
| MySQL 8.0 | データベース |
| python-jose | JWT 認証 |
| passlib (bcrypt) | パスワードハッシュ化 |

### 環境変数

| 変数名 | 説明 | デフォルト値 |
|---|---|---|
| PORT | APIサーバのポート番号 | 8080 |
| DB_HOST | MySQLホスト名 | localhost |
| DB_PORT | MySQLポート番号 | 3306 |
| DB_USER | MySQLユーザ名 | root |
| DB_PASSWORD | MySQLパスワード | password |
| DB_NAME | データベース名 | sns_camp |
| JWT_SECRET | JWT署名用シークレットキー | your-secret-key |
| ALLOWED_ORIGINS | CORS許可オリジン | http://localhost:3000 |

---

## ローカル環境での起動方法

### Docker Compose で起動（API + MySQL）

```bash
docker compose up -d
```

このコマンドで以下が起動します：
- **MySQL** (ポート: 3306) - データベース
- **API** (ポート: 8080) - バックエンドサーバー

#### 起動確認

```bash
curl http://localhost:8080/health
# {"status":"ok"} が返れば成功
```

#### 停止・削除

```bash
docker compose down

# DBデータも削除する場合
docker compose down -v
```

API 単体で動作するため、フロントエンドなしでも起動・動作確認が可能です。

#### デプロイ後の確認

```bash
curl http://localhost:8080/health
# {"status":"ok"} が返れば成功
```

---

## AWS での起動方法

### データベース

RDS (MySQL 8.0) で起動できます。データベースとテーブルは API の初回起動時に自動作成されるため、手動でのマイグレーション作業は不要です。

### API

ECS (Fargate) で起動できます。

#### ECR へのイメージプッシュ

```bash
# ECR にログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <アカウントID>.dkr.ecr.ap-northeast-1.amazonaws.com

# イメージをビルド（Apple シリコンの場合は --platform を指定）
docker build --platform linux/amd64 -t sns-camp-api .

# タグ付け
docker tag sns-camp-api:latest <アカウントID>.dkr.ecr.ap-northeast-1.amazonaws.com/sns-camp-api:latest

# プッシュ
docker push <アカウントID>.dkr.ecr.ap-northeast-1.amazonaws.com/sns-camp-api:latest
```

#### ECS タスク定義の環境変数

| 変数名 | 設定値 | 設定例 |
|---|---|---|
| `DB_HOST` | RDS のエンドポイント | `sns-camp-db.xxxxxxxxxxxx.ap-northeast-1.rds.amazonaws.com` |
| `DB_PORT` | MySQL のポート番号 | `3306`（固定） |
| `DB_USER` | RDS のユーザ名 | `admin` |
| `DB_PASSWORD` | RDS のパスワード | `yourpassword` |
| `DB_NAME` | データベース名 | `sns_camp`（固定） |
| `JWT_SECRET` | JWT 署名用シークレットキー（本番用に変更すること） | `my-secret-key-12345` |
| `ALLOWED_ORIGINS` | フロントエンドの URL（CORS 許可オリジン） | `https://sns-camp.example.com` |

> **補足**: `ALLOWED_ORIGINS` はブラウザからの CORS リクエストを許可するための設定です。フロントエンドを使用せず API 単体で動作させる場合は、ダミー値（例: `https://dummy.example.com`）を設定すれば問題ありません。

#### デプロイ後の確認

`<your-host>` は ALB や ECS に設定したドメインに読み替えてください。

```bash
curl http://<your-host>/health
# {"status":"ok"} が返れば成功
```

---

## 動作確認

API が正常に動作していることを確認する手順です。

`<your-host>` は環境に合わせて読み替えてください。
- ローカル環境: `localhost:8080`
- AWS 環境: ALB や ECS に設定したドメイン

### 1. ヘルスチェック

```bash
curl http://<your-host>/health
```

```json
{"status":"ok"}
```

### 2. ユーザ登録

```bash
curl -X POST http://<your-host>/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "display_name": "テストユーザ"
  }'
```

レスポンスに含まれる `token` を以降の手順で使用します。

```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": { "id": 1, "username": "testuser", "email": "test@example.com", "display_name": "テストユーザ" }
  }
}
```

### 3. ログイン

```bash
curl -X POST http://<your-host>/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": { "id": 1, "username": "testuser", "email": "test@example.com", "display_name": "テストユーザ" }
  }
}
```

### 4. 投稿作成

取得したトークンを `TOKEN` に設定して実行します。

```bash
TOKEN="eyJhbGciOiJIUzI1NiIs..."

curl -X POST http://<your-host>/api/v1/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "はじめての投稿です"
  }'
```

### 5. タイムライン取得

```bash
curl http://<your-host>/api/v1/timeline \
  -H "Authorization: Bearer $TOKEN"
```

投稿した内容が一覧に表示されれば正常に動作しています。

これ以外にも、フォローやいいねなど様々な機能が用意されています。詳しくは後続のAPI仕様書を参照してください。

---

# API仕様書

## APIの概要

SNS Camp のバックエンド REST API です。ユーザ認証、投稿、フォロー、いいね機能を提供します。

## 共通仕様

- ベースURL: `http://<your-host>/api/v1`
- 日時フォーマット: ISO 8601（例: `2026-04-03T12:00:00`）
- ページネーション: クエリパラメータ `limit`（デフォルト: 20、最大: 100）、`offset`（デフォルト: 0）

## 認証方式

ヘルスチェック・ユーザ登録・ログインを除くすべてのAPIリクエストにBearerトークンが必要です。

```
Authorization: Bearer <access_token>
```

トークンは JWT（HS256）で、有効期限は24時間です。

## レスポンス形式

成功時:
```json
{ "data": { ... } }
```

エラー時:
```json
{ "error": { "code": "ERROR_CODE", "message": "エラーメッセージ" } }
```

## ステータスコード一覧

| ステータスコード | 意味 |
|---|---|
| 200 | リクエスト成功 |
| 201 | リソース作成成功 |
| 400 | バリデーションエラー / ビジネスロジックエラー |
| 401 | 認証エラー |
| 403 | 権限エラー |
| 404 | リソースが見つからない |
| 500 | サーバ内部エラー |

## エンドポイント一覧

| No. | API ID | API名 | メソッド | エンドポイント | 認証 |
|---|---|---|---|---|---|
| 1 | API-001 | ヘルスチェック | GET | /health | 不要 |
| 2 | API-002 | ユーザ登録 | POST | /api/v1/auth/register | 不要 |
| 3 | API-003 | ログイン | POST | /api/v1/auth/login | 不要 |
| 4 | API-004 | 現在のユーザ取得 | GET | /api/v1/auth/me | 必要 |
| 5 | API-005 | 投稿作成 | POST | /api/v1/posts | 必要 |
| 6 | API-006 | 投稿詳細取得 | GET | /api/v1/posts/{post_id} | 必要 |
| 7 | API-007 | 投稿編集 | PUT | /api/v1/posts/{post_id} | 必要 |
| 8 | API-008 | 投稿削除 | DELETE | /api/v1/posts/{post_id} | 必要 |
| 9 | API-009 | タイムライン取得 | GET | /api/v1/timeline | 必要 |
| 10 | API-010 | ユーザプロフィール取得 | GET | /api/v1/users/{username} | 必要 |
| 11 | API-011 | ユーザの投稿一覧取得 | GET | /api/v1/users/{username}/posts | 必要 |
| 12 | API-012 | フォローする | POST | /api/v1/users/{username}/follow | 必要 |
| 13 | API-013 | フォロー解除 | DELETE | /api/v1/users/{username}/follow | 必要 |
| 14 | API-014 | フォロワー一覧取得 | GET | /api/v1/users/{username}/followers | 必要 |
| 15 | API-015 | フォロー中一覧取得 | GET | /api/v1/users/{username}/following | 必要 |
| 16 | API-016 | いいねする | POST | /api/v1/posts/{post_id}/like | 必要 |
| 17 | API-017 | いいね解除 | DELETE | /api/v1/posts/{post_id}/like | 必要 |

---

## API詳細

### API-001 ヘルスチェック

`GET /health`

レスポンス（200 OK）:

```json
{ "status": "ok" }
```

---

### API-002 ユーザ登録

`POST /api/v1/auth/register`

リクエストパラメータ:

| パラメータ名 | 型 | 必須 | 説明 |
|---|---|---|---|
| username | string | ○ | ユーザ名（3〜20文字、英数字とアンダースコアのみ） |
| email | string | ○ | メールアドレス（一意制約あり） |
| password | string | ○ | パスワード（8文字以上） |
| display_name | string | - | 表示名（50文字以内） |

リクエスト例:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "display_name": "テストユーザ"
}
```

レスポンス（201 Created）:

| フィールド名 | 型 | 説明 |
|---|---|---|
| data.token | string | JWTアクセストークン |
| data.user.id | integer | ユーザID |
| data.user.username | string | ユーザ名 |
| data.user.email | string | メールアドレス |
| data.user.display_name | string / null | 表示名 |

レスポンス例:

```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "display_name": "テストユーザ"
    }
  }
}
```

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 400 | USERNAME_EXISTS | ユーザ名の重複 |
| 400 | EMAIL_EXISTS | メールアドレスの重複 |
| 400 | VALIDATION_ERROR | バリデーションエラー |

---

### API-003 ログイン

`POST /api/v1/auth/login`

リクエストパラメータ:

| パラメータ名 | 型 | 必須 | 説明 |
|---|---|---|---|
| email | string | ○ | メールアドレス |
| password | string | ○ | パスワード |

リクエスト例:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

レスポンス（200 OK）:

```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "display_name": "テストユーザ"
    }
  }
}
```

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 401 | INVALID_CREDENTIALS | メールアドレスまたはパスワードが正しくない |

---

### API-004 現在のユーザ取得

`GET /api/v1/auth/me`

レスポンス（200 OK）:

| フィールド名 | 型 | 説明 |
|---|---|---|
| data.id | integer | ユーザID |
| data.username | string | ユーザ名 |
| data.email | string | メールアドレス |
| data.display_name | string / null | 表示名 |
| data.created_at | string | 作成日時（ISO 8601） |
| data.updated_at | string | 更新日時（ISO 8601） |

---

### API-005 投稿作成

`POST /api/v1/posts`

リクエストパラメータ:

| パラメータ名 | 型 | 必須 | 説明 |
|---|---|---|---|
| content | string | ○ | 投稿内容（1〜280文字） |

リクエスト例:

```json
{
  "content": "これはテスト投稿です"
}
```

レスポンス（201 Created）:

| フィールド名 | 型 | 説明 |
|---|---|---|
| data.id | integer | 投稿ID |
| data.user_id | integer | 投稿者ID |
| data.content | string | 投稿内容 |
| data.username | string | 投稿者ユーザ名 |
| data.display_name | string / null | 投稿者表示名 |
| data.like_count | integer | いいね数 |
| data.is_liked | boolean | 自分がいいね済みか |
| data.created_at | string | 作成日時（ISO 8601） |
| data.updated_at | string | 更新日時（ISO 8601） |

---

### API-006 投稿詳細取得

`GET /api/v1/posts/{post_id}`

パスパラメータ:

| パラメータ名 | 型 | 説明 |
|---|---|---|
| post_id | integer | 投稿ID |

レスポンス（200 OK）: API-005 と同じ形式

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 404 | NOT_FOUND | 投稿が見つからない |

---

### API-007 投稿編集

`PUT /api/v1/posts/{post_id}`

リクエストパラメータ:

| パラメータ名 | 型 | 必須 | 説明 |
|---|---|---|---|
| content | string | ○ | 投稿内容（1〜280文字） |

レスポンス（200 OK）: API-005 と同じ形式

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 403 | FORBIDDEN | 他人の投稿は編集できない |
| 404 | NOT_FOUND | 投稿が見つからない |

---

### API-008 投稿削除

`DELETE /api/v1/posts/{post_id}`

レスポンス（200 OK）:

```json
{
  "data": {
    "message": "投稿を削除しました"
  }
}
```

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 403 | FORBIDDEN | 他人の投稿は削除できない |
| 404 | NOT_FOUND | 投稿が見つからない |

---

### API-009 タイムライン取得

`GET /api/v1/timeline`

クエリパラメータ:

| パラメータ名 | 型 | 必須 | 説明 |
|---|---|---|---|
| limit | integer | - | 取得件数（デフォルト: 20、最大: 100） |
| offset | integer | - | オフセット（デフォルト: 0） |
| filter | string | - | `all`（全投稿）または `following`（フォロー中のみ）、デフォルト: `all` |

レスポンス（200 OK）:

```json
{
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "content": "投稿内容",
      "username": "testuser",
      "display_name": "テストユーザ",
      "like_count": 3,
      "is_liked": false,
      "created_at": "2026-04-03T12:00:00",
      "updated_at": "2026-04-03T12:00:00"
    }
  ]
}
```

---

### API-010 ユーザプロフィール取得

`GET /api/v1/users/{username}`

レスポンス（200 OK）:

| フィールド名 | 型 | 説明 |
|---|---|---|
| data.id | integer | ユーザID |
| data.username | string | ユーザ名 |
| data.display_name | string / null | 表示名 |
| data.followers_count | integer | フォロワー数 |
| data.following_count | integer | フォロー中数 |
| data.is_following | boolean | 自分がフォロー済みか |

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 404 | NOT_FOUND | ユーザが見つからない |

---

### API-011 ユーザの投稿一覧取得

`GET /api/v1/users/{username}/posts`

クエリパラメータ:

| パラメータ名 | 型 | 必須 | 説明 |
|---|---|---|---|
| limit | integer | - | 取得件数（デフォルト: 20、最大: 100） |
| offset | integer | - | オフセット（デフォルト: 0） |

レスポンス（200 OK）: API-009 と同じ形式（配列）

---

### API-012 フォローする

`POST /api/v1/users/{username}/follow`

レスポンス（201 Created）:

```json
{
  "data": {
    "message": "フォローしました"
  }
}
```

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 400 | VALIDATION_ERROR | 自分自身はフォローできない |
| 400 | ALREADY_FOLLOWING | 既にフォロー済み |
| 404 | NOT_FOUND | ユーザが見つからない |

---

### API-013 フォロー解除

`DELETE /api/v1/users/{username}/follow`

レスポンス（200 OK）:

```json
{
  "data": {
    "message": "フォローを解除しました"
  }
}
```

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 400 | NOT_FOLLOWING | フォローしていない |
| 404 | NOT_FOUND | ユーザが見つからない |

---

### API-014 フォロワー一覧取得

`GET /api/v1/users/{username}/followers`

クエリパラメータ: limit, offset（API-011 と同じ）

レスポンス（200 OK）:

```json
{
  "data": [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "display_name": "ユーザ1"
    }
  ]
}
```

---

### API-015 フォロー中一覧取得

`GET /api/v1/users/{username}/following`

クエリパラメータ: limit, offset（API-011 と同じ）

レスポンス（200 OK）: API-014 と同じ形式

---

### API-016 いいねする

`POST /api/v1/posts/{post_id}/like`

レスポンス（201 Created）:

```json
{
  "data": {
    "message": "いいねしました",
    "like_count": 4
  }
}
```

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 400 | VALIDATION_ERROR | 自分の投稿にはいいねできない |
| 400 | ALREADY_LIKED | 既にいいね済み |
| 404 | NOT_FOUND | 投稿が見つからない |

---

### API-017 いいね解除

`DELETE /api/v1/posts/{post_id}/like`

レスポンス（200 OK）:

```json
{
  "data": {
    "message": "いいねを解除しました",
    "like_count": 3
  }
}
```

エラーレスポンス:

| ステータスコード | エラーコード | エラー内容 |
|---|---|---|
| 400 | NOT_LIKED | いいねしていない |
| 404 | NOT_FOUND | 投稿が見つからない |

---

# データベース仕様

データベースとテーブルはアプリケーション起動時に自動作成されます。

## users テーブル

| カラム | 型 | 説明 |
|---|---|---|
| id | BIGINT | 主キー |
| username | VARCHAR(20) | ユーザ名（一意） |
| email | VARCHAR(255) | メールアドレス（一意） |
| password_hash | VARCHAR(255) | パスワードハッシュ |
| display_name | VARCHAR(50) | 表示名 |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## posts テーブル

| カラム | 型 | 説明 |
|---|---|---|
| id | BIGINT | 主キー |
| user_id | BIGINT | 投稿者ID（FK: users.id） |
| content | VARCHAR(280) | 投稿内容 |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## follows テーブル

| カラム | 型 | 説明 |
|---|---|---|
| id | BIGINT | 主キー |
| follower_id | BIGINT | フォローするユーザID（FK: users.id） |
| following_id | BIGINT | フォローされるユーザID（FK: users.id） |
| created_at | TIMESTAMP | 作成日時 |

## likes テーブル

| カラム | 型 | 説明 |
|---|---|---|
| id | BIGINT | 主キー |
| user_id | BIGINT | いいねしたユーザID（FK: users.id） |
| post_id | BIGINT | いいねされた投稿ID（FK: posts.id） |
| created_at | TIMESTAMP | 作成日時 |

---

# テスト仕様

## 自動テスト

pytest を使用した自動テストです。テストは SQLite のインメモリ DB を使用するため、MySQL の起動は不要です。

| 種類 | ツール | 実行コマンド | 説明 |
|---|---|---|---|
| ユニットテスト | pytest | `pytest` | API エンドポイントの自動テスト |
| 詳細出力 | pytest | `pytest -v` | テスト名を表示して実行 |
| カバレッジ計測 | pytest-cov | `pytest --cov=app --cov-report=term-missing` | テストカバレッジの確認（未カバー行番号付き） |

テストは Arrange（準備）- Act（実行）- Assert（検証）パターンで記述されています。フィクスチャによりユーザ登録・認証ヘッダーの生成を共通化し、パラメタライズドテストで複数パターンのバリデーションを検証しています。

## 静的解析

講座「Pythonで静的解析をしよう」で扱う3つのツールを導入しています。

| 種類 | ツール | 実行コマンド | 説明 |
|---|---|---|---|
| コードスタイルチェック | Flake8 | `flake8 app/` | PEP 8 に準拠しているかを検証 |
| コード自動フォーマット | Black | `black app/` | コードスタイルを自動修正 |
| 型チェック | mypy | `mypy app/` | 型アノテーションの不整合を検出 |

### 設定ファイル

| ファイル | 対象ツール | 主な設定 |
|---|---|---|
| `.flake8` | Flake8 | 1行120文字、循環的複雑度10、E203/W503を無視 |
| `pyproject.toml` | Black / mypy | 1行120文字（Black）、Python 3.12（mypy） |

### 実行例

```bash
# 自動テスト
pytest -v

# カバレッジ計測
pytest --cov=app --cov-report=term-missing

# コードスタイルチェック
flake8 app/

# フォーマット確認（変更なし）
black --check app/

# フォーマット実行（自動修正）
black app/

# 型チェック
mypy app/
```

## テスト項目表

### ヘルスチェック（test_health.py）

| No. | テストID | テスト項目 | 対象API | 期待値 |
|---|---|---|---|---|
| 1 | HEALTH-001 | ヘルスチェック | GET /health | 200と `{"status":"ok"}` が返ること |

### 認証（test_auth.py）

| No. | テストID | テスト関数 | 対象API | 期待値 |
|---|---|---|---|---|
| 2 | AUTH-001 | test_register_success | POST /auth/register | 正しいパラメータで201が返ること |
| 3 | AUTH-002 | test_register_duplicate_username | POST /auth/register | 既存ユーザ名で400（USERNAME_EXISTS）が返ること |
| 4 | AUTH-003 | test_register_duplicate_email | POST /auth/register | 既存メールで400（EMAIL_EXISTS）が返ること |
| 5 | AUTH-004 | test_register_invalid_username | POST /auth/register | 2文字以下・21文字以上・記号含みで422が返ること（パラメタライズ） |
| 6 | AUTH-005 | test_register_short_password | POST /auth/register | 7文字以下で422が返ること |
| 7 | AUTH-006 | test_login_success | POST /auth/login | 正しい認証情報で200とトークンが返ること |
| 8 | AUTH-007 | test_login_wrong_email | POST /auth/login | 存在しないメールで401が返ること |
| 9 | AUTH-008 | test_login_wrong_password | POST /auth/login | 誤ったパスワードで401が返ること |
| 10 | AUTH-009 | test_me_success | GET /auth/me | 有効なトークンで200とユーザ情報が返ること |
| 11 | AUTH-010 | test_me_no_token | GET /auth/me | トークンなしで403が返ること |
| 12 | AUTH-011 | test_me_invalid_token | GET /auth/me | 無効なトークンで401が返ること |

### 投稿（test_posts.py）

| No. | テストID | テスト関数 | 対象API | 期待値 |
|---|---|---|---|---|
| 13 | POST-001 | test_create_post | POST /posts | 正しいパラメータで201が返ること |
| 14 | POST-002 | test_create_post_empty | POST /posts | 空の content で422が返ること |
| 15 | POST-003 | test_create_post_too_long | POST /posts | 280文字超で422が返ること |
| 16 | POST-004 | test_create_post_no_auth | POST /posts | トークンなしで403が返ること |
| 17 | POST-005 | test_get_post | GET /posts/{id} | 存在する投稿IDで200が返ること |
| 18 | POST-006 | test_get_post_not_found | GET /posts/{id} | 存在しないIDで404が返ること |
| 19 | POST-007 | test_update_post | PUT /posts/{id} | 本人の投稿を正常に更新できること |
| 20 | POST-008 | test_update_post_forbidden | PUT /posts/{id} | 他人の投稿で403が返ること |
| 21 | POST-009 | test_delete_post | DELETE /posts/{id} | 本人の投稿を正常に削除できること |
| 22 | POST-010 | test_delete_post_forbidden | DELETE /posts/{id} | 他人の投稿で403が返ること |

### タイムライン（test_timeline.py）

| No. | テストID | テスト関数 | 対象API | 期待値 |
|---|---|---|---|---|
| 23 | TL-001 | test_timeline_all | GET /timeline?filter=all | 全ユーザの投稿が新着順で返ること |
| 24 | TL-002 | test_timeline_following | GET /timeline?filter=following | フォロー中ユーザと自分の投稿のみ返ること |
| 25 | TL-003 | test_timeline_pagination | GET /timeline?limit=5&offset=0 | limit/offset が正しく動作すること |
| 26 | TL-004 | test_timeline_no_auth | GET /timeline | トークンなしで403が返ること |

### ユーザ（test_users.py）

| No. | テストID | テスト関数 | 対象API | 期待値 |
|---|---|---|---|---|
| 27 | USER-001 | test_get_profile | GET /users/{username} | 存在するユーザのプロフィールが返ること |
| 28 | USER-002 | test_get_profile_not_found | GET /users/{username} | 存在しないユーザで404が返ること |
| 29 | USER-003 | test_get_profile_is_following | GET /users/{username} | is_following が正しく反映されること |
| 30 | USER-004 | test_get_user_posts | GET /users/{username}/posts | 指定ユーザの投稿が新着順で返ること |

### フォロー（test_follow.py）

| No. | テストID | テスト関数 | 対象API | 期待値 |
|---|---|---|---|---|
| 31 | FOLLOW-001 | test_follow | POST /users/{username}/follow | 201とメッセージが返ること |
| 32 | FOLLOW-002 | test_follow_self | POST /users/{username}/follow | 自分自身で400が返ること |
| 33 | FOLLOW-003 | test_follow_already_following | POST /users/{username}/follow | 重複フォローで400（ALREADY_FOLLOWING）が返ること |
| 34 | FOLLOW-004 | test_unfollow | DELETE /users/{username}/follow | 200とメッセージが返ること |
| 35 | FOLLOW-005 | test_unfollow_not_following | DELETE /users/{username}/follow | フォローしていない状態で400（NOT_FOLLOWING）が返ること |
| 36 | FOLLOW-006 | test_get_followers | GET /users/{username}/followers | フォロワーの一覧が返ること |
| 37 | FOLLOW-007 | test_get_following | GET /users/{username}/following | フォロー中の一覧が返ること |

### いいね（test_likes.py）

| No. | テストID | テスト関数 | 対象API | 期待値 |
|---|---|---|---|---|
| 38 | LIKE-001 | test_like_post | POST /posts/{id}/like | 201といいね数が返ること |
| 39 | LIKE-002 | test_like_own_post | POST /posts/{id}/like | 自分の投稿で400が返ること |
| 40 | LIKE-003 | test_like_already_liked | POST /posts/{id}/like | 重複いいねで400（ALREADY_LIKED）が返ること |
| 41 | LIKE-004 | test_like_nonexistent_post | POST /posts/{id}/like | 存在しない投稿で404が返ること |
| 42 | LIKE-005 | test_unlike_post | DELETE /posts/{id}/like | 200といいね数が返ること |
| 43 | LIKE-006 | test_unlike_not_liked | DELETE /posts/{id}/like | いいねしていない状態で400（NOT_LIKED）が返ること |
