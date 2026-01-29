from clld.web.maps import ParameterMap, Map, Layer, Legend
from clld.web.util.htmllib import HTML, literal

#
# FIXME: add family legend to languages map!
# allow deeper zoom on language map
#


class LanguagesMap(Map):
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