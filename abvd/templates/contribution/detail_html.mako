<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>

<%def name="sidebar()">
    <div class="well well-small">
        <dl>
            <dt>Author:</dt>
            <dd>${ctx.description}</dd>
            <dt>Typed by:</dt>
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
