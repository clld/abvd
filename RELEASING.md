# Releasing the ABVD clld app

```shell
git clone https://github.com/clld/abvd
git clone https://github.com/lexibank/abvd abvd-cldf
cd abvd
pip install -e .[test]
```

```shell
clld initdb development.ini --cldf ../abvd-cldf/cldf/cldf-metadata.json --glottolog ../../glottolog/glottolog
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
pg_dump -xO abvd > abvd.sql
zip abvd.sql.zip abvd.sql
rm abvd.sql
```

