"""
数据库 CRUD 操作
"""
import json
from sqlalchemy.orm import Session
from .models import HomePage, News
from .schemas import HomeUpdate


def get_or_create_home(db: Session) -> HomePage:
    """获取或创建首页数据（单例模式）"""
    home = db.query(HomePage).first()
    if not home:
        home = HomePage(
            nav_brand_text="EIHO / 衛宝",
            nav_top_text="トップ",
            nav_concept_text="メッセージ",
            nav_news_text="ニュース",
            nav_services_text="事業内容",
            nav_strengths_text="強み",
            nav_profile_text="会社概要",
            nav_cta_text="お問合わせ",
            hero_kicker="Japan × China | Automotive Trading",
            hero_title="品質と情熱で、日中のカーライフを繋ぐ架け橋へ",
            hero_subtitle="株式会社衛宝（EIHO Co., Ltd.）は、日本と中国という世界最大級の自動車市場を結ぶ貿易のエキスパートです。\n厳選された高品質な自動車用品の輸入・輸出を通じて、ドライバーの皆様に「安心・快適・楽しさ」をお届けすることを使命としています。",
            hero_primary_cta="事業内容を見る",
            hero_secondary_cta="会社概要",
            concept_title="メッセージ（コンセプト）",
            concept_subtitle="私たちは「貿易＝運ぶ」だけではなく、「信頼＝つなぐ」ことを重視します。\n現地ネットワークの強みと、日本基準の品質管理を掛け合わせ、安心して選べるカー用品を届け続けます。",
            mission_title="Mission",
            mission_body="高品質な自動車用品の輸出入を通じて、日中市場の価値循環を加速させます。",
            vision_title="Vision",
            vision_body="「品質と情熱」で、日中カーライフの架け橋となるグローバル・パートナーへ。",
            services_section_title="事業内容（Our Services）",
            services_section_subtitle="輸入・輸出・OEM/コンサルまで、日中ビジネスをトータルに支援します。",
            strengths_section_title="当社の強み（Why Choose Us?）",
            strengths_section_subtitle="スピード・品質・柔軟性。日中ビジネスに必要な“実務力”で差をつけます。",
            profile_title="会社概要（Company Profile）",
            profile_subtitle="以下はテンプレートです。住所・代表者・設立年月などを差し替えてそのまま使えます。",
            company_name="株式会社 衛宝（EIHO Co., Ltd.）",
            address="〒000-0000 [都道府県・住所を入力]",
            representative="[代表者名を入力]",
            established="[設立年・月を入力]",
            business_desc="自動車関連部品および自動車用品、カーアクセサリーの輸出入及び販売\n卸売\nコンサルティング・OEM受託（市場調査／製品開発支援）",
            clients="日本国内のカーショップ、中国国内の製造メーカー、各商社",
            cta_title="日中貿易・OEMのご相談はこちら",
            cta_subtitle="小ロットのテスト導入から量産・仕様調整まで。まずは要件だけでもお聞かせください。",
            cta_button_text="メールで問い合わせ",
            cta_phone_text="または：03-0000-0000（平日 9:00–18:00）",
            contact_form_title="お問い合わせフォーム（ダミー）",
            contact_form_note="※このフォームはデモです（送信は行いません）。実運用ではバックエンド（例：Node/PHP/Django等）に接続してください。",
            contact_examples_title="対応可能なご相談例",
            access_title="アクセス",
            access_address="〒000-0000 [都道府県・住所を入力]",
            footer_copyright="EIHO Co., Ltd. All rights reserved.",
            footer_link_top="TOP",
            footer_link_services="Services",
            footer_link_profile="Profile",
        )
        # 默认数据
        home.hero_stats_json = json.dumps([
            {
                "value": 2,
                "suffix": "国間",
                "label": "日中の調達・販売を一気通貫"
            },
            {
                "value": 3,
                "suffix": "領域",
                "label": "輸入 / 輸出 / OEM・コンサル"
            },
            {
                "value": 100,
                "suffix": "%",
                "label": "品質基準に向けた検品体制"
            },
        ], ensure_ascii=False)
        home.concept_points_json = json.dumps([
            {
                "label": "安心",
                "body": "検品・規格・品質の可視化"
            },
            {
                "label": "快適",
                "body": "機能性・耐久性・コスパの両立"
            },
            {
                "label": "楽しさ",
                "body": "カーライフを彩るアクセサリー提案"
            },
        ], ensure_ascii=False)
        home.services_json = json.dumps([
            {
                "title": "輸入事業（Import）",
                "body": "中国の先進的な製造ネットワークを駆使し、最新のカーアクセサリーや機能パーツをいち早く日本市場へ導入。徹底した検品体制で、コストパフォーマンスと品質を両立させた製品を提供します。",
                "icon": "box-seam"
            },
            {
                "title": "輸出事業（Export）",
                "body": "信頼の「Made in Japan」ブランドの自動車用品・メンテナンス用品を中国市場へ展開。現地のニーズを的確に捉えたマーケティングにより、日本の優れた技術を世界へ広めます。",
                "icon": "truck"
            },
            {
                "title": "コンサル・OEM受託",
                "body": "日中間の貿易実務だけでなく、市場調査から製品のオリジナル開発（OEM）まで、お客様のビジネス拡大をトータルにサポートいたします。",
                "icon": "clipboard2-data"
            },
        ], ensure_ascii=False)

        home.strengths_json = json.dumps([
            {
                "title": "独自のネットワーク",
                "body": "中国現地の工場やサプライヤーと直接提携し、迅速かつ安定した供給ルートを確保。",
                "icon": "diagram-3-fill"
            },
            {
                "title": "厳格な品質管理",
                "body": "日本の基準に合わせた厳しい品質チェックを、現地と国内の両方で実施。安心して選べる品質を守ります。",
                "icon": "shield-check"
            },
            {
                "title": "柔軟な対応力",
                "body": "小ロットの輸入から大規模なOEM開発まで、企業規模を問わず柔軟に対応します。",
                "icon": "arrows-move"
            },
        ], ensure_ascii=False)
        home.contact_examples_json = json.dumps([
            "日本向け：カーアクセサリー／機能パーツの輸入（小ロット〜）",
            "中国向け：Made in Japan用品の輸出・販路開拓",
            "OEM：仕様策定、パッケージ、品質基準、検品設計",
            "貿易実務：通関・輸送手配・納期管理・リスク整理",
        ], ensure_ascii=False)

        db.add(home)
        db.commit()
        db.refresh(home)
    return home


