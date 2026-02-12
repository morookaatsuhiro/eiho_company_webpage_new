from pydantic import BaseModel
from typing import List, Optional, Any

class ServiceItem(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None

class StrengthItem(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None


class HeroStatItem(BaseModel):
    value: int
    suffix: str
    label: str


class ConceptPointItem(BaseModel):
    label: str
    body: str

class HomePublic(BaseModel):
    nav_brand_text: str
    nav_top_text: str
    nav_concept_text: str
    nav_news_text: str
    nav_services_text: str
    nav_strengths_text: str
    nav_profile_text: str
    nav_cta_text: str

    hero_kicker: str
    hero_title: str
    hero_subtitle: str
    hero_bg_image: str
    hero_primary_cta: str
    hero_secondary_cta: str
    hero_stats: List[HeroStatItem]

    concept_title: str
    concept_subtitle: str
    concept_points: List[ConceptPointItem]
    mission_title: str
    mission_body: str
    vision_title: str
    vision_body: str

    services_section_title: str
    services_section_subtitle: str
    strengths_section_title: str
    strengths_section_subtitle: str

    services: List[ServiceItem]
    strengths: List[StrengthItem]

    profile_title: str
    profile_subtitle: str
    company_name: str
    address: str
    representative: str
    established: str
    business_desc: str
    clients: str

    cta_title: str
    cta_subtitle: str
    cta_button_text: str
    cta_phone_text: str
    contact_form_title: str
    contact_form_note: str
    contact_examples_title: str
    contact_examples: List[str]
    access_title: str
    access_address: str

    footer_copyright: str
    footer_link_top: str
    footer_link_services: str
    footer_link_profile: str

class HomeUpdate(BaseModel):
    nav_brand_text: Optional[str] = None
    nav_top_text: Optional[str] = None
    nav_concept_text: Optional[str] = None
    nav_news_text: Optional[str] = None
    nav_services_text: Optional[str] = None
    nav_strengths_text: Optional[str] = None
    nav_profile_text: Optional[str] = None
    nav_cta_text: Optional[str] = None

    hero_kicker: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_bg_image: Optional[str] = None
    hero_primary_cta: Optional[str] = None
    hero_secondary_cta: Optional[str] = None
    hero_stats: Optional[List[HeroStatItem]] = None

    concept_title: Optional[str] = None
    concept_subtitle: Optional[str] = None
    concept_points: Optional[List[ConceptPointItem]] = None
    mission_title: Optional[str] = None
    mission_body: Optional[str] = None
    vision_title: Optional[str] = None
    vision_body: Optional[str] = None

    services_section_title: Optional[str] = None
    services_section_subtitle: Optional[str] = None
    strengths_section_title: Optional[str] = None
    strengths_section_subtitle: Optional[str] = None

    services: Optional[List[ServiceItem]] = None
    strengths: Optional[List[StrengthItem]] = None

    profile_title: Optional[str] = None
    profile_subtitle: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    representative: Optional[str] = None
    established: Optional[str] = None
    business_desc: Optional[str] = None
    clients: Optional[str] = None

    cta_title: Optional[str] = None
    cta_subtitle: Optional[str] = None
    cta_button_text: Optional[str] = None
    cta_phone_text: Optional[str] = None
    contact_form_title: Optional[str] = None
    contact_form_note: Optional[str] = None
    contact_examples_title: Optional[str] = None
    contact_examples: Optional[List[str]] = None
    access_title: Optional[str] = None
    access_address: Optional[str] = None

    footer_copyright: Optional[str] = None
    footer_link_top: Optional[str] = None
    footer_link_services: Optional[str] = None
    footer_link_profile: Optional[str] = None


class ContactRequest(BaseModel):
    name: str
    company: Optional[str] = None
    email: str
    message: str


class NewsPublic(BaseModel):
    id: int
    title: str
    url: str
