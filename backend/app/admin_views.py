"""
后台管理视图：登录、登出、内容编辑
"""
import json
import shutil
import uuid
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Type, Optional
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .db import get_db
from .crud import get_or_create_home, update_home, list_news, create_news, update_news, delete_news
from .github_storage import github_enabled, upload_to_github
from .auth import ADMIN_USER, ADMIN_PASS_HASH, verify_password, create_session_token, is_logged_in
from .schemas import HomeUpdate, ServiceItem, StrengthItem, HeroStatItem, ConceptPointItem

router = APIRouter()


def _parse_services(services_json: str) -> list:
    """将 JSON 字符串解析为 ServiceItem 列表，缺字段补空字符串"""
    raw = json.loads(services_json) if services_json.strip() else []
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        detail_images_raw = item.get("detail_images") or []
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

        detail_files_raw = item.get("detail_files") or []
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
                    file_url = line
                    file_name = Path(urlparse(file_url).path).name or "文件"
                if file_url:
                    detail_files.append({"name": file_name or "文件", "url": file_url})
        elif isinstance(detail_files_raw, list):
            for row in detail_files_raw:
                if isinstance(row, dict):
                    file_url = str(row.get("url") or "").strip()
                    file_name = str(row.get("name") or "").strip()
                else:
                    file_url = str(row).strip()
                    file_name = Path(urlparse(file_url).path).name or "文件"
                if file_url:
                    detail_files.append({"name": file_name or "文件", "url": file_url})

        out.append(ServiceItem(
            title=item.get("title") or "",
            body=item.get("body") or "",
            icon=item.get("icon"),
            detail_body=item.get("detail_body") or "",
            detail_images=detail_images,
            detail_files=detail_files,
        ))
    return out


def _parse_strengths(strengths_json: str) -> list:
    """将 JSON 字符串解析为 StrengthItem 列表"""
    raw = json.loads(strengths_json) if strengths_json.strip() else []
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(StrengthItem(
            title=item.get("title") or "",
            body=item.get("body") or "",
            icon=item.get("icon"),
        ))
    return out


def _parse_hero_stats(stats_json: str) -> list:
    """将 JSON 字符串解析为 HeroStatItem 列表"""
    raw = json.loads(stats_json) if stats_json.strip() else []
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            value = int(item.get("value") or 0)
        except Exception:
            value = 0
        out.append(HeroStatItem(
            value=value,
            suffix=item.get("suffix") or "",
            label=item.get("label") or "",
        ))
    return out


def _parse_concept_points(points_json: str) -> list:
    """将 JSON 字符串解析为 ConceptPointItem 列表"""
    raw = json.loads(points_json) if points_json.strip() else []
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append(ConceptPointItem(
            label=item.get("label") or "",
            body=item.get("body") or "",
        ))
    return out


def _parse_contact_examples(examples_json: str) -> list:
    """将 JSON 字符串解析为字符串列表"""
    raw = json.loads(examples_json) if examples_json.strip() else []
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append(item)
    return out
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_BASE = Path(__file__).resolve().parents[2] / "uploads" / "news"
SERVICE_IMAGES_UPLOAD_BASE = Path(__file__).resolve().parents[2] / "uploads" / "services" / "images"
SERVICE_FILES_UPLOAD_BASE = Path(__file__).resolve().parents[2] / "uploads" / "services" / "files"
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _save_local_upload(upload: UploadFile | None) -> str:
    if not upload or not upload.filename:
        return ""
    ext = Path(upload.filename).suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    UPLOAD_BASE.mkdir(parents=True, exist_ok=True)
    target = UPLOAD_BASE / filename
    with target.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return f"/static/uploads/news/{filename}"


def _store_upload(upload: UploadFile | None) -> str:
    if not upload or not upload.filename:
        return ""
    if github_enabled():
        return upload_to_github(upload, folder="news")
    return _save_local_upload(upload)


def _save_local_service_upload(upload: UploadFile, kind: str) -> dict:
    ext = Path(upload.filename or "").suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    if kind == "image":
        base = SERVICE_IMAGES_UPLOAD_BASE
        url_prefix = "/static/uploads/services/images"
    else:
        base = SERVICE_FILES_UPLOAD_BASE
        url_prefix = "/static/uploads/services/files"

    base.mkdir(parents=True, exist_ok=True)
    target = base / filename
    with target.open("wb") as f:
        shutil.copyfileobj(upload.file, f)

    return {
        "name": upload.filename or filename,
        "url": f"{url_prefix}/{filename}",
    }