def update_home(db: Session, payload: HomeUpdate) -> HomePage:
    """更新首页数据"""
    home = get_or_create_home(db)

    # 只更新提供的字段（exclude_unset=True）
    # model_dump() 后 services/strengths 已是 list of dict，直接 json.dumps 即可
    for k, v in payload.model_dump(exclude_unset=True).items():
        if k == "services" and v is not None:
            try:
                home.services_json = json.dumps(v, ensure_ascii=False)
            except Exception as e:
                raise ValueError(f"Invalid services data: {e}")
        elif k == "strengths" and v is not None:
            try:
                home.strengths_json = json.dumps(v, ensure_ascii=False)
            except Exception as e:
                raise ValueError(f"Invalid strengths data: {e}")
        elif k == "hero_stats" and v is not None:
            try:
                home.hero_stats_json = json.dumps(v, ensure_ascii=False)
            except Exception as e:
                raise ValueError(f"Invalid hero stats data: {e}")
        elif k == "concept_points" and v is not None:
            try:
                home.concept_points_json = json.dumps(v, ensure_ascii=False)
            except Exception as e:
                raise ValueError(f"Invalid concept points data: {e}")
        elif k == "contact_examples" and v is not None:
            try:
                home.contact_examples_json = json.dumps(v, ensure_ascii=False)
            except Exception as e:
                raise ValueError(f"Invalid contact examples data: {e}")
        else:
            setattr(home, k, v)

    db.commit()
    db.refresh(home)
    return home


def list_news(db: Session) -> list[News]:
    return db.query(News).order_by(News.created_at.desc()).all()


def list_published_news(db: Session) -> list[News]:
    return (
        db.query(News)
        .filter(News.is_published.is_(True))
        .order_by(News.created_at.desc())
        .all()
    )


def get_news(db: Session, news_id: int) -> News | None:
    return db.query(News).filter(News.id == news_id).first()


def create_news(
    db: Session,
    title: str,
    body: str,
    image_path: str = "",
    file_path: str = "",
    is_published: bool = False,
) -> News:
    item = News(
        title=title.strip(),
        body=body or "",
        image_path=image_path or "",
        file_path=file_path or "",
        is_published=is_published,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_news(
    db: Session,
    news_id: int,
    title: str,
    body: str,
    image_path: str | None = None,
    file_path: str | None = None,
    is_published: bool = False,
) -> News | None:
    item = get_news(db, news_id)
    if not item:
        return None
    item.title = title.strip()
    item.body = body or ""
    if image_path is not None:
        item.image_path = image_path
    if file_path is not None:
        item.file_path = file_path
    item.is_published = is_published
    db.commit()
    db.refresh(item)
    return item


def delete_news(db: Session, news_id: int) -> bool:
    item = get_news(db, news_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
