<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>


<h2>Entries for ${h.link(request, ctx.parameter)} in ${h.link(request, ctx.contribution)}</h2>

% for i, value in enumerate(ctx.values):
<dl class="dl-horizontal">
    <dt>Form:</dt>
    <dd>${value}</dd>
    % if value.loan != 'false':
    <dt>Loan:</dt>
    <dd>${value.loan}</dd>
    % endif
    % if value.cognates:
    <dt>Cognatesets:</dt>
    % for cog in value.cognates:
    <dd>
        ${h.link(req, cog.cognateset)}
        % if cog.doubt:
        ?
        % endif
    </dd>
    % endfor
    % endif
    % if value.comment:
    <dt>Annotation:</dt>
    <dd>${value.comment}</dd>
    % endif
</dl>
% endfor
<%def name="sidebar()">
<div class="well well-small">
<dl>
    <dt class="language">${_('Language')}:</dt>
    <dd class="language">${h.link(request, ctx.language)}</dd>
    <dt class="parameter">Author/Sources:</dt>
    % if ctx.description:
    <dd>${ctx.description}</dd>
    % endif
    % for ref in ctx.references:
    <dd>${h.link(req, ref.source)}</dd>
    % endfor
</dl>
</div>
</%def>
