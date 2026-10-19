"""Dedicated login; never reads the user's normal browser profile."""
import argparse
import ctypes
import json
import os
import time
from pathlib import Path
from ctypes import wintypes


class Blob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def crypt(data, decrypt=False):
    if os.name != "nt":
        raise RuntimeError("Windows DPAPI is required")
    buf = ctypes.create_string_buffer(data)
    src = Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
    dst = Blob()
    fn = ctypes.windll.crypt32.CryptUnprotectData if decrypt else ctypes.windll.crypt32.CryptProtectData
    # LOCAL_MACHINE allows the protected boot task to reuse this dedicated login.
    ok = fn(ctypes.byref(src), None, None, None, None, 0 if decrypt else 4, ctypes.byref(dst))
    if not ok:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(dst.pbData, dst.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(dst.pbData)


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_bytes(crypt(json.dumps(state).encode()))
    temp.replace(path)


def load_state(path):
    return json.loads(crypt(Path(path).read_bytes(), decrypt=True))


def launch_browser(playwright, *, headless):
    # Use the installed Chrome with a separate temporary context. Some Windows
    # systems cannot start bundled Chromium due to its side-by-side dependencies.
    roots=[os.environ.get('PROGRAMFILES',''),os.environ.get('PROGRAMFILES(X86)',''),os.environ.get('LOCALAPPDATA','')]
    for root in roots:
        if root and (Path(root)/'Google/Chrome/Application/chrome.exe').is_file():
            return playwright.chromium.launch(channel='chrome',headless=headless)
    return playwright.chromium.launch(headless=headless)


def login(state_dir, blog_id):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = launch_browser(p,headless=False)
        context = browser.new_context(locale='ko-KR')
        page = context.new_page()
        page.goto(f'https://blog.naver.com/{blog_id}/postwrite',wait_until='domcontentloaded',timeout=60000)
        status=Path(state_dir)/'login-status.json'
        status.write_text(json.dumps({'state':'waiting','message':'열린 전용 Chrome에서 네이버 로그인 후 글쓰기 화면까지 이동하세요.','at':time.time()},ensure_ascii=False),'utf8')
        print('전용 브라우저에서 네이버 로그인 후 글쓰기 화면까지 이동하세요.', flush=True)
        deadline = time.time() + 900
        while time.time() < deadline:
            try:
                for frame in page.frames:
                    if frame.locator('.se-documentTitle').count() and frame.get_by_role('button', name='발행', exact=True).count():
                        save_state(Path(state_dir) / 'naver-session.dpapi', context.storage_state())
                        print('전용 네이버 로그인 상태를 암호화하여 저장했습니다.', flush=True)
                        browser.close()
                        return
                time.sleep(1)
            except Exception:
                if not browser.is_connected():
                    raise RuntimeError('로그인이 완료되기 전에 브라우저가 닫혔습니다.')
        browser.close()
        raise RuntimeError('15분 내 로그인이 완료되지 않았습니다.')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--state-dir', required=True)
    ap.add_argument('--blog-id', default='3700708')
    args = ap.parse_args()
    login(args.state_dir, args.blog_id)