def _store_service_upload(upload: UploadFile, kind: str) -> dict:
    if github_enabled():
        folder = "services/images" if kind == "image" else "services/files"
        return {
            "name": upload.filename or "文件",
            "url": upload_to_github(upload, folder=folder),
        }
    return _save_local_service_upload(upload, kind)


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@router.post("/admin/login")
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """处理登录请求"""
    # 验证用户名和密码
    if username == ADMIN_USER and verify_password(password, ADMIN_PASS_HASH):
        resp = RedirectResponse(url="/admin", status_code=302)
        resp.set_cookie(
            "eiho_session",
            create_session_token(username),
            httponly=True,
            samesite="lax",
            secure=False  # 生产环境 HTTPS 时设为 True
        )
        return resp
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "ログイン失敗：ユーザー名/パスワードが違います。"}
    )


@router.get("/admin/logout")
def admin_logout():
    """登出"""
    resp = RedirectResponse(url="/admin/login", status_code=302)
    resp.delete_cookie("eiho_session")
    return resp


@router.post("/admin/services/upload")
def admin_upload_service_assets(
    request: Request,
    kind: str = Form(...),
    files: List[UploadFile] = File(...),
):
    """上传服务详情页资源（图片/文件）"""
    if not is_logged_in(request):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    normalized_kind = (kind or "").strip().lower()
    if normalized_kind not in {"image", "file"}:
        return JSONResponse(status_code=400, content={"detail": "Invalid upload kind"})

    if not files:
        return JSONResponse(status_code=400, content={"detail": "No files uploaded"})

    uploaded = []
    for upload in files:
        if not upload or not upload.filename:
            continue
        if normalized_kind == "image":
            content_type = (upload.content_type or "").lower()
            if not content_type.startswith("image/"):
                continue
        uploaded.append(_store_service_upload(upload, normalized_kind))

    if not uploaded:
        return JSONResponse(status_code=400, content={"detail": "No valid files uploaded"})
    return {"ok": True, "items": uploaded}


@router.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db)):
    """后台管理主页（需要登录）"""
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    try:
        home = get_or_create_home(db)
        return templates.TemplateResponse("admin_home.html", {
            "request": request,
            "home": home,
            "services": _parse_services(home.services_json or "[]"),
            "strengths": _parse_strengths(home.strengths_json or "[]"),
            "hero_stats": _parse_hero_stats(home.hero_stats_json or "[]"),
            "concept_points": _parse_concept_points(home.concept_points_json or "[]"),
            "contact_examples": _parse_contact_examples(home.contact_examples_json or "[]"),
            "news_items": list_news(db),
        })
    except Exception as e:
        return templates.TemplateResponse(
            "admin_home.html",
            {
                "request": request,
                "home": None,
                "error": f"データの読み込みに失敗しました: {e}"
            },
            status_code=500
        )


