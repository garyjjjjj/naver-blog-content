import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse
import yaml
from markdown_it import MarkdownIt


class InvalidPost(ValueError):
    pass


@dataclass
class Post:
    path: str
    meta: dict
    body: str
    images: dict
    fingerprint: str


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local_image(path):
    decoded = unquote(path)
    p = PurePosixPath(decoded)
    if p.is_absolute() or '\\' in decoded or '..' in p.parts or not p.parts or p.parts[0] != 'images':
        raise InvalidPost('이미지는 같은 글 폴더의 images/ 상대경로여야 합니다.')
    if p.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        raise InvalidPost('지원 이미지 형식: JPG, PNG, WebP')
    return str(p)


def parse_post(path, source, assets, blog_id):
    match = re.fullmatch(r'---\s*\n(.*?)\n---\s*\n(.*)', source, re.S)
    if not match:
        raise InvalidPost('YAML 발행 정보가 필요합니다.')
    meta = yaml.safe_load(match.group(1))
    if not isinstance(meta, dict):
        raise InvalidPost('잘못된 발행 정보')
    if meta.get('status') != 'ready':
        return None
    for field in ('post_id', 'title', 'muse_account'):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise InvalidPost(f'{field}가 필요합니다.')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', meta['post_id']):
        raise InvalidPost('글ID는 영문·숫자·하이픈·밑줄로 지정하세요.')
    if type(meta.get('revision')) is not int or meta['revision'] < 1:
        raise InvalidPost('revision은 1 이상의 정수여야 합니다.')
    if meta.get('blog_url', '').rstrip('/') != f'https://blog.naver.com/{blog_id}':
        raise InvalidPost('허용된 발행 대상 블로그와 다릅니다.')
    if meta.get('action') != 'publish' or meta.get('visibility') != 'public':
        raise InvalidPost('무인 발행은 action: publish, visibility: public을 사용하세요.')
    if meta.get('scheduled_at'):
        raise InvalidPost('현재 무인 버전은 즉시 발행만 지원합니다. 예약값을 지우세요.')
    tags = meta.get('tags', [])
    if not isinstance(tags, list) or len(tags) > 30 or any(not isinstance(x, str) or not x or len(x) > 50 for x in tags):
        raise InvalidPost('태그는 최대 30개의 문자열 목록이어야 합니다.')
    body_part = match.group(2)
    if body_part.count('<!-- 본문 시작 -->') != 1 or body_part.count('<!-- 본문 끝 -->') != 1:
        raise InvalidPost('본문 시작/끝 표시를 각각 한 번 넣으세요.')
    body = body_part.split('<!-- 본문 시작 -->')[1].split('<!-- 본문 끝 -->')[0].strip()
    if not re.sub(r'<!--.*?-->', '', body, flags=re.S).strip():
        raise InvalidPost('완성된 본문이 없습니다.')
    # Raw HTML is not executed. A future renderer can add a reviewed allowlist.
    if re.search(r'<\s*/?\s*(script|iframe|style|img|video|audio)\b', body, re.I):
        raise InvalidPost('실행 가능한 HTML·외부 미디어는 지원하지 않습니다.')
    md = MarkdownIt('commonmark', {'html': False}).enable('table')
    image_paths = []
    for token in md.parse(body):
        for child in token.children or []:
            if child.type == 'image':
                image_paths.append(local_image(child.attrGet('src') or ''))
            if child.type == 'link_open':
                if urlparse(child.attrGet('href') or '').scheme not in ('http', 'https', 'mailto'):
                    raise InvalidPost('본문 링크는 http/https/mailto만 허용합니다.')
    manifest = meta.get('assets', [])
    if not isinstance(manifest, list):
        raise InvalidPost('assets는 경로와 sha256을 가진 목록이어야 합니다.')
    manifest_map = {}
    for entry in manifest:
        if not isinstance(entry, dict):
            raise InvalidPost('잘못된 assets 항목')
        key = local_image(entry.get('path', ''))
        checksum = entry.get('sha256', '')
        if key in manifest_map or not re.fullmatch('[0-9a-f]{64}', checksum):
            raise InvalidPost('이미지 경로 중복 또는 SHA256 오류')
        manifest_map[key] = checksum
    if set(image_paths) != set(manifest_map):
        raise InvalidPost('본문 이미지와 assets 목록이 일치하지 않습니다.')
    cover = meta.get('cover_image', '')
    if cover and local_image(cover) not in image_paths:
        raise InvalidPost('대표 이미지는 본문 이미지 중 하나여야 합니다.')
    for key, checksum in manifest_map.items():
        if key not in assets or digest(assets[key]) != checksum:
            raise InvalidPost(f'이미지 누락 또는 해시 불일치: {key}')
        if len(assets[key]) > 20 * 1024 * 1024:
            raise InvalidPost('이미지는 파일당 20MB 이하로 준비하세요.')
        from PIL import Image
        import io
        try:
            with Image.open(io.BytesIO(assets[key])) as image:
                image.verify()
        except Exception as exc:
            raise InvalidPost(f'이미지 파일 검증 실패: {key}') from exc
    content_meta = {k: meta.get(k) for k in ('post_id', 'title', 'blog_url', 'category', 'tags', 'action', 'visibility', 'cover_image')}
    fingerprint = digest(json.dumps([content_meta, body, manifest_map], ensure_ascii=False, sort_keys=True).encode())
    return Post(path, meta, body, assets, fingerprint)
