<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

<h2>${_('Language')} ${ctx.name}</h2>

<h4>Wordlists</h4>
<ul>
    % for wordlist in ctx.wordlists:
        <li>${h.link(req, wordlist)}</li>
    % endfor
</ul>

<%def name="sidebar()">
    ${util.language_meta()}
</%def>
