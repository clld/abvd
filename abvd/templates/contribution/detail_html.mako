<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
    <div class="well well-small">
        <dl>
            <dt>Language:</dt>
            <dd>${h.link(req, ctx.language)}</dd>
             % if ctx.language.family:
            <dt>Family:</dt>
            <dd>${ctx.language.family}</dd>
            % endif
            <dt>Author/Sources:</dt>
            % if ctx.description:
            <dd>${ctx.description}</dd>
            % endif
            % for ref in ctx.references:
            <dd>${h.link(req, ref.source)}</dd>
            % endfor
            % if ctx.notes:
            <dt>Notes:</dt>
            <dd>${ctx.notes|n}</dd>
            % endif
            <dt>Statistics:</dt>
            <dd>
                <table class="table table-condensed table-nonfluid">
                    <tr><th>Total Data:</th><td>&nbsp;</td><td class="right">${ctx.count_words}</td></tr>
                    <tr><th>Number of Retentions:</th><td>${h.link(req, pmp, label='Proto Malayo-Polynesian')}:</td><td class="right">${pmp_retentions}</td></tr>
                    <tr><th>&nbsp;</th><td>${h.link(req, poc, label='Proto Oceanic')}:</td><td class="right">${poc_retentions}</td></tr>
                    <tr><th>Number of Loans:</th><td>&nbsp;</td><td class="right">${ctx.count_loans}</td></tr>
                </table>
            </dd>
            % if ctx.problems:
            <dt>Problems:</dt>
            <dd>${ctx.problems|n}</dd>
            % endif
            <dt>Contributed by:</dt>
            <dd>
                <ul class="unstyled inline">
                    % for ca in ctx.contributor_assocs:
                        % if 'typedby' in ca.jsondata['type']:
                            ${h.link(req, ca.contributor)}
                        % endif
                    % endfor
                </ul>
            </dd>
            <dt>Checked by:</dt>
            <dd>
                <ul class="unstyled inline">
                    % for ca in ctx.contributor_assocs:
                        % if 'checkedby' in ca.jsondata['type']:
                            ${h.link(req, ca.contributor)}
                        % endif
                    % endfor
                </ul>
            </dd>
        </dl>
    </div>
</%def>

<h2>${_('Contribution')} ${ctx.name}</h2>

<% dt = request.get_datatable('values', h.models.Value, contribution=ctx) %>
% if dt:
    <div>
        ${dt.render()}
    </div>
% endif
