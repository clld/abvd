# Releasing the ABVD clld app

```shell
git clone https://github.com/clld/abvd
git clone --branch v0.3 --depth 1 https://github.com/lexibank/abvd abvd-cldf
git clone --branch v5.3 --depth 1 https://github.com/glottolog/glottolog
cd abvd
pip install -e .[test]
```

```shell
clld initdb development.ini --cldf ../abvd-cldf/cldf/cldf-metadata.json --glottolog ../glottolog/
```

```shell
pytest
```

Store the tested requirements:
```shell
pip freeze > requirements.txt
```

Store a db dump:
```shell
pg_dump -xO --compress gzip:9 abvd > abvd.sql.gz
```

