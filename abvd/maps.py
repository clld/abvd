from clld.web.maps import ParameterMap, Map, Layer, Legend
from clld.web.util.htmllib import HTML, literal
from clldutils.misc import data_url
from clldutils.svg import icon
from clld_cognacy_plugin.maps import CognatesetMap


class CogsetMap(CognatesetMap):
    def get_options(self):
        return {'max_zoom': 15}


class LanguagesMap(Map):
    def get_options(self):
        return {'max_zoom': 15}

    def get_legends(self):
        def val(label, ico):
            return HTML.label(
                HTML.img(width=18, src=data_url(icon(ico))),
                literal('&nbsp;'),
                label,
                style='margin-left: 1em; margin-right: 1em;')

        yield Legend(
            self,
            'values',
            [
                val('Oceanic languages', 'cffffff'),
                val('other Austronesian languages', 'tffffff')],
            label='Legend')



def includeme(config):
    pass
