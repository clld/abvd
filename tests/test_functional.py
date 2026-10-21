import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ('get_html', '/'),
        ('get_html', '/legal'),
        ('get_html', '/download'),
        ('get_html', '/austronesian/language.php'),
    ])
def test_pages(app, method, path):
    getattr(app, method)(path)
