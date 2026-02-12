"""
FastAPI 主应用：路由、中间件、静态文件托管
"""
import json
import logging
from pathlib import Path
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from .db import (
    Base,
    engine,
    get_db,
    ensure_homepage_nav_columns,
    ensure_news_asset_columns,
    ensure_homepage_profile_rows_column,
    ensure_homepage_value_columns,
)
from .crud import (
    get_or_create_home,
    update_home,
    list_published_news,
    list_published_news_page,
    get_news,
)
from .schemas import HomePublic, HomeUpdate, ContactRequest, NewsPublic
from .admin_views import router as admin_router
from .auth import is_logged_in
from .mail import send_contact_email

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]  # 指向 web_page_company 项目根目录
ENV_PATH = BASE_DIR / "backend" / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=str(ENV_PATH))
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# 创建数据库表
Base.metadata.create_all(bind=engine)
ensure_homepage_nav_columns()
ensure_news_asset_columns()
ensure_homepage_profile_rows_column()
ensure_homepage_value_columns()

# 创建 FastAPI 应用
app = FastAPI(
    title="EIHO Admin Backend",
    description="株式会社衛宝（EIHO）官网后台管理系统",
    version="1.0.0"
)

# CORS 中间件（生产环境建议限制域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议写死域名，如 ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册后台管理路由
app.include_router(admin_router)

# 静态资源挂载（css/js/images），挂载项目根目录
# 访问 /static/css/main.css 会映射到 web_page_company/css/main.css
try:
    app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")
except Exception as e:
    logger.warning(f"Failed to mount static files: {e}")


@app.get("/")
def serve_frontend():
    """访问 http://127.0.0.1:8000/ 返回前端主页"""
    html_path = BASE_DIR / "test.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Frontend file not found")
    return FileResponse(str(html_path))


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "EIHO Backend"}


@app.get("/api/public/home", response_model=HomePublic)
def public_home(db: Session = Depends(get_db)):
    """公开 API：获取首页数据"""
    try:
        home = get_or_create_home(db)
        profile_rows_raw = json.loads(home.profile_rows_json or "[]")
        if isinstance(profile_rows_raw, list):
            profile_rows = [
                {
                    "label": str(row.get("label") or "").strip(),
                    "value": str(row.get("value") or "").strip(),
                }
                for row in profile_rows_raw
                if isinstance(row, dict) and (str(row.get("label") or "").strip() or str(row.get("value") or "").strip())
            ]
        else:
            profile_rows = []
        if not profile_rows:
            profile_rows = [
                {"label": "名称", "value": home.company_name or ""},
                {"label": "所在地", "value": home.address or ""},
                {"label": "代表者", "value": home.representative or ""},
                {"label": "設立", "value": home.established or ""},
                {"label": "事業内容", "value": home.business_desc or ""},
                {"label": "主要取引先", "value": home.clients or ""},
            ]
        return HomePublic(
            nav_brand_text=home.nav_brand_text or "",
            nav_top_text=home.nav_top_text or "",
            nav_concept_text=home.nav_concept_text or "メッセージ",
            nav_news_text=home.nav_news_text or "ニュース",
            nav_services_text=home.nav_services_text or "",
            nav_strengths_text=home.nav_strengths_text or "",
            nav_profile_text=home.nav_profile_text or "",
            nav_cta_text=home.nav_cta_text or "",
            hero_kicker=home.hero_kicker or "",
            hero_title=home.hero_title or "",
            hero_subtitle=home.hero_subtitle or "",
            hero_bg_image=home.hero_bg_image or "",
            hero_primary_cta=home.hero_primary_cta or "",
            hero_secondary_cta=home.hero_secondary_cta or "",
            hero_stats=json.loads(home.hero_stats_json or "[]"),
            concept_title=home.concept_title or "",
            concept_subtitle=home.concept_subtitle or "",
            concept_points=json.loads(home.concept_points_json or "[]"),
            mission_title=home.mission_title or "",
            mission_body=home.mission_body or "",
            vision_title=home.vision_title or "",
            vision_body=home.vision_body or "",
            value_title=home.value_title or "",
            value_body=home.value_body or "",
            services_section_title=home.services_section_title or "",
            services_section_subtitle=home.services_section_subtitle or "",
            strengths_section_title=home.strengths_section_title or "",
            strengths_section_subtitle=home.strengths_section_subtitle or "",
            services=json.loads(home.services_json or "[]"),
            strengths=json.loads(home.strengths_json or "[]"),
            profile_title=home.profile_title or "",
            profile_subtitle=home.profile_subtitle or "",
            company_name=home.company_name or "",
            address=home.address or "",
            representative=home.representative or "",
            established=home.established or "",
            business_desc=home.business_desc or "",
            clients=home.clients or "",
            profile_rows=profile_rows,
            cta_title=home.cta_title or "",
            cta_subtitle=home.cta_subtitle or "",
            cta_button_text=home.cta_button_text or "",
            cta_phone_text=home.cta_phone_text or "",
            contact_form_title=home.contact_form_title or "",
            contact_form_note=home.contact_form_note or "",
            contact_examples_title=home.contact_examples_title or "",
            contact_examples=json.loads(home.contact_examples_json or "[]"),
            access_title=home.access_title or "",
            access_address=home.access_address or "",
            footer_copyright=home.footer_copyright or "",
            footer_link_top=home.footer_link_top or "",
            footer_link_services=home.footer_link_services or "",
            footer_link_profile=home.footer_link_profile or "",
        )
    except Exception as e:
        logger.error(f"Error fetching home data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch home data")


