/**
 * 从后台 /api/public/home 拉取首页数据，填充 hero 标题、副标题与事业内容列表。
 * 接口失败时保留 HTML 内静态内容。
 */
(async () => {
  try {
    const res = await fetch("/api/public/home");
    if (!res.ok) return;
    const data = await res.json();

    const setText = (selector, value) => {
      if (value === undefined || value === null) return;
      if (typeof value === "string" && value.trim() === "") return;
      const el = document.querySelector(selector);
      if (el) el.textContent = value;
    };

    const setMultilineText = (selector, value) => {
      if (value === undefined || value === null) return;
      if (typeof value === "string" && value.trim() === "") return;
      const el = document.querySelector(selector);
      if (!el) return;
      const lines = String(value)
        .split(/\r?\n/)
        .map(s => s.trim())
        .filter(Boolean);
      el.innerHTML = lines.map(line => escapeHtml(line)).join("<br>");
    };

    // Nav
    setText("#navBrandText", data.nav_brand_text);
    setText("#navTopText", data.nav_top_text);
    setText("#navConceptText", data.nav_concept_text);
    setText("#navNewsText", data.nav_news_text);
    setText("#navServicesText", data.nav_services_text);
    setText("#navStrengthsText", data.nav_strengths_text);
    setText("#navProfileText", data.nav_profile_text);
    setText("#navCtaText", data.nav_cta_text);

    // Hero
    setText("#heroKickerText", data.hero_kicker);
    const heroTitle = document.querySelector("#heroTitle");
    const heroSubtitle = document.querySelector("#heroSubtitle");
    if (data.hero_title && heroTitle) heroTitle.textContent = data.hero_title;
    if (data.hero_subtitle && heroSubtitle) {
      const lines = String(data.hero_subtitle).split(/\r?\n/);
      heroSubtitle.innerHTML = lines.map(line => escapeHtml(line)).join("<br>");
    }
    setText("#heroPrimaryCtaText", data.hero_primary_cta);
    setText("#heroSecondaryCtaText", data.hero_secondary_cta);

    // Hero 背景图（可选，支持最多 5 张，逗号/换行分隔）
    const heroSection = document.querySelector("[data-hero]");
    const heroSlides = Array.from(document.querySelectorAll("[data-hero-bg-slide]"));
    if (heroSection && heroSlides.length > 0 && data.hero_bg_image) {
      const bgImages = String(data.hero_bg_image)
        .split(/[\r\n,]+/)
        .map((item) => item.trim())
        .filter(Boolean);
      if (bgImages.length > 0) {
        heroSlides.forEach((slide, index) => {
          const imageUrl = bgImages[index % bgImages.length];
          slide.style.backgroundImage = `url("${imageUrl}")`;
        });
      }
    }

    const normalizeIcon = (icon, fallback) => {
      const value = icon || fallback || "";
      return value.startsWith("bi-") ? value : `bi-${value}`;
    };

    const heroStats = Array.isArray(data.hero_stats) ? data.hero_stats : [];
    const heroCardsWrap = document.querySelector(".hero-cards");
    if (heroCardsWrap && heroStats.length > 0) {
      heroCardsWrap.innerHTML = heroStats
        .map((stat) => {
          const value = Number.parseInt(stat?.value, 10);
          const safeValue = Number.isNaN(value) ? 0 : value;
          const suffix = escapeHtml(String(stat?.suffix || ""));
          const label = escapeHtml(String(stat?.label || ""));
          return `
<div class="hero-card">
  <div class="num"><span class="countup" data-to="${safeValue}">${safeValue}</span><span>${suffix}</span></div>
  <div class="label">${label}</div>
</div>`;
        })
        .join("");
    }

    // Concept / Mission / Vision
    setText("#conceptTitle", data.concept_title);
    setMultilineText("#conceptSubtitle", data.concept_subtitle);
    const conceptPoints = Array.isArray(data.concept_points) ? data.concept_points : [];
    conceptPoints.forEach((point, i) => {
      const label = point?.label ? `${point.label}${point.label.endsWith("：") ? "" : "："}` : "";
      setText(`#conceptPoint${i}Label`, label);
      setText(`#conceptPoint${i}Body`, point?.body);
    });
    setText("#missionTitle", data.mission_title);
    setMultilineText("#missionBody", data.mission_body);
    setText("#visionTitle", data.vision_title);
    setMultilineText("#visionBody", data.vision_body);

    // News list (separate API)
    const newsList = document.querySelector("#newsList");
    if (newsList) {
      try {
        const newsRes = await fetch("/api/public/news");
        if (newsRes.ok) {
          const newsData = await newsRes.json();
          if (Array.isArray(newsData) && newsData.length > 0) {
            newsList.innerHTML = newsData
              .map(item => {
                const title = escapeHtml(item.title || "");
                const url = item.url || "#";
                return `
<a class="news-card-link" href="${url}">
  <article class="news-card">
    <div class="news-card-title">${title}</div>
    <div class="news-card-meta">詳細を見る <i class="bi bi-arrow-right-short"></i></div>
  </article>
</a>`;
              })
              .join("");
          } else {
            newsList.innerHTML = `
<article class="news-card news-empty">
  <div class="news-card-title">現在、ニュースはありません。</div>
  <div class="news-card-meta">新しいお知らせが公開されると、ここに表示されます。</div>
</article>`;
          }
        }
      } catch (_) {
        /* ignore news errors */
      }
    }

    // Section headings
    setText("#servicesTitle", data.services_section_title);
    setMultilineText("#servicesSubtitle", data.services_section_subtitle);
    setText("#strengthsTitle", data.strengths_section_title);
    setMultilineText("#strengthsSubtitle", data.strengths_section_subtitle);

    const servicesWrap = document.querySelector("#servicesWrap");
    if (servicesWrap && Array.isArray(data.services) && data.services.length > 0) {
      const icons = ["bi-box-seam", "bi-truck", "bi-clipboard2-data"];
      const html = data.services
        .map((s, i) => {
          const icon = normalizeIcon(s.icon, icons[i % icons.length]);
          return `
  <div class="col-lg-4">
    <div class="card svc-card p-4">
      <div class="icon mb-3"><i class="bi ${icon}"></i></div>
      <h5 class="fw-bold">${escapeHtml(s.title || "")}</h5>
      <p class="text-secondary mb-0">${escapeHtml(s.body || "")}</p>
    </div>
  </div>`;
        })
        .join("");
      servicesWrap.innerHTML = html;
    }

    // Strengths 渲染
    const strengthsWrap = document.querySelector("#strengthsWrap");
    if (strengthsWrap && Array.isArray(data.strengths) && data.strengths.length > 0) {
      const icons = ["bi-diagram-3-fill", "bi-shield-check", "bi-arrows-move"];
      const html = data.strengths
        .map((s, i) => {
          const icon = normalizeIcon(s.icon, icons[i % icons.length]);
          return `
  <div class="col-lg-4">
    <div class="strength-item">
      <div class="d-flex align-items-center gap-2 mb-2">
        <i class="bi ${icon} fs-4 text-brand-2"></i>
        <h5 class="fw-bold mb-0">${escapeHtml(s.title || "")}</h5>
      </div>
      <p class="text-secondary mb-0">${escapeHtml(s.body || "")}</p>
    </div>
  </div>`;
        })
        .join("");
      strengthsWrap.innerHTML = html;
    }

    // Company Profile 渲染
    setText("#profileTitle", data.profile_title);
    setMultilineText("#profileSubtitle", data.profile_subtitle);
    const companyNameHead = document.querySelector("#companyNameHead");
    const companyName = document.querySelector("#companyName");
    const companyAddress = document.querySelector("#companyAddress");
    const companyRepresentative = document.querySelector("#companyRepresentative");
    const companyEstablished = document.querySelector("#companyEstablished");
    const businessDesc = document.querySelector("#businessDesc");
    const companyClients = document.querySelector("#companyClients");

    if (data.company_name) {
      if (companyNameHead) companyNameHead.textContent = data.company_name;
      if (companyName) companyName.textContent = data.company_name;
    }
    if (data.address && companyAddress) companyAddress.textContent = data.address;
    if (data.representative && companyRepresentative) companyRepresentative.textContent = data.representative;
    if (data.established && companyEstablished) companyEstablished.textContent = data.established;
    if (data.clients && companyClients) companyClients.textContent = data.clients;

    if (businessDesc && data.business_desc) {
      const lines = String(data.business_desc)
        .split(/\r?\n/)
        .map(s => s.trim())
        .filter(Boolean);
      businessDesc.innerHTML = lines
        .map(line => `<li>${escapeHtml(line)}</li>`)
        .join("") || `<li>${escapeHtml(data.business_desc)}</li>`;
    }

    // Contact / CTA
    setText("#ctaTitle", data.cta_title);
    setMultilineText("#ctaSubtitle", data.cta_subtitle);
    setText("#ctaButtonText", data.cta_button_text);
    setText("#ctaPhoneText", data.cta_phone_text);
    setText("#contactFormTitle", data.contact_form_title);
    setMultilineText("#contactFormNote", data.contact_form_note);
    setText("#contactExamplesTitle", data.contact_examples_title);
    setText("#accessTitle", data.access_title);
    setText("#accessAddress", data.access_address);

    const contactExamples = document.querySelector("#contactExamplesList");
    if (contactExamples && Array.isArray(data.contact_examples) && data.contact_examples.length > 0) {
      contactExamples.innerHTML = data.contact_examples
        .map(item => `<li class="mb-2">${escapeHtml(item)}</li>`)
        .join("");
    }

    // Footer
    setText("#footerCopyrightText", data.footer_copyright);
    setText("#footerLinkTop", data.footer_link_top);
    setText("#footerLinkServices", data.footer_link_services);
    setText("#footerLinkProfile", data.footer_link_profile);
  } catch (_) {
    /* 后台未开或跨域等：保留静态内容，不报错 */
  }
})();

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
