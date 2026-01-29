from pyramid.config import Configurator
from clld import interfaces
from clld.web.icon import MapMarker
from clldutils import svg

# we must make sure custom models are known at database initialization!
from abvd import models


_ = lambda s: s
_('Parameter')
_('Parameters')
_('Contribution')
_('Contributions')
_('Contributor')
_('Contributors')


class ABVDMapMarker(MapMarker):
    def __call__(self, ctx, req):
        icon = None

        if interfaces.ILanguage.providedBy(ctx):
            icon = ctx.jsondata['icon']

        if interfaces.IContribution.providedBy(ctx):
            return self.__call__(ctx.language, req)

        if interfaces.IValueSet.providedBy(ctx):
            icon = ctx.language.jsondata['icon']

        if interfaces.IValue.providedBy(ctx):
            return self.__call__(ctx.valueset, req)

        if icon:
            return svg.data_url(svg.icon(icon))

        return super(ABVDMapMarker, self).__call__(ctx, req)  # pragma: no cover


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings['route_patterns'] = {
        'languages': r'/austronesian/language.php',
        'contribution': r'/austronesian/language.php/{id:[^/\.]+}',
        'parameters': r'/austronesian/word.php',
        'parameter': r'/austronesian/word.php/{id:[^/\.]+}',
    }
    config = Configurator(settings=settings)
    config.include('clldmpg')
    config.include('clld_cognacy_plugin')
    config.registry.registerUtility(ABVDMapMarker(), interfaces.IMapMarker)
    return config.make_wsgi_app()
