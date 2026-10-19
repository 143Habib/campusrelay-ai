"""Lightweight delivery and UI contract checks; no external browser is required."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_new_frontend_assets_are_served(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'CampusRelay | Campus Service Desk' in response.text
    for name in ('styles.css', 'app.js'):
        asset = client.get('/static/' + name)
        assert asset.status_code == 200
        assert len(asset.content) > 1000
        assert asset.headers['x-content-type-options'] == 'nosniff'


def test_ui_has_authentication_and_workflow_hooks():
    js = (ROOT / 'static' / 'app.js').read_text(encoding='utf-8')
    for required in (
        'data-auth-tab="login"', 'data-auth-tab="register"',
        "data-action=\"toggle-password\"", 'data-nav="tickets"',
        'data-action="new"', 'data-action="close-menu"',
        'data-action="high-priority"', 'ticketLoadSequence',
        'aria-current="page"', 'aria-modal="true"',
    ):
        assert required in js, f"Missing frontend interaction hook: {required}"


def test_responsive_and_motion_accessibility_rules():
    css = (ROOT / 'static' / 'styles.css').read_text(encoding='utf-8')
    for required in (
        '@media (max-width: 1230px)', '@media (max-width: 1040px)',
        '@media (max-width: 800px)', '@media (max-width: 590px)',
        '@media (prefers-reduced-motion: reduce)', ':focus-visible',
        '.mobile-backdrop', '.modal', '.table-wrap', '.password-toggle',
    ):
        assert required in css, f"Missing UI accessibility/responsive styling: {required}"


def test_no_external_frontend_dependency_or_inline_script():
    html = (ROOT / 'static' / 'index.html').read_text(encoding='utf-8')
    assert 'https://' not in html and 'http://' not in html
    assert '<script defer src="/static/app.js"></script>' in html
    assert '<script>' not in html
    js = (ROOT / 'static' / 'app.js').read_text(encoding='utf-8')
    assert 'https://fonts.googleapis' not in js
    assert 'cdn.jsdelivr' not in js


def test_v3_theme_and_motion_contract():
    css = (ROOT / 'static' / 'styles.css').read_text(encoding='utf-8')
    for required in (
        'V3 • Atmosphere', '.sidebar::after', '.metric-card::before',
        '@keyframes ui-enter', '@keyframes modal-enter',
        '@keyframes board-drift', '@media (prefers-reduced-motion:reduce)',
        'animation:none !important', '.overview-callout::after',
    ):
        assert required in css, f'Missing V3 visual or motion rule: {required}'
    assert 'https://fonts' not in css
