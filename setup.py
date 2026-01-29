from setuptools import setup, find_packages


setup(
    name='abvd',
    version='0.0',
    description='abvd',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='DLCE EVA Dev',
    author_email='dlce.rdm@eva.mpg.de',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clld>=9.2.1',
        'clldmpg>=4.2',
        'clld-cognacy-plugin',
        'sqlalchemy',
        'waitress',
        'setuptools<81',
    ],
    extras_require={
        'dev': [
            'flake8',
            'tox',
        ],
        'test': [
            'psycopg2',
            'mock',
            'pytest>=3.6',
            'pytest-clld>=0.4',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    test_suite="abvd",
    entry_points={
        'console_scripts': [
            'abvd-app=abvd.__main__:main',
        ],
        'paste.app_factory': [
            'main = abvd:main',
        ],
    },
)
