<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "cognatesets" %>
<%block name="title">${_('Cognateset')} ${ctx.name}</%block>

<h2>${_('Cognateset')} ${ctx.id}</h2>

% if ctx.description:
<p>${ctx.description}</p>
% endif

% if map_ or request.map:
${(map_ or request.map).render()}
% endif

<table class="table">
    <tbody>
    % for co in ctx.cognates:
    <tr>
        <td>${h.link(request, co.counterpart.valueset.language)}</td>
        <td>${h.link(request, co.counterpart.valueset.contribution)}</td>
        <td>${h.link(request, co.counterpart)}</td>
    </tr>
    % endfor
    </tbody>
</table>