@router.post("/admin/save")
def admin_save(
    request: Request,
    db: Session = Depends(get_db),
    nav_brand_text: str = Form(""),
    nav_top_text: str = Form(""),
    nav_concept_text: str = Form(""),
    nav_news_text: str = Form(""),
    nav_services_text: str = Form(""),
    nav_strengths_text: str = Form(""),
    nav_profile_text: str = Form(""),
    nav_cta_text: str = Form(""),
    hero_kicker: str = Form(""),
    hero_title: str = Form(""),
    hero_subtitle: str = Form(""),
    hero_bg_image: str = Form(""),
    hero_primary_cta: str = Form(""),
    hero_secondary_cta: str = Form(""),
    hero_stat_value: List[str] = Form([]),
    hero_stat_suffix: List[str] = Form([]),
    hero_stat_label: List[str] = Form([]),
    concept_title: str = Form(""),
    concept_subtitle: str = Form(""),
    concept_point_label: List[str] = Form([]),
    concept_point_body: List[str] = Form([]),
    mission_title: str = Form(""),
    mission_body: str = Form(""),
    vision_title: str = Form(""),
    vision_body: str = Form(""),
    services_section_title: str = Form(""),
    services_section_subtitle: str = Form(""),
    strengths_section_title: str = Form(""),
    strengths_section_subtitle: str = Form(""),
    profile_title: str = Form(""),
    profile_subtitle: str = Form(""),
    company_name: str = Form(""),
    address: str = Form(""),
    representative: str = Form(""),
    established: str = Form(""),
    business_desc: str = Form(""),
    clients: str = Form(""),
    cta_title: str = Form(""),
    cta_subtitle: str = Form(""),
    cta_button_text: str = Form(""),
    cta_phone_text: str = Form(""),
    contact_form_title: str = Form(""),
    contact_form_note: str = Form(""),
    contact_examples_title: str = Form(""),
    contact_example_text: List[str] = Form([]),
    access_title: str = Form(""),
    access_address: str = Form(""),
    footer_copyright: str = Form(""),
    footer_link_top: str = Form(""),
    footer_link_services: str = Form(""),
    footer_link_profile: str = Form(""),
    services_title: List[str] = Form([]),
    services_body: List[str] = Form([]),
    services_icon: List[str] = Form([]),
    services_detail_body: List[str] = Form([]),
    services_detail_images: List[str] = Form([]),
    services_detail_files: List[str] = Form([]),
    strengths_title: List[str] = Form([]),
    strengths_body: List[str] = Form([]),
    strengths_icon: List[str] = Form([]),
):
    """保存首页数据（需要登录）"""
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    def _build_items(titles: List[str], bodies: List[str], icons: List[str], cls: Type) -> list:
        items = []
        max_len = max(len(titles), len(bodies), len(icons), 0)
        for i in range(max_len):
            title = titles[i].strip() if i < len(titles) else ""
            body = bodies[i].strip() if i < len(bodies) else ""
            icon = icons[i].strip() if i < len(icons) else ""
            if not (title or body or icon):
                continue
            items.append(cls(title=title, body=body, icon=icon or None))
        return items

    def _build_services(
        titles: List[str],
        bodies: List[str],
        icons: List[str],
        detail_bodies: List[str],
        detail_images_values: List[str],
        detail_files_values: List[str],
    ) -> list:
        items = []
        max_len = max(
            len(titles),
            len(bodies),
            len(icons),
            len(detail_bodies),
            len(detail_images_values),
            len(detail_files_values),
            0,
        )
        for i in range(max_len):
            title = titles[i].strip() if i < len(titles) else ""
            body = bodies[i].strip() if i < len(bodies) else ""
            icon = icons[i].strip() if i < len(icons) else ""
            detail_body = detail_bodies[i].strip() if i < len(detail_bodies) else ""
            detail_images_raw = detail_images_values[i] if i < len(detail_images_values) else ""
            detail_files_raw = detail_files_values[i] if i < len(detail_files_values) else ""

            detail_images = [
                line.strip()
                for line in str(detail_images_raw).replace("，", ",").replace(",", "\n").splitlines()
                if line.strip()
            ]

            detail_files = []
            for line in str(detail_files_raw).splitlines():
                line = line.strip()
                if not line:
                    continue
                if "|" in line:
                    file_name, file_url = line.split("|", 1)
                    file_name = file_name.strip()
                    file_url = file_url.strip()
                else:
                    file_url = line
                    file_name = Path(urlparse(file_url).path).name or "文件"
                if file_url:
                    detail_files.append({"name": file_name or "文件", "url": file_url})

            if not (title or body or icon or detail_body or detail_images or detail_files):
                continue

            items.append(ServiceItem(
                title=title,
                body=body,
                icon=icon or None,
                detail_body=detail_body or None,
                detail_images=detail_images,
                detail_files=detail_files,
            ))
        return items

    def _build_hero_stats(values: List[str], suffixes: List[str], labels: List[str]) -> list:
        items = []
        max_len = max(len(values), len(suffixes), len(labels), 0)
        for i in range(max_len):
            value_raw = values[i].strip() if i < len(values) else ""
            suffix = suffixes[i].strip() if i < len(suffixes) else ""
            label = labels[i].strip() if i < len(labels) else ""
            if not (value_raw or suffix or label):
                continue
            try:
                value = int(value_raw) if value_raw else 0
            except Exception:
                value = 0
            items.append(HeroStatItem(value=value, suffix=suffix, label=label))
        return items

    def _build_concept_points(labels: List[str], bodies: List[str]) -> list:
        items = []
        max_len = max(len(labels), len(bodies), 0)
        for i in range(max_len):
            label = labels[i].strip() if i < len(labels) else ""
            body = bodies[i].strip() if i < len(bodies) else ""
            if not (label or body):
                continue
            items.append(ConceptPointItem(label=label, body=body))
        return items

    def _build_simple_list(values: List[str]) -> list:
        return [v.strip() for v in values if isinstance(v, str) and v.strip()]

    def _clean(value: str) -> Optional[str]:
        return value.strip() if value and value.strip() else None

    services_list = _build_services(
        services_title,
        services_body,
        services_icon,
        services_detail_body,
        services_detail_images,
        services_detail_files,
    )
    strengths_list = _build_items(strengths_title, strengths_body, strengths_icon, StrengthItem)
    hero_stats_list = _build_hero_stats(hero_stat_value, hero_stat_suffix, hero_stat_label)
    concept_points_list = _build_concept_points(concept_point_label, concept_point_body)
    contact_examples_list = _build_simple_list(contact_example_text)

    try:
        # 构建更新数据（所有字段都传，空字符串也会写入数据库）
        update_data = HomeUpdate(
            nav_brand_text=_clean(nav_brand_text),
            nav_top_text=_clean(nav_top_text),
            nav_concept_text=_clean(nav_concept_text),
            nav_news_text=_clean(nav_news_text),
            nav_services_text=_clean(nav_services_text),
            nav_strengths_text=_clean(nav_strengths_text),
            nav_profile_text=_clean(nav_profile_text),
            nav_cta_text=_clean(nav_cta_text),
            hero_kicker=_clean(hero_kicker),
            hero_title=_clean(hero_title),
            hero_subtitle=_clean(hero_subtitle),
            hero_bg_image=_clean(hero_bg_image),
            hero_primary_cta=_clean(hero_primary_cta),
            hero_secondary_cta=_clean(hero_secondary_cta),
            hero_stats=hero_stats_list,
            concept_title=_clean(concept_title),
            concept_subtitle=_clean(concept_subtitle),
            concept_points=concept_points_list,
            mission_title=_clean(mission_title),
            mission_body=_clean(mission_body),
            vision_title=_clean(vision_title),
            vision_body=_clean(vision_body),
            services_section_title=_clean(services_section_title),
            services_section_subtitle=_clean(services_section_subtitle),
            strengths_section_title=_clean(strengths_section_title),
            strengths_section_subtitle=_clean(strengths_section_subtitle),
            profile_title=_clean(profile_title),
            profile_subtitle=_clean(profile_subtitle),
            company_name=_clean(company_name),
            address=_clean(address),
            representative=_clean(representative),
            established=_clean(established),
            business_desc=_clean(business_desc),
            clients=_clean(clients),
            cta_title=_clean(cta_title),
            cta_subtitle=_clean(cta_subtitle),
            cta_button_text=_clean(cta_button_text),
            cta_phone_text=_clean(cta_phone_text),
            contact_form_title=_clean(contact_form_title),
            contact_form_note=_clean(contact_form_note),
            contact_examples_title=_clean(contact_examples_title),
            contact_examples=contact_examples_list,
            access_title=_clean(access_title),
            access_address=_clean(access_address),
            footer_copyright=_clean(footer_copyright),
            footer_link_top=_clean(footer_link_top),
            footer_link_services=_clean(footer_link_services),
            footer_link_profile=_clean(footer_link_profile),
            services=services_list,
            strengths=strengths_list,
        )
        update_home(db, update_data)
        return RedirectResponse(url="/admin?success=1", status_code=302)
    except Exception as e:
        return RedirectResponse(url="/admin?error=save_failed", status_code=302)


