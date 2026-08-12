<%inherit file="../snippet.mako"/>
<%namespace name="util" file="../util.mako"/>

${ctx.notes|n}

% if ctx.references:
<strong>Sources:</strong>

<dl>
% for ref in ctx.references:
<dt>${h.link(req, ref.source)}</dt>
    <dd>${ref.source.bibtex().text()}</dd>
% endfor
</dl>
% endif