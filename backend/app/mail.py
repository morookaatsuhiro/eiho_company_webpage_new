"""
SMTP 邮件发送工具
"""
from dataclasses import dataclass
import os
import smtplib
import ssl
from email.message import EmailMessage


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    username: str
    password: str
    use_tls: bool
    admin_email: str
    sender_email: str


def _parse_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError("SMTP_TLS must be a boolean-like value")


def load_smtp_config() -> SmtpConfig:
    host = os.getenv("SMTP_HOST", "").strip()
    port_raw = os.getenv("SMTP_PORT", "").strip()
    username = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASS", "").strip()
    admin_email = os.getenv("SMTP_ADMIN_EMAIL", "").strip()
    sender_email = os.getenv("SMTP_FROM", "").strip()
    use_tls = _parse_bool(os.getenv("SMTP_TLS"), default=True)

    missing = [key for key, value in {
        "SMTP_HOST": host,
        "SMTP_PORT": port_raw,
        "SMTP_USER": username,
        "SMTP_PASS": password,
        "SMTP_ADMIN_EMAIL": admin_email,
    }.items() if not value]
    if missing:
        raise ValueError(f"Missing SMTP configuration: {', '.join(missing)}")

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ValueError("SMTP_PORT must be an integer") from exc
    if port <= 0 or port > 65535:
        raise ValueError("SMTP_PORT must be between 1 and 65535")

    if not sender_email:
        sender_email = username

    return SmtpConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls,
        admin_email=admin_email,
        sender_email=sender_email,
    )


def send_contact_email(name: str, company: str | None, email: str, message: str) -> None:
    config = load_smtp_config()

    msg = EmailMessage()
    msg["Subject"] = f"[官网咨询] {name}"
    msg["From"] = config.sender_email
    msg["To"] = config.admin_email
    msg["Reply-To"] = email

    company_line = company.strip() if company else "（未填写）"
    body = "\n".join([
        "有新的官网咨询提交：",
        "",
        f"姓名：{name}",
        f"公司：{company_line}",
        f"邮箱：{email}",
        "内容：",
        message,
    ])
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(config.host, config.port, timeout=15) as server:
        if config.use_tls:
            server.starttls(context=context)
        server.login(config.username, config.password)
        server.send_message(msg)