@router.post("/admin/news/create")
def admin_create_news(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(""),
    body: str = Form(""),
    is_published: Optional[str] = Form(None),
    image: UploadFile | None = File(None),
    attachment: UploadFile | None = File(None),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    if not title.strip():
        return RedirectResponse(url="/admin?error=news_title_required", status_code=302)
    image_path = _store_upload(image)
    file_path = _store_upload(attachment)
    create_news(
        db,
        title=title,
        body=body,
        image_path=image_path,
        file_path=file_path,
        is_published=bool(is_published),
    )
    return RedirectResponse(url="/admin?news=created", status_code=302)


@router.post("/admin/news/update/{news_id}")
def admin_update_news(
    news_id: int,
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(""),
    body: str = Form(""),
    is_published: Optional[str] = Form(None),
    image: UploadFile | None = File(None),
    attachment: UploadFile | None = File(None),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    if not title.strip():
        return RedirectResponse(url="/admin?error=news_title_required", status_code=302)
    image_path = _store_upload(image) if image and image.filename else None
    file_path = _store_upload(attachment) if attachment and attachment.filename else None
    update_news(
        db,
        news_id=news_id,
        title=title,
        body=body,
        image_path=image_path,
        file_path=file_path,
        is_published=bool(is_published),
    )
    return RedirectResponse(url="/admin?news=updated", status_code=302)


@router.post("/admin/news/delete/{news_id}")
def admin_delete_news(
    news_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    delete_news(db, news_id)
    return RedirectResponse(url="/admin?news=deleted", status_code=302)
