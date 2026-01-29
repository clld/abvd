<%inherit file="../home_comp.mako"/>

<%def name="sidebar()">
    <div class="well">
        <h3>Cite</h3>
        <p>
           To cite this database, please reference the following paper:
        </p>
        <blockquote>
            Greenhill, S.J., Blust. R, & Gray, R.D. (2008). The Austronesian Basic Vocabulary Database: From Bioinformatics to Lexomics. Evolutionary Bioinformatics, 4:271-283.
        </blockquote>
    </div>
</%def>

<h2><span style="color: #07b;">Austronesian</span><br>
    <span style="font-size: smaller">Basic Vocabulary Database</span></h2>

<blockquote>
    "The poets made all the words, and therefore language is the archives of history" -Ralph Waldo Emerson, Essays: "The Poet".
</blockquote>

<p class="lead">
    <strong>Kia Ora!</strong>
</p>

<div class="alert-info alert">
    <div style="width: 100%; text-align: center;">
        Random Word: ${h.link(req, word)} ("${h.link(req, word.valueset.parameter)}" in ${h.link(req, word.valueset.language)})
    </div>
</div>

<p>
    This database contains ${'{:,}'.format(vcount)} lexical items from
    <a href="${req.route_url('languages')}">${'{:,}'.format(lcount)}
    languages</a> spoken throughout the Pacific region. Most of these
    languages belong to the
    <a href="https://glottolog.org/resource/languoid/id/aust1307"><b>Austronesian</b></a>
    language family, which is the largest family in the world containing around
    1,200 languages.
</p>

<p> Each language in our database has around 210 words associated with it.
    These words correspond to basic items of vocabulary, such as simple verbs
    like <a href="${req.route_url('parameter', id='5_towalk')}">'to walk'</a>, or
    <a href="${req.route_url('parameter', id='101_tofly')}">'to fly'</a>, the names of body
    parts like <a href="${req.route_url('parameter', id='101_tofly')}">hand</a> or
    <a href="${req.route_url('parameter', id='30_mouth')}">mouth</a>, colors like
    <a href="${req.route_url('parameter', id='149_red')}">red</a>,
     numbers (<a href="${req.route_url('parameter', id='197_one')}">1</a>,
    <a href="${req.route_url('parameter', id='198_two')}">2</a>,
    <a href="${req.route_url('parameter', id='199_three')}">3</a>,
    <a href="${req.route_url('parameter', id='200_four')}">4</a>) and kinship terms such as
    <a href="${req.route_url('parameter', id='59_mother')}">Mother</a>,
    <a href="${req.route_url('parameter', id='60_father')}">Father</a> and
    <a href="${req.route_url('parameter', id='53_personhumanbeing')}">Person</a>.
    The full list is <a href="${req.route_url('parameters')}">here</a>.
</p>
