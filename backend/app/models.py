from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .db import Base

class HomePage(Base):
    __tablename__ = "homepage"

    id = Column(Integer, primary_key=True, index=True)

    # Nav
    nav_brand_text = Column(String(255), default="EIHO / 衛宝")
    nav_top_text = Column(String(100), default="トップ")
    nav_concept_text = Column(String(100), default="メッセージ")
    nav_news_text = Column(String(100), default="ニュース")
    nav_services_text = Column(String(100), default="事業内容")
    nav_strengths_text = Column(String(100), default="強み")
    nav_profile_text = Column(String(100), default="会社概要")
    nav_cta_text = Column("nav_contact_text", String(100), default="お問合わせ")

    # Hero / Top message
    hero_kicker = Column("hero_kicker_text", String(255), default="Japan × China | Automotive Trading")
    hero_title = Column(String(255), default="品質と情熱で、日中のカーライフを繋ぐ架け橋へ")
    hero_subtitle = Column(Text, default="")
    hero_bg_image = Column(String(500), default="")  # URL or local path
    hero_primary_cta = Column("hero_cta_primary_text", String(255), default="事業内容を見る")
    hero_secondary_cta = Column("hero_cta_secondary_text", String(255), default="会社概要")
    hero_stats_json = Column(Text, default="[]")

    # Concept
    concept_title = Column(String(255), default="メッセージ（コンセプト）")
    concept_subtitle = Column("concept_body", Text, default="")
    concept_points_json = Column(Text, default="[]")
    mission_title = Column(String(100), default="Mission")
    mission_body = Column(Text, default="")
    vision_title = Column(String(100), default="Vision")
    vision_body = Column(Text, default="")
    value_title = Column(String(100), default="Value")
    value_body = Column(Text, default="")

    # Section headings
    services_section_title = Column("services_title", String(255), default="事業内容（Our Services）")
    services_section_subtitle = Column("services_subtitle", Text, default="")
    strengths_section_title = Column("strengths_title", String(255), default="当社の強み（Why Choose Us?）")
    strengths_section_subtitle = Column("strengths_subtitle", Text, default="")

    # Services (store JSON-like string for quick start; later can normalize to separate tables)
    services_json = Column(Text, default="[]")

    # Strengths
    strengths_json = Column(Text, default="[]")

    # Company profile
    profile_title = Column(String(255), default="会社概要（Company Profile）")
    profile_subtitle = Column(Text, default="")
    profile_rows_json = Column(Text, default="[]")
    company_name = Column(String(255), default="株式会社 衛宝（EIHO Co., Ltd.）")
    address = Column(String(255), default="〒000-0000 [都道府県・住所を入力]")
    representative = Column(String(255), default="[代表者名を入力]")
    established = Column(String(255), default="[設立年・月を入力]")
    business_desc = Column(Text, default="自動車関連部品および自動車用品、カーアクセサリーの輸出入及び販売\n卸売\nコンサルティング・OEM受託（市場調査／製品開発支援）")
    clients = Column(Text, default="日本国内のカーショップ、中国国内の製造メーカー、各商社")

    # Contact / CTA
    cta_title = Column("contact_title", String(255), default="日中貿易・OEMのご相談はこちら")
    cta_subtitle = Column("contact_body", Text, default="小ロットのテスト導入から量産・仕様調整まで。まずは要件だけでもお聞かせください。")
    cta_button_text = Column("contact_button_text", String(255), default="メールで問い合わせ")
    cta_phone_text = Column("contact_phone_text", String(255), default="または：03-0000-0000（平日 9:00–18:00）")
    contact_form_title = Column(String(255), default="お問い合わせフォーム（ダミー）")
    contact_form_note = Column(Text, default="※このフォームはデモです（送信は行いません）。実運用ではバックエンド（例：Node/PHP/Django等）に接続してください。")
    contact_examples_title = Column(String(255), default="対応可能なご相談例")
    contact_examples_json = Column(Text, default="[]")
    access_title = Column(String(255), default="アクセス")
    access_address = Column(String(255), default="〒000-0000 [都道府県・住所を入力]")

    # Footer
    footer_copyright = Column("footer_text", String(255), default="EIHO Co., Ltd. All rights reserved.")
    footer_link_top = Column(String(100), default="TOP")
    footer_link_services = Column(String(100), default="Services")
    footer_link_profile = Column(String(100), default="Profile")

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, default="")
    image_path = Column(String(500), default="")
    file_path = Column(String(500), default="")
    image_paths_json = Column(Text, default="[]")
    file_paths_json = Column(Text, default="[]")
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