@app.get("/api/public/news", response_model=list[NewsPublic])
def public_news(db: Session = Depends(get_db), limit: int = 8):
    """公开 API：获取已发布新闻列表（仅标题与链接）"""
    safe_limit = max(1, min(int(limit or 8), 100))
    items = list_published_news(db)[:safe_limit]
    return [
        NewsPublic(id=item.id, title=item.title, url=f"/news/{item.id}")
        for item in items
    ]


@app.get("/news", response_class=HTMLResponse)
def news_list_page(
    request: Request,
    db: Session = Depends(get_db),
    q: str = "",
    page: int = 1,
    sort: str = "latest",
):
    """新闻列表页：支持搜索与分页（每页 10 条）。"""
    page_size = 10
    safe_page = max(int(page or 1), 1)
    keyword = (q or "").strip()
    safe_sort = (sort or "latest").strip().lower()
    if safe_sort not in {"latest", "oldest"}:
        safe_sort = "latest"

    items, total = list_published_news_page(
        db=db,
        page=safe_page,
        page_size=page_size,
        keyword=keyword,
        sort=safe_sort,
    )
    total_pages = max((total + page_size - 1) // page_size, 1)
    current_page = min(safe_page, total_pages)
    if current_page != safe_page:
        items, total = list_published_news_page(
            db=db,
            page=current_page,
            page_size=page_size,
            keyword=keyword,
            sort=safe_sort,
        )

    page_numbers = list(range(max(1, current_page - 2), min(total_pages, current_page + 2) + 1))
    return templates.TemplateResponse(
        "news_list.html",
        {
            "request": request,
            "news_items": items,
            "keyword": keyword,
            "sort": safe_sort,
            "page": current_page,
            "total_pages": total_pages,
            "total_items": total,
            "page_numbers": page_numbers,
        },
    )


@app.put("/api/admin/home")
def admin_update_home(payload: HomeUpdate, request: Request, db: Session = Depends(get_db)):
    """后台 API：更新首页数据（需要登录）"""
    if not is_logged_in(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        home = update_home(db, payload)
        return {"ok": True, "updated_at": str(home.updated_at)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating home data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update home data")


@app.post("/api/contact")
def submit_contact(payload: ContactRequest):
    """联系表单：发送邮件给管理员"""
    try:
        send_contact_email(
            name=payload.name,
            company=payload.company,
            email=payload.email,
            message=payload.message,
        )
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send contact email: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send email")


@app.get("/news/{news_id}", response_class=HTMLResponse)
def news_detail(news_id: int, request: Request, db: Session = Depends(get_db)):
    """新闻详情页"""
    item = get_news(db, news_id)
    if not item or not item.is_published:
        raise HTTPException(status_code=404, detail="News not found")

    image_list = []
    try:
        parsed_images = json.loads(item.image_paths_json or "[]")
    except Exception:
        parsed_images = []
    if isinstance(parsed_images, list):
        for row in parsed_images:
            if isinstance(row, dict):
                url = str(row.get("url") or row.get("src") or "").strip()
            else:
                url = str(row).strip()
            if url:
                image_list.append(url)
    if not image_list and item.image_path:
        image_list = [item.image_path]

    file_list = []
    try:
        parsed_files = json.loads(item.file_paths_json or "[]")
    except Exception:
        parsed_files = []
    if isinstance(parsed_files, list):
        for row in parsed_files:
            if isinstance(row, dict):
                url = str(row.get("url") or "").strip()
                name = str(row.get("name") or "").strip()
            else:
                url = str(row).strip()
                name = "文件"
            if url:
                file_list.append({"name": name or "文件", "url": url})
    if not file_list and item.file_path:
        file_list = [{"name": "附件", "url": item.file_path}]

    return templates.TemplateResponse(
        "news_detail.html",
        {"request": request, "news": item, "news_images": image_list, "news_files": file_list}
    )


@app.get("/services/{service_index}", response_class=HTMLResponse)
def service_detail(service_index: int, request: Request, db: Session = Depends(get_db)):
    """服务详情页"""
    home = get_or_create_home(db)
    try:
        services = json.loads(home.services_json or "[]")
    except Exception:
        services = []

    if not isinstance(services, list) or len(services) == 0:
        # 兜底：当数据库里 services 为空/损坏时，仍可打开默认服务详情页
        services = [
            {
                "title": "輸入事業（Import）",
                "body": "中国の先進的な製造ネットワークを駆使し、最新のカーアクセサリーや機能パーツをいち早く日本市場へ導入。徹底した検品体制で、コストパフォーマンスと品質を両立させた製品を提供します。",
                "detail_body": "",
                "detail_images": [],
                "detail_files": [],
            },
            {
                "title": "輸出事業（Export）",
                "body": "信頼の「Made in Japan」ブランドの自動車用品・メンテナンス用品を中国市場へ展開。現地のニーズを的確に捉えたマーケティングにより、日本の優れた技術を世界へ広めます。",
                "detail_body": "",
                "detail_images": [],
                "detail_files": [],
            },
            {
                "title": "コンサル・OEM受託",
                "body": "日中間の貿易実務だけでなく、市場調査から製品のオリジナル開発（OEM）まで、お客様のビジネス拡大をトータルにサポートいたします。",
                "detail_body": "",
                "detail_images": [],
                "detail_files": [],
            },
        ]

    if service_index < 0 or service_index >= len(services):
        raise HTTPException(status_code=404, detail="Service not found")

    raw = services[service_index]
    if not isinstance(raw, dict):
        raise HTTPException(status_code=404, detail="Service not found")

    detail_images_raw = raw.get("detail_images") or []
    if isinstance(detail_images_raw, str):
        detail_images = [
            line.strip()
            for line in detail_images_raw.replace("，", ",").replace(",", "\n").splitlines()
            if line.strip()
        ]
    elif isinstance(detail_images_raw, list):
        detail_images = []
        for line in detail_images_raw:
            if isinstance(line, dict):
                value = str(line.get("url") or line.get("src") or "").strip()
            else:
                value = str(line).strip()
            if value:
                detail_images.append(value)
    else:
        detail_images = []

    detail_files_raw = raw.get("detail_files") or []
    detail_files = []
    if isinstance(detail_files_raw, str):
        for line in detail_files_raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                file_name, file_url = line.split("|", 1)
                file_name = file_name.strip()
                file_url = file_url.strip()
            else:
                file_name = "文件"
                file_url = line
            if file_url:
                detail_files.append({"name": file_name or "文件", "url": file_url})
    elif isinstance(detail_files_raw, list):
        for row in detail_files_raw:
            if isinstance(row, dict):
                file_url = str(row.get("url") or "").strip()
                file_name = str(row.get("name") or "").strip()
            else:
                file_url = str(row).strip()
                file_name = "文件"
            if file_url:
                detail_files.append({"name": file_name or "文件", "url": file_url})

    service = {
        "title": str(raw.get("title") or ""),
        "body": str(raw.get("body") or ""),
        "detail_body": str(raw.get("detail_body") or ""),
        "detail_images": detail_images,
        "detail_files": detail_files,
    }
    return templates.TemplateResponse(
        "service_detail.html",
        {"request": request, "service": service, "service_index": service_index}
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """404 错误处理"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """500 错误处理"""
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
