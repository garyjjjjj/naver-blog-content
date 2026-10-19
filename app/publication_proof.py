"""Independent validation of browser observations; never publishes or retries."""
import time
import unicodedata
from urllib.parse import urlparse, parse_qs


class UnconfirmedPublication(ValueError):
    pass


def naver_identity(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.netloc != 'blog.naver.com' or parsed.fragment:
        raise UnconfirmedPublication('대상 네이버 게시글 주소가 아닙니다.')
    parts = parsed.path.strip('/').split('/')
    if len(parts) == 2 and parts[1].isascii() and parts[1].isdigit() and not parsed.query:
        return parts[0], parts[1]
    if parsed.path == '/PostView.naver':
        query = parse_qs(parsed.query)
        blogs, numbers = query.get('blogId', []), query.get('logNo', [])
        if len(blogs) == len(numbers) == 1 and numbers[0].isascii() and numbers[0].isdigit():
            return blogs[0], numbers[0]
    raise UnconfirmedPublication('게시글 번호를 확인할 수 없습니다.')


def validate_publication(post, evidence, *, blog_id, category_id, source_commit, previous_url=''):
    """Evidence must come from a fresh viewer read, not the publish button response.

    The browser adapter remains responsible for observing body/image order; this
    function rejects missing/contradictory evidence instead of inferring success.
    """
    def require(condition, message):
        if not condition:
            raise UnconfirmedPublication(message)
    blog, number = naver_identity(evidence.get('url', ''))
    require(blog == blog_id, '다른 블로그의 발행 결과입니다.')
    if previous_url:
        require(naver_identity(previous_url) == (blog, number), '수정본이 기존 게시글 번호와 다릅니다.')
    require(evidence.get('editor_open') is False, '편집기 종료를 확인하지 못했습니다.')
    require(evidence.get('viewer_reloaded') is True, '게시글 화면을 새로 읽은 증거가 필요합니다.')
    require(evidence.get('body_verified') is True and evidence.get('image_order_verified') is True,
            '본문과 이미지 순서의 실제 대조가 필요합니다.')
    require(unicodedata.normalize('NFC', evidence.get('title', '')) == unicodedata.normalize('NFC', post.meta['title']),
            '게시글 제목이 원고와 다릅니다.')
    require(type(evidence.get('category_id')) is int and evidence['category_id'] == category_id, '게시글 카테고리가 다릅니다.')
    require(evidence.get('visibility') == 'public', '전체공개 결과를 확인하지 못했습니다.')
    require(type(evidence.get('image_count')) is int and evidence['image_count'] == len(post.images), '게시된 이미지 수가 다릅니다.')
    require(evidence.get('post_id') == post.meta['post_id'] and type(evidence.get('revision')) is int
            and evidence['revision'] == post.meta['revision'], '다른 글 또는 버전의 결과입니다.')
    require(evidence.get('fingerprint') == post.fingerprint and evidence.get('source_commit') == source_commit,
            '원고 내용 또는 GitHub 커밋이 다릅니다.')
    checked = evidence.get('checked_at')
    require(type(checked) in (int, float) and 0 <= time.time() - checked <= 300, '발행 확인 시각이 없거나 오래됐습니다.')
    return f'https://blog.naver.com/{blog}/{number}'
